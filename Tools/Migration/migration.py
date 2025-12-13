"""
Word Document to JSON Converter
Extracts text from a Microsoft Word file and converts it to a structured JSON format.
"""

import sys
import json
import random
import os
import re
import subprocess
import hashlib
from pathlib import Path
from docx import Document
from docx.text.paragraph import Paragraph

# Optional import for SmartArt/Drawing Canvas detection
try:
    import win32com.client
    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False



def generate_id():
    """Generate an 8-character random alphanumeric string."""
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(chars) for _ in range(8))


def create_paragraph_wrapper(content_list, content_type_name):
    """
    Create a paragraph wrapper if content contains mixed text and equations.
    
    Args:
        content_list: List of tuples (content_type, content_value) from extract_paragraph_content_in_order
        content_type_name: The base content type (e.g., 'body', 'bullet1', 'highlight-red')
    
    Returns:
        Single content item (paragraph wrapper if mixed, or single item if not)
    """
    if not content_list:
        return None
    
    # Check if we have mixed content (both text and equations)
    has_text = any(ct == 'text' for ct, _ in content_list)
    has_equation = any(ct == 'equation' for ct, _ in content_list)
    
    # If only one type, return as single item
    if not (has_text and has_equation):
        # Single text item
        if len(content_list) == 1 and content_list[0][0] == 'text':
            return {
                "id": generate_id(),
                "type": content_type_name,
                "text": content_list[0][1]
            }
        # Single equation item
        elif len(content_list) == 1 and content_list[0][0] == 'equation':
            return {
                "id": generate_id(),
                "type": "equation",
                "equation": content_list[0][1]
            }
    
    # Mixed content - create paragraph wrapper
    items = []
    for content_type, content_value in content_list:
        if content_type == 'text':
            items.append({
                "id": generate_id(),
                "type": "body",
                "text": content_value
            })
        elif content_type == 'equation':
            items.append({
                "id": generate_id(),
                "type": "equation",
                "equation": content_value
            })
    
    return {
        "id": generate_id(),
        "type": "paragraph",
        "items": items
    }



def sanitize_filename(label):
    """
    Sanitize label to create a valid filename.
    - Replace spaces with hyphens
    - Remove special characters like ., ?, !, etc.
    """
    # Replace spaces with hyphens
    filename = label.replace(' ', '-')
    # Remove special characters (keep only alphanumeric, hyphens, and underscores)
    filename = re.sub(r'[^a-zA-Z0-9\-_]', '', filename)
    return filename


def is_bold(run):
    """Check if a run has bold formatting."""
    return run.bold is True


def extract_text_with_formatting(paragraph):
    """Extract text from paragraph, preserving bold formatting with markdown."""
    text_parts = []
    for run in paragraph.runs:
        text = run.text
        if text:
            if is_bold(run):
                text_parts.append(f"**{text}**")
            else:
                text_parts.append(text)
    return ''.join(text_parts)


def extract_paragraph_content_in_order(paragraph):
    """
    Extract paragraph content (text and equations) in document order.
    
    Returns:
        List of tuples: (content_type, content_value)
        where content_type is 'text' or 'equation'
    """
    m_ns = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
    w_ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    
    content_items = []
    para_xml = paragraph._element
    
    # Track current text buffer
    text_buffer = []
    
    # Iterate through all child elements of the paragraph
    for child in para_xml:
        tag = child.tag
        
        # Check if this is a run (text content)
        if tag == f'{w_ns}r':
            # Check if this run contains an equation
            omath = child.find(f'.//{m_ns}oMath')
            if omath is not None:
                # Flush text buffer before adding equation
                if text_buffer:
                    text_content = ''.join(text_buffer).strip()
                    if text_content:
                        content_items.append(('text', text_content))
                    text_buffer = []
                
                # Extract equation
                latex = omml_to_latex(omath)
                if latex:
                    content_items.append(('equation', latex))
            else:
                # Regular text run - extract text with formatting
                run_text = ''
                t_elem = child.find(f'.//{w_ns}t')
                if t_elem is not None and t_elem.text:
                    # Check if bold
                    rPr = child.find(f'{w_ns}rPr')
                    is_bold_run = False
                    if rPr is not None:
                        b_elem = rPr.find(f'{w_ns}b')
                        if b_elem is not None:
                            # Check if bold is explicitly turned off
                            val = b_elem.get(f'{w_ns}val', 'true')
                            is_bold_run = val.lower() != 'false'
                    
                    if is_bold_run:
                        run_text = f"**{t_elem.text}**"
                    else:
                        run_text = t_elem.text
                    
                    text_buffer.append(run_text)
        
        # Check if this is an inline oMath (direct child of paragraph)
        elif tag == f'{m_ns}oMath':
            # Flush text buffer before adding equation
            if text_buffer:
                text_content = ''.join(text_buffer).strip()
                if text_content:
                    content_items.append(('text', text_content))
                text_buffer = []
            
            # Extract inline equation
            latex = omml_to_latex(child)
            if latex:
                content_items.append(('equation', latex))
        
        # Check if this is an oMathPara (display equation)
        elif tag == f'{m_ns}oMathPara':
            # Flush text buffer before adding equation
            if text_buffer:
                text_content = ''.join(text_buffer).strip()
                if text_content:
                    content_items.append(('text', text_content))
                text_buffer = []
            
            # Extract display equation
            omaths = child.findall(f'{m_ns}oMath')
            if omaths:
                latex_lines = []
                for omath in omaths:
                    latex = omml_to_latex(omath)
                    if latex:
                        latex_lines.append(latex)
                
                if latex_lines:
                    # If multiple equations, combine them with aligned environment
                    if len(latex_lines) > 1:
                        aligned_lines = []
                        for i, line in enumerate(latex_lines):
                            if i == 0:
                                # First line: add & before the first = sign
                                if '=' in line:
                                    line = line.replace('=', '&=', 1)
                                aligned_lines.append(line)
                            else:
                                # Subsequent lines: add & at the start if line starts with =
                                if line.strip().startswith('='):
                                    aligned_lines.append('&' + line.strip())
                                else:
                                    # If line doesn't start with =, add & before first =
                                    if '=' in line:
                                        line = line.replace('=', '&=', 1)
                                    aligned_lines.append(line)
                        
                        combined_latex = '\\begin{aligned}\n' + ' \\\\\n'.join(aligned_lines) + '\n\\end{aligned}'
                        content_items.append(('equation', combined_latex))
                    else:
                        content_items.append(('equation', latex_lines[0]))
    
    # Flush remaining text buffer
    if text_buffer:
        text_content = ''.join(text_buffer).strip()
        if text_content:
            content_items.append(('text', text_content))
    
    return content_items



