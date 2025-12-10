"""
Debug script to check if images have crop information in the Word document.
"""

import win32com.client
from pathlib import Path

def check_image_crops(file_path):
    word = None
    doc = None
    
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        
        abs_path = str(Path(file_path).resolve())
        doc = word.Documents.Open(abs_path)
        
        print(f"\n=== Checking Image Crops: {Path(file_path).name} ===\n")
        
        # Check InlineShapes (where most images are)
        print(f"InlineShapes: {doc.InlineShapes.Count} items")
        for i, shape in enumerate(doc.InlineShapes, 1):
            if shape.Type == 3:  # Picture
                try:
                    # Check if image has crop properties
                    has_crop = False
                    crop_info = []
                    
                    # Try to get crop values
                    try:
                        if hasattr(shape.PictureFormat, 'CropLeft'):
                            left = shape.PictureFormat.CropLeft
                            top = shape.PictureFormat.CropTop
                            right = shape.PictureFormat.CropRight
                            bottom = shape.PictureFormat.CropBottom
                            
                            if left != 0 or top != 0 or right != 0 or bottom != 0:
                                has_crop = True
                                crop_info = [f"L={left:.1f}", f"T={top:.1f}", f"R={right:.1f}", f"B={bottom:.1f}"]
                    except:
                        pass
                    
                    page = shape.Range.Information(3)
                    if has_crop:
                        print(f"  InlineShape {i}: Page={page}, CROPPED ({', '.join(crop_info)})")
                    else:
                        print(f"  InlineShape {i}: Page={page}, No crop")
                except Exception as e:
                    print(f"  InlineShape {i}: Error - {e}")
        
        # Check Shapes
        print(f"\nShapes: {doc.Shapes.Count} items")
        for i, shape in enumerate(doc.Shapes, 1):
            if shape.Type == 13:  # Picture in shapes
                try:
                    has_crop = False
                    crop_info = []
                    
                    try:
                        if hasattr(shape.PictureFormat, 'CropLeft'):
                            left = shape.PictureFormat.CropLeft
                            top = shape.PictureFormat.CropTop
                            right = shape.PictureFormat.CropRight
                            bottom = shape.PictureFormat.CropBottom
                            
                            if left != 0 or top != 0 or right != 0 or bottom != 0:
                                has_crop = True
                                crop_info = [f"L={left:.1f}", f"T={top:.1f}", f"R={right:.1f}", f"B={bottom:.1f}"]
                    except:
                        pass
                    
                    page = shape.Anchor.Information(3)
                    if has_crop:
                        print(f"  Shape {i}: Page={page}, CROPPED ({', '.join(crop_info)})")
                    else:
                        print(f"  Shape {i}: Page={page}, No crop")
                except Exception as e:
                    print(f"  Shape {i}: Error - {e}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        if doc:
            doc.Close(False)
        if word:
            word.Quit()

if __name__ == "__main__":
    input_dir = Path("input")
    docx_files = list(input_dir.glob("*.docx"))
    
    if docx_files:
        check_image_crops(docx_files[0])
    else:
        print("No .docx files found in input directory")
