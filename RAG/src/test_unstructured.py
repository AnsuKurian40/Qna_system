# test_unstructured.py
try:
    from unstructured.partition.pdf import partition_pdf
    print("✅ Unstructured installed successfully!")
    
    # Check available languages
    import pytesseract
    langs = pytesseract.get_languages(config='')
    print(f"✅ Tesseract languages: {langs}")
    
    if 'mal' in langs:
        print("✅ Malayalam OCR supported!")
    else:
        print("⚠️ Malayalam language not found in Tesseract")
        print("Download mal.traineddata and add to tessdata folder")
        
except ImportError as e:
    print(f"❌ Error: {e}")
    print("Install with: pip install 'unstructured[pdf,ocr]'")