def get_paragraph_style(paragraph):
    """Get the style name of a paragraph."""
    if paragraph.style and paragraph.style.name:
        return paragraph.style.name
    return None


def omml_to_latex(omml_element):
    """
    Convert OMML (Office Math Markup Language) to LaTeX.
    
    Args:
        omml_element: XML element containing OMML math
    
    Returns:
        LaTeX string representation
    """
    # OMML namespace
    m_ns = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
    
    def process_element(elem):
        """Recursively process OMML elements."""
        tag = elem.tag.replace(m_ns, '')
        
        # Fraction
        if tag == 'f':
            num = elem.find(f'{m_ns}num')
            den = elem.find(f'{m_ns}den')
            num_latex = process_element(num) if num is not None else ''
            den_latex = process_element(den) if den is not None else ''
            return f'\\frac{{{num_latex}}}{{{den_latex}}}'
        
        # Superscript
        elif tag == 'sSup':
            base = elem.find(f'{m_ns}e')
            sup = elem.find(f'{m_ns}sup')
            base_latex = process_element(base) if base is not None else ''
            sup_latex = process_element(sup) if sup is not None else ''
            return f'{base_latex}^{{{sup_latex}}}'
        
        # Subscript
        elif tag == 'sSub':
            base = elem.find(f'{m_ns}e')
            sub = elem.find(f'{m_ns}sub')
            base_latex = process_element(base) if base is not None else ''
            
            # Check if subscript contains an equation array (multi-line subscript)
            if sub is not None and sub.find(f'{m_ns}eqArr') is not None:
                # Multi-line subscript - use substack for vertical stacking
                eqArr = sub.find(f'{m_ns}eqArr')
                rows = []
                for e_elem in eqArr.findall(f'{m_ns}e'):
                    row_content = process_element(e_elem)
                    if row_content:
                        rows.append(row_content)
                
                if rows:
                    # Use double backslash in Python string to get single backslash in output
                    sub_latex = '\\substack{' + ' \\\\ '.join(rows) + '}'
                else:
                    sub_latex = process_element(sub) if sub is not None else ''
            else:
                sub_latex = process_element(sub) if sub is not None else ''
            
            return f'{base_latex}_{{{sub_latex}}}'
        
        # Subscript-Superscript
        elif tag == 'sSubSup':
            base = elem.find(f'{m_ns}e')
            sub = elem.find(f'{m_ns}sub')
            sup = elem.find(f'{m_ns}sup')
            base_latex = process_element(base) if base is not None else ''
            sub_latex = process_element(sub) if sub is not None else ''
            sup_latex = process_element(sup) if sup is not None else ''
            return f'{base_latex}_{{{sub_latex}}}^{{{sup_latex}}}'
        
        # Radical (square root)
        elif tag == 'rad':
            deg = elem.find(f'{m_ns}deg')
            base = elem.find(f'{m_ns}e')
            base_latex = process_element(base) if base is not None else ''
            if deg is not None and deg.text and deg.text.strip():
                deg_latex = process_element(deg)
                return f'\\sqrt[{deg_latex}]{{{base_latex}}}'
            return f'\\sqrt{{{base_latex}}}'
        
        # Function (like lim, sin, cos, etc.)
        elif tag == 'func':
            # Get the function name
            fName = elem.find(f'{m_ns}fName')
            func_name = process_element(fName) if fName is not None else ''
            
            # Get the base expression (what comes after the function)
            e_elem = elem.find(f'{m_ns}e')
            base_latex = process_element(e_elem) if e_elem is not None else ''
            
            # Add backslash for LaTeX function names (lim, sin, cos, etc.)
            if func_name and not func_name.startswith('\\'):
                func_name = '\\' + func_name
            
            return f'{func_name}{base_latex}'
        
        # Equation Array (aligned equations)
        elif tag == 'eqArr':
            rows = []
            for e_elem in elem.findall(f'{m_ns}e'):
                row_content = process_element(e_elem)
                if row_content:
                    # Add alignment marker based on content
                    # Case 1: Row starts with = (common in multi-line equations like |A| = ... = ... = ...)
                    if row_content.strip().startswith('='):
                        row_content = '&' + row_content.strip()
                    # Case 2: Row contains = but doesn't start with it
                    elif '=' in row_content:
                        row_content = row_content.replace('=', '&=', 1)
                    # Case 3: No = sign - align at the start (for cases like limits with conditions)
                    else:
                        row_content = '&' + row_content
                    
                    rows.append(row_content)
            
            if rows:
                # Join rows with LaTeX line break
                aligned_content = ' \\\\\n'.join(rows)
                return f'\\begin{{aligned}}\n{aligned_content}\n\\end{{aligned}}'
            return ''
        
        # N-ary operators (summation, product, integral, etc.)
        elif tag == 'nary':
            # Get the operator character
            naryPr = elem.find(f'{m_ns}naryPr')
            operator = '\\sum'  # Default to summation
            chr_val = '∑'  # Default character
            
            if naryPr is not None:
                chr_elem = naryPr.find(f'{m_ns}chr')
                if chr_elem is not None:
                    chr_val = chr_elem.get(f'{m_ns}val', '∑')
                    # Map common n-ary operators to LaTeX
                    operator_map = {
                        '∑': '\\sum',
                        '∏': '\\prod',
                        '∫': '\\int',
                        '⋃': '\\bigcup',
                        '⋂': '\\bigcap',
                        '⨁': '\\bigoplus',
                        '⨂': '\\bigotimes'
                    }
                    operator = operator_map.get(chr_val, '\\sum')
            
            # Get subscript (lower limit)
            sub_elem = elem.find(f'{m_ns}sub')
            sub_latex = process_element(sub_elem) if sub_elem is not None else ''
            
            # Get superscript (upper limit)
            sup_elem = elem.find(f'{m_ns}sup')
            sup_latex = process_element(sup_elem) if sup_elem is not None else ''
            
            # HEURISTIC: Word sometimes stores integrals as summations
            # Detect if this is actually an integral by checking the limits
            if chr_val == '∑' and sub_elem is not None and sup_elem is not None:
                # Integrals typically have simple single-character limits (a, b, 0, 1, etc.)
                # Summations typically have expressions like i=1, n, etc.
                is_simple_lower = len(sub_latex) == 1 and sub_latex.isalnum()
                is_simple_upper = len(sup_latex) == 1 and sup_latex.isalnum()
                
                if is_simple_lower and is_simple_upper:
                    operator = '\\int'
            
            # Get the base expression (what comes after the operator)
            e_elem = elem.find(f'{m_ns}e')
            base_latex = process_element(e_elem) if e_elem is not None else ''
            
            # Build the LaTeX expression
            result = operator
            if sub_latex:
                result += f'_{{{sub_latex}}}'
            if sup_latex:
                result += f'^{{{sup_latex}}}'
            result += base_latex
            
            return result
        
        # Delimiter (parentheses, brackets, etc.)
        elif tag == 'd':
            e_elem = elem.find(f'{m_ns}e')
            content = process_element(e_elem) if e_elem is not None else ''
            # Try to get delimiter properties
            dPr = elem.find(f'{m_ns}dPr')
            if dPr is not None:
                begChr = dPr.find(f'{m_ns}begChr')
                endChr = dPr.find(f'{m_ns}endChr')
                begin = begChr.get(f'{m_ns}val', '(') if begChr is not None else '('
                end = endChr.get(f'{m_ns}val', ')') if endChr is not None else ')'
                return f'{begin}{content}{end}'
            return f'\\left({content}\\right)'
        
        # Text run
        elif tag == 'r':
            t_elem = elem.find(f'{m_ns}t')
            if t_elem is not None and t_elem.text:
                return t_elem.text
            return ''
        
        # Text element
        elif tag == 't':
            return elem.text if elem.text else ''
        
        # Container elements - process children
        elif tag in ['oMath', 'oMathPara', 'e', 'num', 'den', 'sup', 'sub', 'deg']:
            result = ''
            for child in elem:
                result += process_element(child)
            return result
        
        # Default: process children
        else:
            result = ''
            for child in elem:
                result += process_element(child)
            return result
    
    try:
        latex = process_element(omml_element)
        return latex.strip()
    except Exception as e:
        print(f"Warning: Error converting OMML to LaTeX: {e}")
        return ""


