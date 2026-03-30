#!/usr/bin/env python3
"""
Test script to verify table extraction is working
Run: python test_fix.py
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append('src')

try:
    from main import MalayalamRAG
    from config import MALAYALAM_DOCS_DIR  # ← ADD THIS IMPORT
    print("✅ Successfully imported MalayalamRAG and config")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_table_extraction():
    """Test if tables are being extracted from PDFs"""
    print("\n" + "="*60)
    print("🔍 TESTING TABLE EXTRACTION")
    print("="*60)
    
    # Initialize RAG
    rag = MalayalamRAG()
    
    # Find PDF files - USE MALAYALAM_DOCS_DIR directly
    pdf_files = list(MALAYALAM_DOCS_DIR.glob("*.pdf"))  # ← CHANGED HERE
    
    if not pdf_files:
        print("❌ No PDF files found in malayalam_docs/")
        return False
    
    print(f"📁 Found {len(pdf_files)} PDF file(s)")
    
    for pdf_file in pdf_files[:1]:  # Test only first PDF
        print(f"\n📄 Testing: {pdf_file.name}")
        print("-" * 40)
        
        try:
            # Test the fixed extraction method
            text = rag._extract_from_pdf_unstructured(pdf_file)
            
            if not text:
                print("❌ No text extracted")
                return False
            
            print(f"✅ Extracted {len(text):,} characters")
            
            # Check for tables
            if "[TABLE" in text:
                table_count = text.count("[TABLE")
                print(f"✅ Found {table_count} tables!")
                
                # Show sample table
                table_start = text.find("[TABLE")
                table_end = text.find("[END TABLE", table_start)
                if table_start != -1 and table_end != -1:
                    table_sample = text[table_start:min(table_end+20, len(text))]
                    print(f"\n📊 Sample table preview:")
                    print(table_sample)
                    if "..." in table_sample:
                        print("...")
            else:
                print("❌ No tables found in extracted text")
                print("\n📝 First 500 characters of extracted text:")
                print(text[:500])
                if len(text) > 500:
                    print("...")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Error during extraction: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_pdfprocessor():
    """Test PDFProcessor class"""
    print("\n" + "="*60)
    print("🔍 TESTING PDFPROCESSOR")
    print("="*60)
    
    try:
        from main import PDFProcessor
        
        pdf_files = list(MALAYALAM_DOCS_DIR.glob("*.pdf"))  # ← CHANGED HERE
        if not pdf_files:
            print("❌ No PDF files found")
            return False
        
        pdf_file = pdf_files[0]
        print(f"📄 Processing: {pdf_file.name}")
        
        extracted_data = PDFProcessor.extract_from_pdf(str(pdf_file))
        
        if not extracted_data:
            print("❌ PDFProcessor.extract_from_pdf returned None")
            return False
        
        tables = extracted_data.get('tables', [])
        print(f"✅ PDFProcessor found {len(tables)} table(s)")
        
        if tables:
            print(f"\n📊 Table details:")
            for i, table in enumerate(tables[:2]):  # Show first 2 tables
                print(f"  Table {i+1}:")
                print(f"    Page: {table.get('page', 'N/A')}")
                print(f"    Size: {table.get('num_rows', 0)}x{table.get('num_cols', 0)}")
                if 'text' in table:
                    preview = table['text'][:100] + "..." if len(table['text']) > 100 else table['text']
                    print(f"    Preview: {preview}")
        
        return len(tables) > 0
        
    except Exception as e:
        print(f"❌ Error testing PDFProcessor: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 RAGtest Table Extraction Test")
    
    # Test 1: MalayalamRAG extraction
    test1_passed = test_table_extraction()
    
    # Test 2: PDFProcessor extraction
    test2_passed = test_pdfprocessor()
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    print(f"Test 1 (MalayalamRAG table extraction): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Test 2 (PDFProcessor table extraction): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! You can now run:")
        print("   1. python src/extract_tables.py --all")
        print("   2. python src/main.py")
    else:
        print("\n⚠️  Some tests failed. Fix the issues before proceeding.")