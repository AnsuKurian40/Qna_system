#!/usr/bin/env python3
"""
Extract tables from PDFs and save them to files
Run: python extract_tables.py
"""

import os
import sys
from pathlib import Path
import json

# Add the current directory to path
sys.path.append('.')

try:
    from main import PDFProcessor
except ImportError:
    print("❌ Cannot import PDFProcessor from main.py")
    sys.exit(1)

def extract_and_save_all_tables():
    """Extract tables from all PDFs and save to files"""
    
    print("🔍 RAGtest - PDF Table Extractor")
    print("="*60)
    
    # Find PDF files
    docs_dir = Path("malayalam_docs")
    if not docs_dir.exists():
        print("❌ malayalam_docs directory not found!")
        print(f"   Looking for: {docs_dir.absolute()}")
        return
    
    pdf_files = list(docs_dir.glob("*.pdf")) + list(docs_dir.glob("*.PDF"))
    if not pdf_files:
        print("❌ No PDF files found in malayalam_docs/")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF file(s):")
    for pdf in pdf_files:
        print(f"   📄 {pdf.name}")
    
    all_tables_summary = []
    
    for pdf_file in pdf_files:
        print(f"\n{'='*60}")
        print(f"📊 Processing: {pdf_file.name}")
        print(f"{'='*60}")
        
        # Extract tables
        extracted_data = PDFProcessor.extract_from_pdf(str(pdf_file))
        
        if not extracted_data:
            print(f"   ❌ Failed to extract data from {pdf_file.name}")
            continue
        
        tables = extracted_data.get('tables', [])
        print(f"   ✅ Extracted {len(tables)} table(s)")
        
        if not tables:
            print(f"   ⚠️  No tables found in {pdf_file.name}")
            continue
        
        # Save tables to files using the new method
        PDFProcessor.save_tables_to_files(extracted_data, pdf_file.name)
        
        # Add to summary
        all_tables_summary.append({
            "pdf_file": pdf_file.name,
            "total_tables": len(tables),
            "pages_processed": extracted_data.get('metadata', {}).get('pages', 0),
            "tables": [
                {
                    "table_id": f"{pdf_file.stem}_table_{i+1}",
                    "page": table.get('page', 'N/A'),
                    "rows": table.get('num_rows', 0),
                    "columns": table.get('num_cols', 0),
                    "text_preview": table.get('text', '')[:100] + "..." if len(table.get('text', '')) > 100 else table.get('text', '')
                }
                for i, table in enumerate(tables)
            ]
        })
    
    # Save global summary
    if all_tables_summary:
        tables_dir = Path("extracted_tables")
        summary_file = tables_dir / "ALL_TABLES_SUMMARY.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(all_tables_summary, f, ensure_ascii=False, indent=2)
        
        total_tables = sum(item['total_tables'] for item in all_tables_summary)
        
        print(f"\n{'='*60}")
        print("📊 EXTRACTION COMPLETE")
        print(f"{'='*60}")
        print(f"📁 Tables saved to: extracted_tables/")
        print(f"📋 Summary file: {summary_file}")
        print(f"📊 Total tables extracted: {total_tables}")
        print(f"{'='*60}")
    else:
        print("\n❌ No tables were extracted from any PDF")

def extract_specific_pdf(pdf_filename):
    """Extract tables from a specific PDF file"""
    
    pdf_path = Path("malayalam_docs") / pdf_filename
    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
        print("Available PDFs:")
        docs_dir = Path("malayalam_docs")
        if docs_dir.exists():
            for pdf in docs_dir.glob("*.pdf"):
                print(f"  - {pdf.name}")
        return
    
    print(f"\n🔍 Extracting tables from: {pdf_filename}")
    print("="*60)
    
    extracted_data = PDFProcessor.extract_from_pdf(str(pdf_path))
    
    if not extracted_data:
        print("❌ Extraction failed")
        return
    
    tables = extracted_data.get('tables', [])
    print(f"✅ Found {len(tables)} table(s)")
    
    # Save to files
    PDFProcessor.save_tables_to_files(extracted_data, pdf_filename)
    
    # Display table previews
    for i, table in enumerate(tables):
        print(f"\n📊 Table {i+1}:")
        print(f"   Page: {table.get('page', 'N/A')}")
        print(f"   Size: {table.get('num_rows', 0)} rows × {table.get('num_cols', 0)} columns")
        
        # Show first few rows
        table_text = table.get('text', '')
        if table_text:
            lines = table_text.split('\n')
            print("   First 3 rows:")
            for j, line in enumerate(lines[:3]):
                print(f"     {line}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract tables from PDFs in RAGtest project')
    parser.add_argument('--pdf', type=str, help='Extract from specific PDF file (e.g., History.pdf)')
    parser.add_argument('--all', action='store_true', help='Extract from all PDFs (default)')
    
    args = parser.parse_args()
    
    if args.pdf:
        extract_specific_pdf(args.pdf)
    else:
        extract_and_save_all_tables()