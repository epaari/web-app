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
        "topics": []
    }
    
    current_topic = None
    current_subtopic = None
    node_image_counter = 0  # Counter for images within current subtopic
    
    # Process all paragraphs
    for paragraph in doc.paragraphs:
        style = get_paragraph_style(paragraph)
        text = paragraph.text.strip()
        
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
            node_image_counter = 0  # Reset image counter for new topic
            
        elif style == "# Sub Topic - 2":
            # Create a new subtopic
            current_subtopic = {
                "id": generate_id(),
                "title": text,
                "content": []
            }
            node_image_counter = 0  # Reset image counter for new subtopic
            
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
                            
                            # Generate filename based on current context
                            if current_subtopic:
                                base_name = sanitize_filename(current_subtopic['title'])
                            elif current_topic:
                                base_name = sanitize_filename(current_topic['title'])
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
                                "id": generate_id(),
                                "type": "image",
                                "url": image_url,
                                "metadata": {
                                    "altText": base_name,
                                    "width": 1920,
                                    "height": 1080
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


def upload_images_to_github(output_dir):
    """
    Upload images from output directory to GitHub repository.
    Asks for user consent before uploading.
    
    Args:
        output_dir: Path to the output directory containing images
    
    Returns:
        bool: True if upload was successful or skipped, False if failed
    """
    # Check if there are any image files to upload
    image_files = list(output_dir.glob('*.png')) + list(output_dir.glob('*.jpg')) + list(output_dir.glob('*.gif'))
    
    if not image_files:
        print("No images to upload.")
        return True
    
    # Ask for user consent
    print(f"\nFound {len(image_files)} image(s) to upload to GitHub.")
    print("Images will be uploaded to: https://github.com/epaari/images")
    
    while True:
        consent = input("Do you want to upload these images? (yes/no): ").strip().lower()
        if consent in ['yes', 'y']:
            break
        elif consent in ['no', 'n']:
            print("Image upload skipped.")
            return True
        else:
            print("Please enter 'yes' or 'no'.")
    
    # Define the GitHub repository path
    github_repo_path = Path("../content-images")
    
    # Check if the repository exists
    if not github_repo_path.exists():
        print(f"Error: GitHub repository not found at {github_repo_path}")
        print("Please clone the repository first: git clone https://github.com/epaari/images.git ../content-images")
        return False
    
    try:
        # Copy images to the GitHub repository
        for image_file in image_files:
            dest_file = github_repo_path / image_file.name
            import shutil
            shutil.copy2(image_file, dest_file)
            print(f"Copied: {image_file.name}")
        
        # Git operations
        print("\nUploading to GitHub...")
        
        # Change to repository directory
        os.chdir(github_repo_path)
        
        # Git add
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Git commit
        commit_message = f"Add images from document conversion"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Git push
        subprocess.run(['git', 'push'], check=True)
        
        print("✓ Images successfully uploaded to GitHub!")
        
        # Delete image files from output directory after successful upload
        print("\nCleaning up output directory...")
        for image_file in image_files:
            try:
                image_file.unlink()
                print(f"Deleted: {image_file.name}")
            except Exception as e:
                print(f"Warning: Could not delete {image_file.name}: {e}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during git operation: {e}")
        return False
    except Exception as e:
        print(f"Error uploading images: {e}")
        return False




def get_subject_id(standard, subject):
    """
    Fetch the subject ID from subjects.json based on standard and subject name.
    
    Args:
        standard: The standard/grade number (e.g., "6")
        subject: The subject name (e.g., "science")
    
    Returns:
        The subject ID if found, empty string otherwise
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
        
        # Search through publishers -> standards -> subjects
        for publisher in subjects_data.get('publishers', []):
            for std in publisher.get('standards', []):
                if std.get('standardName') == standard:
                    for subj in std.get('subjects', []):
                        if subj.get('subjectName', '').lower() == subject_normalized.lower():
                            return subj.get('id', '')
        
        print(f"Warning: Subject '{subject}' not found for standard '{standard}' in subjects.json")
        return ""
        
    except Exception as e:
        print(f"Warning: Error reading subjects.json: {e}")
        return ""


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
    
    # Get subject ID from subjects.json
    subject_id = get_subject_id(standard, subject)
    
    # Construct database directory and filename
    db_dir = Path(f"../db/{standard}-{subject.lower()}")
    db_path = db_dir / "concept.json"
    
    # Create database directory if it doesn't exist
    db_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Process the document to get topics
        result = process_word_document(input_file)
        topics = result['topics']
        
        # Read the existing database or create a new one
        if db_path.exists():
            with open(db_path, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
        else:
            # Create a new database structure
            print(f"Database file not found. Creating new file: {db_path}")
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
                break
        
        if not chapter_found:
            # Create a new chapter entry
            print(f"Chapter {chapter_no} not found. Creating new chapter entry.")
            new_chapter = {
                "id": generate_id(),
                "subjectId": subject_id,
                "chapterNo": chapter_no,
                "chapterName": f"Chapter {chapter_no}",  # Default name
                "topics": topics
            }
            db_data['chapters'].append(new_chapter)
        
        # Write the updated database back to file
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db_data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully converted '{input_path.stem}'")
        
        # Upload images to GitHub
        output_dir = Path("./output")
        upload_images_to_github(output_dir)
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