def extract_equations_from_run(run):
    """
    Extract equations from a paragraph run.
    
    Args:
        run: A run object from python-docx
    
    Returns:
        List of tuples (equation_latex, is_display) where is_display indicates if it's a display equation
    """
    equations = []
    m_ns = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
    
    try:
        # Look for math elements in the run's XML
        # oMathPara = display equation (block)
        # oMath = inline equation
        
        for math_para in run.element.findall(f'.//{m_ns}oMathPara'):
            # Display equation
            omath = math_para.find(f'{m_ns}oMath')
            if omath is not None:
                latex = omml_to_latex(omath)
                if latex:
                    # print(f"  [DEBUG] Found display equation: {latex[:50]}...")
                    equations.append((latex, True))  # True = display equation
        
        for omath in run.element.findall(f'.//{m_ns}oMath'):
            # Check if this oMath is not inside an oMathPara (to avoid duplicates)
            if omath.getparent().tag != f'{m_ns}oMathPara':
                latex = omml_to_latex(omath)
                if latex:
                    # print(f"  [DEBUG] Found inline equation: {latex[:50]}...")
                    equations.append((latex, False))  # False = inline equation
    
    except Exception as e:
        print(f"Warning: Error extracting equations: {e}")
        import traceback
        traceback.print_exc()
    
    return equations



