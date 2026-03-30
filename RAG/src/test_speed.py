# test_speed.py
import time
import os
from pathlib import Path

# Test PyMuPDF
print("Testing PyMuPDF speed...")
try:
    import fitz
    
    # Find a PDF to test
    pdf_dir = Path("malayalam_docs")
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if pdf_files:
        pdf_file = pdf_files[0]
        print(f"Testing with: {pdf_file.name}")
        
        # Test PyMuPDF
        start = time.time()
        doc = fitz.open(pdf_file)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        pymupdf_time = time.time() - start
        
        print(f"✅ PyMuPDF: {pymupdf_time:.2f}s, {len(text):,} chars")
        print(f"   Speed: {len(text)/pymupdf_time:,.0f} chars/sec")
    else:
        print("No PDF files found in malayalam_docs/")
        
except ImportError:
    print("❌ PyMuPDF not installed! Run: pip install PyMuPDF")

# Test Unstructured
print("\nTesting Unstructured...")
try:
    from unstructured.partition.pdf import partition_pdf
    
    if pdf_files:
        # Test fast strategy
        start = time.time()
        elements = partition_pdf(
            filename=str(pdf_file),
            strategy="fast",
            languages=["eng"],
            extract_images_in_pdf=False,
            infer_table_structure=False,
        )
        text = "\n".join([e.text for e in elements if hasattr(e, 'text') and e.text])
        unstructured_fast_time = time.time() - start
        
        print(f"✅ Unstructured (fast): {unstructured_fast_time:.2f}s, {len(text):,} chars")
        
        # Test hi_res strategy (slow)
        start = time.time()
        elements = partition_pdf(
            filename=str(pdf_file),
            strategy="hi_res",
            languages=["eng"],
            ocr_languages="eng",
            extract_images_in_pdf=False,
            infer_table_structure=False,
        )
        text = "\n".join([e.text for e in elements if hasattr(e, 'text') and e.text])
        unstructured_hires_time = time.time() - start
        
        print(f"⚠️ Unstructured (hi_res): {unstructured_hires_time:.2f}s, {len(text):,} chars")
        
except ImportError:
    print("❌ Unstructured not installed")