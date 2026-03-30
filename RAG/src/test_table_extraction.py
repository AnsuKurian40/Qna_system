#!/usr/bin/env python3
"""
Simple table extraction without image processing errors
"""

import os
import sys
from pathlib import Path
import json

# Add to path
sys.path.append('.')

try:
    from main import PDFProcessor
except ImportError:
    print("❌ Cannot import PDFProcessor")
    sys.exit(1)

def simple_pdf_extraction(pdf_path):
    """Extract only text and tables from PDF"""
    try:
        from unstructured.partition.pdf import partition_pdf
        
        print(f"📄 Processing: {os.path.basename(pdf_path)}")
        
        # SIMPLE EXTRACTION - no images, no temp files
        elements = partition_pdf(
            filename=pdf_path,
            strategy="auto",  # Auto chooses best strategy
            languages=["eng"],  # Just English for now
            extract_images_in_pdf=False,
            infer_table_structure=True,
            extract_image_block_types=[],  # No images
            extract_image_block_to_payload=False,
            extract_image_block_output_dir=None,  # No output directory
            max_partition=500,
        )
        
        tables = []
        text_parts = []
        
        for elem in elements:
            elem_type = getattr(elem, 'category', 'Unknown')
            
            if elem_type == "Table":
                table_text = elem.text.strip()
                if table_text:
                    metadata = elem.metadata.to_dict() if hasattr(elem, 'metadata') else {}
                    tables.append({
                        'page': metadata.get('page_number', 1),
                        'text': table_text,
                        'num_rows': len([r for r in table_text.split('\n') if r.strip()])
                    })
            
            elif elem_type in ["Title", "NarrativeText"]:
                text = elem.text.strip()
                if text:
                    text_parts.append(text)
        
        print(f"   ✅ Found {len(tables)} tables, {len(text_parts)} text blocks")
        return tables, text_parts
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return [], []

def save_tables_simple(pdf_filename, tables):
    """Save tables in a simple format"""
    if not tables:
        print(f"   No tables to save from {pdf_filename}")
        return
    
    # Create output directory
    output_dir = Path("extracted_tables_simple")
    output_dir.mkdir(exist_ok=True)
    
    base_name = pdf_filename.replace('.pdf', '').replace('.PDF', '')
    
    # Save each table
    for i, table in enumerate(tables, 1):
        # Save as TXT
        txt_file = output_dir / f"{base_name}_table_{i}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"Source: {pdf_filename}\n")
            f.write(f"Table: {i}\n")
            f.write(f"Page: {table.get('page', 'N/A')}\n")
            f.write(f"Rows: {table.get('num_rows', 0)}\n")
            f.write("="*60 + "\n\n")
            f.write(table.get('text', ''))
        
        # Save as Markdown table
        md_file = output_dir / f"{base_name}_table_{i}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# Table {i} from {pdf_filename}\n\n")
            f.write(f"Page: {table.get('page', 'N/A')}\n\n")
            
            table_text = table.get('text', '')
            if table_text:
                lines = table_text.split('\n')
                for line in lines:
                    # Convert pipe-separated to markdown
                    cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                    if cells:
                        f.write("| " + " | ".join(cells) + " |\n")
                        if i == 1 and line == lines[0]:  # Add header separator for first row
                            f.write("|" + "---|" * len(cells) + "\n")
    
    # Save summary
    summary_file = output_dir / f"{base_name}_summary.json"
    summary = {
        "pdf_file": pdf_filename,
        "total_tables": len(tables),
        "tables": [
            {
                "table_number": i,
                "page": table.get('page', 'N/A'),
                "rows": table.get('num_rows', 0),
                "preview": table.get('text', '')[:100] + "..." if len(table.get('text', '')) > 100 else table.get('text', '')
            }
            for i, table in enumerate(tables, 1)
        ]
    }
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"   💾 Saved {len(tables)} tables to {output_dir}/")

def main():
    """Main function"""
    print("🔧 Simple Table Extractor")
    print("="*60)
    
    # Find PDFs
    docs_dir = Path("malayalam_docs")
    if not docs_dir.exists():
        print(f"❌ Directory not found: {docs_dir}")
        return
    
    pdf_files = list(docs_dir.glob("*.pdf"))
    if not pdf_files:
        print("❌ No PDF files found")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s):")
    for pdf in pdf_files:
        print(f"  - {pdf.name}")
    
    # Process each PDF
    all_results = []
    
    for pdf_file in pdf_files:
        print(f"\n{'='*60}")
        print(f"Processing: {pdf_file.name}")
        
        # Use simple extraction
        tables, text_blocks = simple_pdf_extraction(str(pdf_file))
        
        if tables:
            print(f"✅ Extracted {len(tables)} tables")
            save_tables_simple(pdf_file.name, tables)
            
            # Add to results
            all_results.append({
                "file": pdf_file.name,
                "tables": len(tables),
                "text_blocks": len(text_blocks)
            })
        else:
            print(f"⚠️  No tables found")
    
    # Final summary
    if all_results:
        print(f"\n{'='*60}")
        print("📊 EXTRACTION SUMMARY")
        print(f"{'='*60}")
        
        total_tables = sum(r["tables"] for r in all_results)
        
        for result in all_results:
            print(f"📄 {result['file']}: {result['tables']} tables")
        
        print(f"\n📊 Total tables extracted: {total_tables}")
        print(f"📁 Output folder: extracted_tables_simple/")
        
        # Save overall summary
        summary_file = Path("extracted_tables_simple") / "OVERALL_SUMMARY.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        print(f"📋 Summary saved to: {summary_file}")
    else:
        print("\n❌ No tables extracted from any PDF")

if __name__ == "__main__":
    main()