def scan_for_smartart_and_canvas(file_path):
    """
    Scan a Word document for SmartArt, Drawing Canvas, Tables, and Cropped Images.
    Adds a review comment in the document for each detected object.
    
    Args:
        file_path: Path to the Word document
    
    Returns:
        List of dictionaries with object type and page number
    """
    if not WIN32COM_AVAILABLE:
        print("⚠ Object detection not available (win32com not installed)")
        return []
    
    objects_found = []
    word = None
    doc = None
    
    try:
        # Start Word application
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        
        # Open document
        abs_path = str(Path(file_path).resolve())
        doc = word.Documents.Open(abs_path)
        
        changes_made = False

        # Scan Shapes collection
        shape_count = 0
        for shape in doc.Shapes:
            shape_count += 1
            try:
                # Get the page number where this shape is located
                page_num = shape.Anchor.Information(3)  # wdActiveEndPageNumber = 3
                shape_type = shape.Type
                found_type = None
                
                # Type 15 is msoSmartArt
                if shape_type == 15:
                    found_type = 'SmartArt'
                # Type 16 is msoCanvas (old constant, rarely used)
                # Type 20 is msoDiagram/msoGroup (Drawing Canvas in modern Word)
                elif shape_type == 16 or shape_type == 20:
                    found_type = 'Drawing Canvas'
                # Type 13 is Picture - check if cropped
                elif shape_type == 13:
                    try:
                        if hasattr(shape.PictureFormat, 'CropLeft'):
                            left = shape.PictureFormat.CropLeft
                            top = shape.PictureFormat.CropTop
                            right = shape.PictureFormat.CropRight
                            bottom = shape.PictureFormat.CropBottom
                            
                            if left != 0 or top != 0 or right != 0 or bottom != 0:
                                found_type = 'Cropped Image'
                    except:
                        pass
                
                if found_type:
                    objects_found.append({
                        'type': found_type,
                        'page': page_num
                    })
                    # Add comment
                    try:
                        doc.Comments.Add(Range=shape.Anchor, Text=f"[Migration] {found_type} detected. Please review.")
                        changes_made = True
                    except Exception as comment_err:
                        print(f"  ⚠ Could not add comment for {found_type} on page {page_num}: {comment_err}")

            except Exception as e:
                # Some shapes might not have page info
                pass
        
        # Also scan InlineShapes collection (SmartArt can be inline)
        inline_count = 0
        for inline_shape in doc.InlineShapes:
            inline_count += 1
            try:
                # Get the page number
                page_num = inline_shape.Range.Information(3)  # wdActiveEndPageNumber = 3
                shape_type = inline_shape.Type
                found_type = None
                
                # Type 15 is wdInlineShapeSmartArt
                if shape_type == 15:
                    found_type = 'SmartArt'
                # Type 3 is Picture - check if cropped
                elif shape_type == 3:
                    try:
                        if hasattr(inline_shape.PictureFormat, 'CropLeft'):
                            left = inline_shape.PictureFormat.CropLeft
                            top = inline_shape.PictureFormat.CropTop
                            right = inline_shape.PictureFormat.CropRight
                            bottom = inline_shape.PictureFormat.CropBottom
                            
                            if left != 0 or top != 0 or right != 0 or bottom != 0:
                                found_type = 'Cropped Image'
                    except:
                        pass
                
                if found_type:
                    objects_found.append({
                        'type': found_type,
                        'page': page_num
                    })
                    # Add comment
                    try:
                        doc.Comments.Add(Range=inline_shape.Range, Text=f"[Migration] {found_type} detected. Please review.")
                        changes_made = True
                    except Exception as comment_err:
                        print(f"  ⚠ Could not add comment for {found_type} on page {page_num}: {comment_err}")

            except Exception as e:
                # Some inline shapes might not have page info
                pass
        
        # Scan for tables
        table_count = 0
        for table in doc.Tables:
            table_count += 1
            try:
                # Get the page number where this table is located
                page_num = table.Range.Information(3)  # wdActiveEndPageNumber = 3
                found_type = 'Table'
                
                objects_found.append({
                    'type': found_type,
                    'page': page_num
                })
                # Add comment
                try:
                    doc.Comments.Add(Range=table.Range, Text=f"[Migration] {found_type} detected. Please review.")
                    changes_made = True
                except Exception as comment_err:
                    print(f"  ⚠ Could not add comment for {found_type} on page {page_num}: {comment_err}")
                
            except Exception as e:
                # Some tables might not have page info
                pass
        
        # Debug output
        if shape_count == 0 and inline_count == 0 and table_count == 0:
            print("  (No shapes, inline shapes, or tables found in document)")
            
        if changes_made:
            doc.Save()
        
    except Exception as e:
        print(f"⚠ Error scanning document: {e}")
    
    finally:
        # Clean up
        if doc:
            doc.Close(False)
        if word:
            word.Quit()
    
    return objects_found


