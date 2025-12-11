import sys
from pathlib import Path
from docx import Document
import xml.etree.ElementTree as ET

# Test script to debug equation extraction
def test_equation_extraction(docx_file):
    """Test equation extraction from a Word document."""
    doc = Document(docx_file)
    
    m_ns = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
    
    print(f"Testing: {docx_file}")
    print("=" * 60)
    
    total_math_found = 0
    
    # Check each paragraph
    for i, paragraph in enumerate(doc.paragraphs):
        para_text = paragraph.text[:80] if paragraph.text else "(empty)"
        
        # Search for any math elements in the paragraph's XML
        para_xml = paragraph._element
        math_paras = para_xml.findall(f'.//{m_ns}oMathPara')
        omaths = para_xml.findall(f'.//{m_ns}oMath')
        
        if math_paras or omaths:
            print(f"\n✓ Paragraph {i}: '{para_text}'")
            print(f"  Style: {paragraph.style.name if paragraph.style else 'None'}")
            print(f"  Found {len(math_paras)} oMathPara, {len(omaths)} oMath elements")
            total_math_found += len(math_paras) + len(omaths)
            
            # Check runs
            for j, run in enumerate(paragraph.runs):
                run_math_paras = run.element.findall(f'.//{m_ns}oMathPara')
                run_omaths = run.element.findall(f'.//{m_ns}oMath')
                if run_math_paras or run_omaths:
                    print(f"    Run {j}: {len(run_math_paras)} oMathPara, {len(run_omaths)} oMath")
                    
                    # Print a snippet of the XML
                    xml_str = ET.tostring(run.element, encoding='unicode')
                    print(f"    XML (first 150 chars): {xml_str[:150]}...")
    
    print("\n" + "=" * 60)
    print(f"Total math elements found: {total_math_found}")
    
    if total_math_found == 0:
        print("\n⚠ No equations found in document!")
        print("This could mean:")
        print("  1. The document doesn't contain equations")
        print("  2. Equations are in a different format (e.g., MathType, images)")
        print("  3. The document needs to be saved in a compatible format")

if __name__ == "__main__":
    # Test with the input file
    input_dir = Path(__file__).parent / "input"
    docx_files = sorted([f for f in input_dir.glob("*.docx") if not f.name.startswith("~$")])
    
    if docx_files:
        print(f"Found {len(docx_files)} .docx file(s)\n")
        for docx_file in docx_files:
            test_equation_extraction(docx_file)
            print("\n")
    else:
        print("No .docx files found in input directory")

