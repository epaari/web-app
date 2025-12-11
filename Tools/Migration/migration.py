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
                    print(f"  [DEBUG] Found display equation: {latex[:50]}...")
                    equations.append((latex, True))  # True = display equation
        
        for omath in run.element.findall(f'.//{m_ns}oMath'):
            # Check if this oMath is not inside an oMathPara (to avoid duplicates)
            if omath.getparent().tag != f'{m_ns}oMathPara':
                latex = omml_to_latex(omath)
                if latex:
                    print(f"  [DEBUG] Found inline equation: {latex[:50]}...")
                    equations.append((latex, False))  # False = inline equation
    
    except Exception as e:
        print(f"Warning: Error extracting equations: {e}")
        import traceback
        traceback.print_exc()
    
    return equations



def scan_for_smartart_and_canvas(file_path):
    """
    Scan a Word document for SmartArt, Drawing Canvas, Tables, and Cropped Images.
    
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
        
        # Scan Shapes collection
        shape_count = 0
        for shape in doc.Shapes:
            shape_count += 1
            try:
                # Get the page number where this shape is located
                page_num = shape.Anchor.Information(3)  # wdActiveEndPageNumber = 3
                shape_type = shape.Type
                
                # Type 15 is msoSmartArt
                if shape_type == 15:
                    objects_found.append({
                        'type': 'SmartArt',
                        'page': page_num
                    })
                # Type 16 is msoCanvas (old constant, rarely used)
                # Type 20 is msoDiagram/msoGroup (Drawing Canvas in modern Word)
                elif shape_type == 16 or shape_type == 20:
                    objects_found.append({
                        'type': 'Drawing Canvas',
                        'page': page_num
                    })
                # Type 13 is Picture - check if cropped
                elif shape_type == 13:
                    try:
                        if hasattr(shape.PictureFormat, 'CropLeft'):
                            left = shape.PictureFormat.CropLeft
                            top = shape.PictureFormat.CropTop
                            right = shape.PictureFormat.CropRight
                            bottom = shape.PictureFormat.CropBottom
                            
                            if left != 0 or top != 0 or right != 0 or bottom != 0:
                                objects_found.append({
                                    'type': 'Cropped Image',
                                    'page': page_num
                                })
                    except:
                        pass
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
                
                # Type 15 is wdInlineShapeSmartArt
                if shape_type == 15:
                    objects_found.append({
                        'type': 'SmartArt',
                        'page': page_num
                    })
                # Type 3 is Picture - check if cropped
                elif shape_type == 3:
                    try:
                        if hasattr(inline_shape.PictureFormat, 'CropLeft'):
                            left = inline_shape.PictureFormat.CropLeft
                            top = inline_shape.PictureFormat.CropTop
                            right = inline_shape.PictureFormat.CropRight
                            bottom = inline_shape.PictureFormat.CropBottom
                            
                            if left != 0 or top != 0 or right != 0 or bottom != 0:
                                objects_found.append({
                                    'type': 'Cropped Image',
                                    'page': page_num
                                })
                    except:
                        pass
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
                objects_found.append({
                    'type': 'Table',
                    'page': page_num
                })
            except Exception as e:
                # Some tables might not have page info
                pass
        
        # Debug output
        if shape_count == 0 and inline_count == 0 and table_count == 0:
            print("  (No shapes, inline shapes, or tables found in document)")
        
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
            # Extract text with bold formatting
            formatted_text = extract_text_with_formatting(paragraph)
            
            # Only create content item if there's actual text (not just equations)
            if formatted_text.strip():
                content_item = {
                    "id": generate_id(),
                    "type": "bullet1",
                    "text": formatted_text
                }
                
                # Add to current subtopic's content if exists
                if current_subtopic is not None:
                    if "content" not in current_subtopic:
                        current_subtopic["content"] = []
                    current_subtopic["content"].append(content_item)
                
        elif style == "# Body":
            # Extract text with bold formatting
            formatted_text = extract_text_with_formatting(paragraph)
            
            # Only create content item if there's actual text (not just equations)
            if formatted_text.strip():
                content_item = {
                    "id": generate_id(),
                    "type": "body",
                    "text": formatted_text
                }
                
                # Add to current subtopic's content if exists
                if current_subtopic is not None:
                    if "content" not in current_subtopic:
                        current_subtopic["content"] = []
                    current_subtopic["content"].append(content_item)
                
        elif style == "# Bullet-2":
            # Extract text with bold formatting
            formatted_text = extract_text_with_formatting(paragraph)
            
            # Only create content item if there's actual text (not just equations)
            if formatted_text.strip():
                content_item = {
                    "id": generate_id(),
                    "type": "bullet2",
                    "text": formatted_text
                }
                
                # Add to current subtopic's content if exists
                if current_subtopic is not None:
                    if "content" not in current_subtopic:
                        current_subtopic["content"] = []
                    current_subtopic["content"].append(content_item)
        
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
        
        # Check for equations at paragraph level (not just in runs)
        # Equations are stored in the paragraph's XML structure
        m_ns = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
        
        try:
            # Search for math elements in the paragraph's XML
            para_xml = paragraph._element
            

            
            # Display equations (oMathPara)
            math_paras = para_xml.findall(f'.//{m_ns}oMathPara')
            
            for math_para in math_paras:
                # An oMathPara can contain multiple oMath elements (separated by line breaks)
                omaths = math_para.findall(f'{m_ns}oMath')
                
                if omaths:
                    latex_lines = []
                    for omath in omaths:
                        latex = omml_to_latex(omath)
                        if latex:
                            latex_lines.append(latex)
                    
                    if latex_lines:
                        # If multiple equations, combine them with aligned environment
                        if len(latex_lines) > 1:
                            # Add alignment markers for multi-line equations
                            aligned_lines = []
                            for line in latex_lines:
                                # If line starts with =, add & before it
                                if line.strip().startswith('='):
                                    aligned_lines.append('&' + line.strip())
                                else:
                                    aligned_lines.append(line)
                            
                            combined_latex = '\\begin{aligned}\n' + ' \\\\\n'.join(aligned_lines) + '\n\\end{aligned}'
                            print(f"  [DEBUG] Found multi-line display equation: {combined_latex}")
                        else:
                            combined_latex = latex_lines[0]
                            print(f"  [DEBUG] Found display equation: {combined_latex}")
                        
                        equation_item = {
                            "id": generate_id(),
                            "type": "equation",
                            "equation": combined_latex
                        }
                        
                        # Add to current subtopic
                        if current_subtopic is not None:
                            if "content" not in current_subtopic:
                                current_subtopic["content"] = []
                            current_subtopic["content"].append(equation_item)
            
            # Inline equations (oMath not inside oMathPara)
            inline_omaths = para_xml.findall(f'.//{m_ns}oMath')
            inline_count = 0
            
            # Get all oMath elements that are inside oMathPara (to exclude them)
            omaths_in_para = []
            for math_para in math_paras:
                omaths_in_para.extend(math_para.findall(f'.//{m_ns}oMath'))
            
            for omath in inline_omaths:
                # Check if this oMath is NOT in the list of oMaths inside oMathPara
                if omath not in omaths_in_para:
                    latex = omml_to_latex(omath)
                    if latex:
                        print(f"  [DEBUG] Found inline equation: {latex[:100]}...")
                        equation_item = {
                            "id": generate_id(),
                            "type": "equation",
                            "equation": latex
                        }
                        
                        # Add to current subtopic
                        if current_subtopic is not None:
                            if "content" not in current_subtopic:
                                current_subtopic["content"] = []
                            current_subtopic["content"].append(equation_item)
        
        except Exception as e:
            print(f"Warning: Error extracting equations from paragraph: {e}")
            import traceback
            traceback.print_exc()
    
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
        # Scan for SmartArt, Drawing Canvas, Tables, and Cropped Images before processing
        objects = scan_for_smartart_and_canvas(input_file)
        
        if objects:
            print(f"\n⚠ Found {len(objects)} object(s) in '{input_path.name}' that need to be converted to images:")
            
            # Group by type and page
            for obj in objects:
                print(f"  • {obj['type']} on page {obj['page']}")
            
            print("\nPlease convert these objects to images in the Word document:")
            print()
            
            # Prompt user for confirmation
            response = input("Have you converted all objects to images? (yes/no): ").strip().lower()
            
            if response not in ['yes', 'y']:
                print(f"⚠ Skipping '{input_path.name}' - Please convert objects and try again")
                return False
        
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
    print("Scanning files...")
    print()
    
    # Create reports directory
    reports_dir = script_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Prepare CSV report file
    report_path = reports_dir / "Objects-Scanner-Report.csv"
    
    # Collect all scan results as CSV rows
    csv_rows = []
    csv_rows.append("Document,Page No,Issue")  # Header
    
    total_objects = 0
    
    # Scan each file
    for docx_file in docx_files:
        print(f"  Scanning '{docx_file.name}'...")
        objects = scan_for_smartart_and_canvas(docx_file)
        
        if objects:
            total_objects += len(objects)
            for obj in objects:
                csv_rows.append(f"{docx_file.stem},{obj['page']},{obj['type']}")
    
    # Write CSV report to file
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(csv_rows))
    
    print()
    print(f"✓ Scan complete!")
    print(f"  Total objects found: {total_objects}")
    print(f"  Report saved to: {report_path}")
    print("\n" + "=" * 60)


def run_concepts_exporter():
    """Run the Concepts Exporter tool to extract content from docx and push it to JSON."""
    print("\n" + "=" * 60)
    print("Concepts Exporter")
    print("=" * 60)
    print()
    
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
    print("Processing files...")
    print("-" * 60)
    
    success_count = 0
    fail_count = 0
    
    for docx_file in docx_files:
        if process_single_file(docx_file, standard, subject, subject_id, db_path):
            success_count += 1
        else:
            fail_count += 1
    
    # Summary
    print("-" * 60)
    print()
    print("Summary:")
    print(f"  ✓ Successfully processed: {success_count} file(s)")
    if fail_count > 0:
        print(f"  ✗ Failed: {fail_count} file(s)")
    print(f"  📁 Output: {db_path}")
    print()
    print("=" * 60)


def display_menu():
    """Display the migration tools menu."""
    print("\n")
    print("Please select a migration tool:")
    print()
    print("  1. Objects Scanner")
    print()
    print("  2. Concepts Exporter")
    print()
    print("  0. Exit")
    print()


def main():
    """Main function to handle interactive execution."""
    while True:
        display_menu()
        
        choice = input("Enter your choice (0-2): ").strip()
        
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
            continue_choice = input("Press Enter to return to menu or type 'exit' to quit: ").strip().lower()
            if continue_choice == "exit":
                print("\nExiting Migration Tools. Goodbye!")
                break


if __name__ == "__main__":
    main()