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
    images_dir = Path(f"../db/{standard}-{subject_slug}/images")
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
    subjects_path = Path("../db/subjects.json")
    
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
                print(f"✓ Updated Chapter {chapter_no}: {input_path.name}")
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


def main():
    """Main function to handle interactive execution."""
    print("=" * 60)
    print("Word Document to JSON Converter")
    print("=" * 60)
    print()
    
    # Prompt for standard
    standard = input("Enter standard (e.g., 6, 7, 8): ").strip()
    if not standard:
        print("Error: Standard cannot be empty.")
        sys.exit(1)
    
    # Prompt for subject
    subject = input("Enter subject (e.g., science, maths): ").strip()
    if not subject:
        print("Error: Subject cannot be empty.")
        sys.exit(1)
    
    # Use the ./input directory automatically
    script_dir = Path(__file__).parent
    dir_path = script_dir / "input"
    
    print(f"Using input directory: {dir_path}")
    print()
    if not dir_path.exists():
        print(f"Error: Directory '{dir_path}' not found.")
        sys.exit(1)
    
    if not dir_path.is_dir():
        print(f"Error: '{dir_path}' is not a directory.")
        sys.exit(1)
    
    # Find all .docx files in the directory (exclude temporary files starting with ~$)
    all_docx_files = dir_path.glob("*.docx")
    docx_files = sorted([f for f in all_docx_files if not f.name.startswith("~$")])
    
    if not docx_files:
        print(f"Error: No .docx files found in '{dir_path}'")
        sys.exit(1)
    
    print()
    print(f"Found {len(docx_files)} .docx file(s):")
    for file in docx_files:
        print(f"  - {file.name}")
    print()
    
    # Get subject ID from subjects.json
    subject_id = get_subject_id(standard, subject)
    
    # Construct database directory and filename
    db_dir = Path(f"../db/{standard}-{subject.lower()}")
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


if __name__ == "__main__":
    main()
