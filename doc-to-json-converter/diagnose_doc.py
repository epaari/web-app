"""
Quick diagnostic script to check what types of objects are in a Word document.
Run this to see all shape types in your document.
"""

import win32com.client
from pathlib import Path

def diagnose_document(file_path):
    word = None
    doc = None
    
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        
        abs_path = str(Path(file_path).resolve())
        doc = word.Documents.Open(abs_path)
        
        print(f"\n=== Diagnosing: {Path(file_path).name} ===\n")
        
        # Check Shapes
        print(f"Shapes collection: {doc.Shapes.Count} items")
        for i, shape in enumerate(doc.Shapes, 1):
            try:
                page = shape.Anchor.Information(3)
                print(f"  Shape {i}: Type={shape.Type}, Page={page}")
            except:
                print(f"  Shape {i}: Type={shape.Type}, Page=Unknown")
        
        # Check InlineShapes
        print(f"\nInlineShapes collection: {doc.InlineShapes.Count} items")
        for i, inline_shape in enumerate(doc.InlineShapes, 1):
            try:
                page = inline_shape.Range.Information(3)
                print(f"  InlineShape {i}: Type={inline_shape.Type}, Page={page}")
            except:
                print(f"  InlineShape {i}: Type={inline_shape.Type}, Page=Unknown")
        
        # Check Tables
        print(f"\nTables collection: {doc.Tables.Count} items")
        for i, table in enumerate(doc.Tables, 1):
            try:
                page = table.Range.Information(3)
                rows = table.Rows.Count
                cols = table.Columns.Count
                print(f"  Table {i}: {rows}x{cols}, Page={page}")
            except:
                print(f"  Table {i}: Page=Unknown")
        
        print("\nType reference:")
        print("  3 = Picture")
        print("  13 = OLE Object")
        print("  15 = SmartArt")
        print("  16 = Canvas (old constant)")
        print("  20 = Diagram/Canvas (msoGroup or msoDiagram)")
        print("  Note: Drawing Canvas is typically Type 20")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        if doc:
            doc.Close(False)
        if word:
            word.Quit()

if __name__ == "__main__":
    # Diagnose the first .docx file in input directory
    input_dir = Path("input")
    docx_files = list(input_dir.glob("*.docx"))
    
    if docx_files:
        diagnose_document(docx_files[0])
    else:
        print("No .docx files found in input directory")