def process_word_document(file_path, standard, subject):
    """
    Process a Word document and convert it to the specified JSON schema.
    
    Args:
        file_path: Path to the Word document
        standard: The standard/grade number (e.g., "6")
        subject: The subject name (e.g., "science")
    
    Returns:
        Dictionary containing the structured data
    """
    doc = Document(file_path)
    
    # Create images directory in db/<standard>-<subject>/images
    subject_slug = subject.lower()
    images_dir = Path(f"../../db/{standard}-{subject_slug}/images")
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize the result structure
    result = {
        "topics": []
    }
    
    current_topic = None
    current_subtopic = None
    
    # Processing state flags
    processing_started = False
    processing_stopped = False
    
    # Process all paragraphs
    for paragraph in doc.paragraphs:
        style = get_paragraph_style(paragraph)
        text = paragraph.text.strip()
        

        
        # Check for start marker: <teach> with style "# Meta Data"
        if style == "# Meta Data" and text.lower() == "<teach>":
            processing_started = True
            continue  # Skip the marker itself
        
        # Check for stop markers: <revision> or <question> with style "# Meta Data"
        if style == "# Meta Data" and (text.lower() == "<revision>" or text.lower() == "<question>"):
            processing_stopped = True
            break  # Stop processing
        
        # Skip processing if we haven't started yet or if we've stopped
        if not processing_started or processing_stopped:
            continue
        
        # Process based on style
        if style == "# Sub Topic - 1":
            # Create a new topic
            current_topic = {
                "id": generate_id(),
                "title": text,
                "subTopics": []
            }
            result["topics"].append(current_topic)
            current_subtopic = None  # Reset subtopic when new topic starts
            
        elif style == "# Sub Topic - 2":
            # Create a new subtopic
            current_subtopic = {
                "id": generate_id(),
                "title": text,
                "content": []
            }
            
            # Add to current topic's subTopics if exists
            if current_topic is not None:
                current_topic["subTopics"].append(current_subtopic)
            else:
                # If no topic exists, create a temporary topic
                current_topic = {
                    "id": generate_id(),
                    "title": "Untitled Topic",
                    "subTopics": [current_subtopic]
                }
                result["topics"].append(current_topic)
                
        elif style == "# Bullet-1":
            # Extract content (text and equations) in document order
            content_list = extract_paragraph_content_in_order(paragraph)
            
            if current_subtopic is not None and content_list:
                if "content" not in current_subtopic:
                    current_subtopic["content"] = []
                
                # Use paragraph wrapper for mixed content
                content_item = create_paragraph_wrapper(content_list, "bullet1")
                if content_item:
                    current_subtopic["content"].append(content_item)
                
        elif style == "# Body":
            # Extract content (text and equations) in document order
            content_list = extract_paragraph_content_in_order(paragraph)
            
            if current_subtopic is not None and content_list:
                if "content" not in current_subtopic:
                    current_subtopic["content"] = []
                
                # Use paragraph wrapper for mixed content
                content_item = create_paragraph_wrapper(content_list, "body")
                if content_item:
                    current_subtopic["content"].append(content_item)
                
        elif style == "# Bullet-2":
            # Extract content (text and equations) in document order
            content_list = extract_paragraph_content_in_order(paragraph)
            
            if current_subtopic is not None and content_list:
                if "content" not in current_subtopic:
                    current_subtopic["content"] = []
                
                # Use paragraph wrapper for mixed content
                content_item = create_paragraph_wrapper(content_list, "bullet2")
                if content_item:
                    current_subtopic["content"].append(content_item)
        
        elif style == "# Sub Topic - 3":
            # Extract content (text and equations) in document order
            content_list = extract_paragraph_content_in_order(paragraph)
            
            if current_subtopic is not None and content_list:
                if "content" not in current_subtopic:
                    current_subtopic["content"] = []
                
                # Use paragraph wrapper for mixed content
                content_item = create_paragraph_wrapper(content_list, "sub-topic-3")
                if content_item:
                    current_subtopic["content"].append(content_item)
        
        elif style == "# Highlight Red":
            # Extract content (text and equations) in document order
            content_list = extract_paragraph_content_in_order(paragraph)
            
            if current_subtopic is not None and content_list:
                if "content" not in current_subtopic:
                    current_subtopic["content"] = []
                
                # Use paragraph wrapper for mixed content
                content_item = create_paragraph_wrapper(content_list, "highlight-red")
                if content_item:
                    current_subtopic["content"].append(content_item)
        
        elif style == "# Highlight Brown":
            # Extract content (text and equations) in document order
            content_list = extract_paragraph_content_in_order(paragraph)
            
            if current_subtopic is not None and content_list:
                if "content" not in current_subtopic:
                    current_subtopic["content"] = []
                
                # Use paragraph wrapper for mixed content
                content_item = create_paragraph_wrapper(content_list, "highlight-brown")
                if content_item:
                    current_subtopic["content"].append(content_item)
        
        elif style == "# Highlight Blue":
            # Extract content (text and equations) in document order
            content_list = extract_paragraph_content_in_order(paragraph)
            
            if current_subtopic is not None and content_list:
                if "content" not in current_subtopic:
                    current_subtopic["content"] = []
                
                # Use paragraph wrapper for mixed content
                content_item = create_paragraph_wrapper(content_list, "highlight-blue")
                if content_item:
                    current_subtopic["content"].append(content_item)
        
        elif style == "# Highlight Green":
            # Extract content (text and equations) in document order
            content_list = extract_paragraph_content_in_order(paragraph)
            
            if current_subtopic is not None and content_list:
                if "content" not in current_subtopic:
                    current_subtopic["content"] = []
                
                # Use paragraph wrapper for mixed content
                content_item = create_paragraph_wrapper(content_list, "highlight-green")
                if content_item:
                    current_subtopic["content"].append(content_item)
        
        # For all other paragraph styles, check if they contain equations
        # This handles styles like "# Body Equation", "# Headline", "# Highlight", etc.
        else:
            # Extract content (text and equations) in document order
            content_list = extract_paragraph_content_in_order(paragraph)
            
            # Add each content item in order
            if current_subtopic is not None and content_list:
                if "content" not in current_subtopic:
                    current_subtopic["content"] = []
                
                # List of styles where we want to extract both text and equations
                text_enabled_styles = ["# Highlight", "# Headline", "# Body Equation"]
                
                for content_type, content_value in content_list:
                    if content_type == 'equation':
                        equation_item = {
                            "id": generate_id(),
                            "type": "equation",
                            "equation": content_value
                        }
                        current_subtopic["content"].append(equation_item)
                    elif content_type == 'text' and style in text_enabled_styles:
                        # Extract text from known styles that may contain inline equations
                        text_item = {
                            "id": generate_id(),
                            "type": "body",
                            "text": content_value
                        }
                        current_subtopic["content"].append(text_item)
        
        # Check for images in paragraph runs
        for run in paragraph.runs:
            # Look for drawing elements in the run's XML
            drawing_elements = run.element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing', )
            
            for drawing in drawing_elements:
                # Find blip elements which contain image references
                blips = drawing.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip')
                
                for blip in blips:
                    # Get the relationship ID
                    embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    
                    if embed_id:
                        try:
                            # Get the image part from the relationship
                            image_part = doc.part.related_parts[embed_id]
                            image_bytes = image_part.blob
                            
                            # Determine image extension
                            content_type = image_part.content_type
                            ext = 'png'
                            if 'jpeg' in content_type or 'jpg' in content_type:
                                ext = 'jpg'
                            elif 'png' in content_type:
                                ext = 'png'
                            elif 'gif' in content_type:
                                ext = 'gif'
                            
                            # Generate consistent ID based on image content hash
                            # This ensures the same image always gets the same ID
                            image_hash = hashlib.md5(image_bytes).hexdigest()
                            image_id = image_hash[:8]  # Use first 8 characters
                            
                            # Use the ID as the filename
                            image_filename = f"{image_id}.{ext}"
                            image_path = images_dir / image_filename
                            
                            # Save image only if it doesn't already exist
                            if not image_path.exists():
                                with open(image_path, 'wb') as img_file:
                                    img_file.write(image_bytes)
                            
                            # Create image content item with relative URL
                            image_url = f"/db/{standard}-{subject_slug}/images/{image_filename}"
                            
                            # Get alt text from current context
                            if current_subtopic:
                                alt_text = current_subtopic['title']
                            elif current_topic:
                                alt_text = current_topic['title']
                            else:
                                alt_text = "Image"
                            
                            content_item = {
                                "id": image_id,
                                "type": "image",
                                "url": image_url,
                                "metadata": {
                                    "altText": alt_text,
                                    "size": "medium"  # Default size
                                }
                            }
                            
                            # Add to current subtopic
                            if current_subtopic is not None:
                                if "content" not in current_subtopic:
                                    current_subtopic["content"] = []
                                current_subtopic["content"].append(content_item)
                            
                        except Exception as e:
                            print(f"Warning: Could not extract image from embed_id {embed_id}: {e}")
        
    
    return result




