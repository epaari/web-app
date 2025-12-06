"""
Word Document to JSON Converter
Extracts text from a Microsoft Word file and converts it to a structured JSON format.
"""

import sys
import json
import random
from pathlib import Path
from docx import Document
from docx.text.paragraph import Paragraph


def generate_id(label):
    """Generate a 3-digit random number followed by the label."""
    random_num = random.randint(100, 999)
    return f"{random_num}-{label}"


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


def process_word_document(file_path, chapter_no="1", chapter_title="Measurements"):
    """
    Process a Word document and convert it to the specified JSON schema.
    
    Args:
        file_path: Path to the Word document
        chapter_no: Chapter number (default: "1")
        chapter_title: Chapter title (default: "Measurements")
    
    Returns:
        Dictionary containing the structured data
    """
    doc = Document(file_path)
    
    # Initialize the result structure
    result = {
        "chapterNo": chapter_no,
        "chapterTitle": chapter_title,
        "nodes": []
    }
    
    current_title1_node = None
    current_title2_node = None
    
    for paragraph in doc.paragraphs:
        style = get_paragraph_style(paragraph)
        text = paragraph.text.strip()
        
        # Skip empty paragraphs
        if not text:
            continue
        
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
            
        elif style == "# Sub Topic - 2":
            # Create a new title2 node
            current_title2_node = {
                "id": generate_id(text),
                "nodeType": "title2",
                "label": text,
                "content": []
            }
            
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
    
    return result


def main():
    """Main function to handle command-line execution."""
    if len(sys.argv) < 2:
        print("Usage: python word_to_json.py <word_file_path> [chapter_no] [chapter_title]")
        print("Example: python word_to_json.py document.docx 1 Measurements")
        sys.exit(1)
    
    input_file = sys.argv[1]
    chapter_no = sys.argv[2]
    chapter_title = sys.argv[3]
    
    # Validate input file exists
    if not Path(input_file).exists():
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    
    # Validate input file is a Word document
    if not input_file.lower().endswith(('.docx', '.doc')):
        print("Error: Input file must be a Microsoft Word document (.docx or .doc)")
        sys.exit(1)
    
    try:
        # Process the document
        print(f"Processing '{input_file}'...")
        result = process_word_document(input_file, chapter_no, chapter_title)
        
        # Generate output filename
        input_path = Path(input_file)
        output_filename = f"db-{input_path.stem}.json"
        
        # Save to JSON file
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully converted to '{output_filename}'")
        print(f"Total nodes created: {len(result['nodes'])}")
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
