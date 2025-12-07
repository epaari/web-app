"""
Word Document to JSON Converter
Extracts text from a Microsoft Word file and converts it to a structured JSON format.
"""

import sys
import json
import random
import os
import re
from pathlib import Path
from docx import Document
from docx.text.paragraph import Paragraph


def generate_id(label):
    """Generate a 3-digit random number followed by the sanitized label."""
    random_num = random.randint(100, 999)
    sanitized_label = sanitize_filename(label)
    return f"{random_num}-{sanitized_label}"


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


def process_word_document(file_path):
    """
    Process a Word document and convert it to the specified JSON schema.
    
    Args:
        file_path: Path to the Word document
    
    Returns:
        Dictionary containing the structured data
    """
    doc = Document(file_path)
    
    # Create output directory and clear it if it exists
    output_dir = Path("./output")
    if output_dir.exists():
        # Remove all files in the output directory
        for file in output_dir.iterdir():
            if file.is_file():
                file.unlink()
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    images_dir = output_dir
    
    
    # Initialize the result structure
    result = {
        "nodes": []
    }
    
    current_title1_node = None
    current_title2_node = None
    node_image_counter = 0  # Counter for images within current node
    
    # Process all paragraphs
    for paragraph in doc.paragraphs:
        style = get_paragraph_style(paragraph)
        text = paragraph.text.strip()
        
        # Process based on style
        if style == "# Sub Topic - 1":
            # Create a new title1 node
            current_title1_node = {
                "id": generate_id(text),
                "nodeType": "title1",
                "label": text,
                "children": []
            }
            result["nodes"].append(current_title1_node)
            current_title2_node = None  # Reset title2 when new title1 starts
            node_image_counter = 0  # Reset image counter for new node
            
        elif style == "# Sub Topic - 2":
            # Create a new title2 node
            current_title2_node = {
                "id": generate_id(text),
                "nodeType": "title2",
                "label": text,
                "content": []
            }
            node_image_counter = 0  # Reset image counter for new node
            
            # Add to current title1 node's children if exists
            if current_title1_node is not None:
                current_title1_node["children"].append(current_title2_node)
            else:
                # If no title1 exists, add directly to nodes
                result["nodes"].append(current_title2_node)
                
        elif style == "# Bullet-1":
            # Extract text with bold formatting
            formatted_text = extract_text_with_formatting(paragraph)
            
            content_item = {
                "type": "bullet1",
                "text": formatted_text
            }
            
            # Add to current title2 node's content if exists
            if current_title2_node is not None:
                if "content" not in current_title2_node:
                    current_title2_node["content"] = []
                current_title2_node["content"].append(content_item)
            elif current_title1_node is not None:
                # If no title2 but title1 exists, add to title1's content
                if "content" not in current_title1_node:
                    current_title1_node["content"] = []
                current_title1_node["content"].append(content_item)
                
        elif style == "# Bullet-2":
            # Extract text with bold formatting
            formatted_text = extract_text_with_formatting(paragraph)
            
            content_item = {
                "type": "bullet2",
                "text": formatted_text
            }
            
            # Add to current title2 node's content if exists
            if current_title2_node is not None:
                if "content" not in current_title2_node:
                    current_title2_node["content"] = []
                current_title2_node["content"].append(content_item)
            elif current_title1_node is not None:
                # If no title2 but title1 exists, add to title1's content
                if "content" not in current_title1_node:
                    current_title1_node["content"] = []
                current_title1_node["content"].append(content_item)
        
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
                            
                            # Generate filename based on current context
                            if current_title2_node:
                                base_name = sanitize_filename(current_title2_node['label'])
                            elif current_title1_node:
                                base_name = sanitize_filename(current_title1_node['label'])
                            else:
                                base_name = f"image"
                            
                            # Increment counter (starting from 1)
                            node_image_counter += 1
                            image_filename = f"{base_name}-{node_image_counter}.{ext}"
                            image_path = images_dir / image_filename
                            
                            # Save image
                            with open(image_path, 'wb') as img_file:
                                img_file.write(image_bytes)
                            
                            # print(f"Extracted image: {image_filename}")
                            
                            # Create image content item
                            image_url = f"https://raw.githubusercontent.com/epaari/ezeescore_ai/main/{image_filename}"
                            content_item = {
                                "type": "image",
                                "url": image_url
                            }
                            
                            # Add to appropriate node
                            if current_title2_node is not None:
                                if "content" not in current_title2_node:
                                    current_title2_node["content"] = []
                                current_title2_node["content"].append(content_item)
                            elif current_title1_node is not None:
                                if "content" not in current_title1_node:
                                    current_title1_node["content"] = []
                                current_title1_node["content"].append(content_item)
                            
                        except Exception as e:
                            print(f"Warning: Could not extract image from embed_id {embed_id}: {e}")
    
    return result


def main():
    """Main function to handle command-line execution."""
    # Check for correct number of arguments
    if len(sys.argv) != 4:
        print("Usage: python doc_to_json.py <standard> <subject> <input-file>")
        print("Example: python doc_to_json.py 6 science 10.docx")
        sys.exit(1)
    
    standard = sys.argv[1]
    subject = sys.argv[2]
    input_file = sys.argv[3]
    
    # Validate input file exists
    if not Path(input_file).exists():
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    
    # Validate input file is a Word document
    if not input_file.lower().endswith(('.docx', '.doc')):
        print("Error: Input file must be a Microsoft Word document (.docx or .doc)")
        sys.exit(1)
    
    # Extract chapter number from filename (without extension)
    input_path = Path(input_file)
    chapter_no = input_path.stem
    
    # Construct database filename
    db_filename = f"../db/{standard}-{subject.lower()}-db.json"
    db_path = Path(db_filename)
    
    # Check if database file exists
    if not db_path.exists():
        print(f"Error: Database file '{db_filename}' not found.")
        sys.exit(1)
    
    try:
        # Process the document to get nodes
        result = process_word_document(input_file)
        nodes = result['nodes']
        
        # Read the existing database
        with open(db_path, 'r', encoding='utf-8') as f:
            db_data = json.load(f)
        
        # Find the chapter in the database
        chapter_found = False
        for chapter in db_data.get('chapters', []):
            if chapter.get('chapterNo') == chapter_no:
                # Update the nodes for this chapter
                chapter['nodes'] = nodes
                chapter_found = True
                break
        
        if not chapter_found:
            print(f"Error: Chapter {chapter_no} not found in database.")
            sys.exit(1)
        
        # Write the updated database back to file
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db_data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully converted '{input_path.stem}'")
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