def get_subject_id(standard, subject):
    """
    Fetch the subject ID from subjects.json based on standard and subject name.
    If not found, automatically adds the standard and/or subject under TNSB publisher.
    
    Args:
        standard: The standard/grade number (e.g., "6")
        subject: The subject name (e.g., "science")
    
    Returns:
        The subject ID (creates new entry if not found)
    """
    subjects_path = Path("../../db/subjects.json")
    
    if not subjects_path.exists():
        print(f"Warning: subjects.json not found at {subjects_path}")
        return ""
    
    try:
        with open(subjects_path, 'r', encoding='utf-8') as f:
            subjects_data = json.load(f)
        
        # Normalize subject name for comparison (capitalize first letter)
        subject_normalized = subject.capitalize()
        
        # Find TNSB publisher (or create if doesn't exist)
        tnsb_publisher = None
        for publisher in subjects_data.get('publishers', []):
            if publisher.get('publisherName') == 'TNSB':
                tnsb_publisher = publisher
                break
        
        if not tnsb_publisher:
            print("Warning: TNSB publisher not found in subjects.json")
            return ""
        
        # Search for the standard
        standard_obj = None
        for std in tnsb_publisher.get('standards', []):
            if std.get('standardName') == standard:
                standard_obj = std
                break
        
        # If standard not found, create it
        if not standard_obj:
            print(f"Standard '{standard}' not found. Creating new standard entry.")
            standard_obj = {
                "id": generate_id(),
                "standardName": standard,
                "subjects": []
            }
            tnsb_publisher['standards'].append(standard_obj)
            # Sort standards by standardName
            tnsb_publisher['standards'].sort(key=lambda x: int(x.get('standardName', '0')))
        
        # Search for the subject within the standard
        for subj in standard_obj.get('subjects', []):
            if subj.get('subjectName', '').lower() == subject_normalized.lower():
                return subj.get('id', '')
        
        # If subject not found, create it
        print(f"Subject '{subject}' not found for standard '{standard}'. Creating new subject entry.")
        new_subject_id = generate_id()
        new_subject = {
            "id": new_subject_id,
            "subjectName": subject_normalized
        }
        standard_obj['subjects'].append(new_subject)
        
        # Write updated data back to subjects.json
        with open(subjects_path, 'w', encoding='utf-8') as f:
            json.dump(subjects_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Added subject '{subject_normalized}' to standard '{standard}' with ID: {new_subject_id}")
        return new_subject_id
        
    except Exception as e:
        print(f"Warning: Error reading subjects.json: {e}")
        return ""


def process_single_file(input_file, standard, subject, subject_id, db_path):
    """
    Process a single Word document and update the database.
    
    Args:
        input_file: Path to the Word document
        standard: The standard/grade number
        subject: The subject name
        subject_id: The subject ID from subjects.json
        db_path: Path to the concept.json database file
    """
    # Extract chapter number from filename (without extension)
    input_path = Path(input_file)
    
    try:
        chapter_no = int(input_path.stem)  # Convert to integer
    except ValueError:
        print(f"⚠ Skipping '{input_path.name}': Filename must be a number (e.g., 1.docx, 2.docx)")
        return False
    
    try:
        # Process the document to get topics
        result = process_word_document(input_file, standard, subject)
        topics = result['topics']
        
        # Read the existing database or create a new one
        if db_path.exists():
            with open(db_path, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
        else:
            # Create a new database structure
            db_data = {
                "chapters": []
            }
        
        # Find the chapter in the database
        chapter_found = False
        for chapter in db_data.get('chapters', []):
            if chapter.get('chapterNo') == chapter_no:
                # Update the topics for this chapter
                chapter['topics'] = topics
                chapter_found = True
                # print(f"✓ Updated Chapter {chapter_no}: {input_path.name}")
                break
        
        if not chapter_found:
            # Create a new chapter entry
            new_chapter = {
                "id": generate_id(),
                "subjectId": subject_id,
                "chapterNo": chapter_no,
                "chapterName": f"Chapter {chapter_no}",  # Default name
                "topics": topics
            }
            db_data['chapters'].append(new_chapter)
            print(f"✓ Added Chapter {chapter_no}: {input_path.name}")
        
        # Sort chapters by chapterNo to maintain numerical order
        db_data['chapters'].sort(key=lambda x: x.get('chapterNo', 0))
        
        # Write the updated database back to file
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db_data, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"✗ Error processing '{input_path.name}': {str(e)}")
        return False


def run_objects_scanner():
    """Run the Objects Scanner tool to detect SmartArt, Drawing Canvas, Tables, and Cropped Images."""
    print("\n" + "=" * 60)
    print("Objects Scanner")
    print("=" * 60)
    print()
    
    # Use the ./input directory automatically
    script_dir = Path(__file__).parent
    dir_path = script_dir / "input"
    
    if not dir_path.exists():
        print(f"Error: Directory '{dir_path}' not found.")
        return
    
    if not dir_path.is_dir():
        print(f"Error: '{dir_path}' is not a directory.")
        return
    
    # Find all .docx files in the directory (exclude temporary files starting with ~$)
    all_docx_files = dir_path.glob("*.docx")
    docx_files = sorted([f for f in all_docx_files if not f.name.startswith("~$")])
    
    if not docx_files:
        print(f"Error: No .docx files found in '{dir_path}'")
        return
    
    print(f"Found {len(docx_files)} .docx file(s) to scan")
    print("Scanning files and adding comments...")
    print()
    
    files_with_issues = []
    
    # Scan each file
    for docx_file in docx_files:
        print(f"  Scanning '{docx_file.name}'...")
        objects = scan_for_smartart_and_canvas(docx_file)
        
        if objects:
            print(f"    ⚠ Found {len(objects)} issue(s). Comments added.")
            files_with_issues.append(docx_file)
        else:
            print("    ✓ No issues found.")

    print()
    print(f"Scan complete. Found issues in {len(files_with_issues)} file(s).")
    
    if files_with_issues and WIN32COM_AVAILABLE:
        print("\n" + "-" * 60)
        print("Starting Review Process")
        print("-" * 60)
        print("Opening files one by one for manual review.")
        print("Please address the comments in each document (e.g., convert SmartArt to images).")
        print("When done with a file, Save and Close it.")
        print()
        
        try:
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = True
            
            for i, file_path in enumerate(files_with_issues):
                print(f"[{i+1}/{len(files_with_issues)}] Opening: {file_path.name}")
                
                abs_path = str(Path(file_path).resolve())
                try:
                    doc = word.Documents.Open(abs_path)
                    doc.Activate()
                    
                    print(f"  >>> Waiting for you to review '{file_path.name}'...")
                    input("  >>> Press Enter when you have finished reviewing and CLOSED the document... ")
                    
                    # Ensure doc is closed if user didn't close it
                    try:
                        # Attempt to close. If it's already closed, this will fail (which is fine)
                        doc.Close(False) 
                    except Exception:
                        pass 
                        
                except Exception as e:
                    print(f"  Error handling document: {e}")
            
            print("\nAll files reviewed.")
            try:
                word.Quit()
            except:
                pass
            
        except Exception as e:
            print(f"Error initializing Word for review: {e}")
    elif files_with_issues and not WIN32COM_AVAILABLE:
        print("\n⚠ Cannot start auto-review: win32com not available.")
        print("Please manually review the files listed above.")
    
    print("\n" + "=" * 60)


def run_concepts_exporter():
    """Run the Concepts Exporter tool to extract content from docx and push it to JSON."""
    
    # Prompt for standard
    standard = input("Enter standard (e.g., 6, 7, 8): ").strip()
    if not standard:
        print("Error: Standard cannot be empty.")
        return
    
    # Prompt for subject
    subject = input("Enter subject (e.g., science, maths): ").strip()
    if not subject:
        print("Error: Subject cannot be empty.")
        return
    
    # Use the ./input directory automatically
    script_dir = Path(__file__).parent
    dir_path = script_dir / "input"
    
    if not dir_path.exists():
        print(f"Error: Directory '{dir_path}' not found.")
        return
    
    if not dir_path.is_dir():
        print(f"Error: '{dir_path}' is not a directory.")
        return
    
    # Find all .docx files in the directory (exclude temporary files starting with ~$)
    all_docx_files = dir_path.glob("*.docx")
    docx_files = sorted([f for f in all_docx_files if not f.name.startswith("~$")])
    
    if not docx_files:
        print(f"Error: No .docx files found in '{dir_path}'")
        return
    
    # Get subject ID from subjects.json
    subject_id = get_subject_id(standard, subject)
    
    # Construct database directory and filename
    db_dir = Path(f"../../db/{standard}-{subject.lower()}")
    db_path = db_dir / "concept.json"
    
    # Create database directory if it doesn't exist
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # Process all files
    # print("Processing files...")
    # print("-" * 60)
    
    success_count = 0
    fail_count = 0
    
    for docx_file in docx_files:
        if process_single_file(docx_file, standard, subject, subject_id, db_path):
            success_count += 1
        else:
            fail_count += 1
    
    # Summary
    # print("-" * 60)
    # print()
    # print("Summary:")
    print(f"Successfully processed: {success_count} file(s)")
    # if fail_count > 0:
    #     print(f"  ✗ Failed: {fail_count} file(s)")
    # print(f"  📁 Output: {db_path}")
    # print()
    # print("=" * 60)


def display_menu():
    """Display the migration tools menu."""
    # print("\n")
    print("Please select a migration tool:")
    print("  1. Objects Scanner")
    print("  2. Concepts Exporter")


def main():
    """Main function to handle interactive execution."""
    while True:
        display_menu()
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            run_objects_scanner()
        elif choice == "2":
            run_concepts_exporter()
        elif choice == "0":
            print("\nExiting Migration Tools. Goodbye!")
            break
        else:
            print("\n⚠ Invalid choice. Please enter a number between 0 and 2.")
        
        # Ask if user wants to continue
        if choice in ["1", "2"]:
            print()
            continue_choice = input("Press Enter to return to menu").strip().lower()
            if continue_choice == "exit":
                # print("\nExiting Migration Tools. Goodbye!")
                break


if __name__ == "__main__":
    main()