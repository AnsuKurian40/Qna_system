#!/usr/bin/env python3
"""
Malayalam RAG System with BATCHED INDEXING for BGE-M3
For RAGtest project
Run: python src/main.py

UPDATED: Uses Unstructured.io for Malayalam OCR in PDFs
UPDATED: Shows only exact pages where answer came from, not just first 3 chunks
"""

import os
import sys
from pathlib import Path
from docx import Document
import chromadb
from chromadb.utils import embedding_functions
import google.generativeai as genai
import time
import re

# ========== UNSTRUCTURED FOR MALAYALAM OCR ==========
import tempfile
import base64
import json
# ====================================================

# Add src to path
sys.path.append(str(Path(__file__).parent))

poppler_bin = r"C:\Users\ansuk\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"
if os.path.exists(poppler_bin):
    os.environ['PATH'] = poppler_bin + ';' + os.environ['PATH']
    print(f"✅ Added Poppler to PATH: {poppler_bin}")
else:
    print(f"❌ Poppler not found at: {poppler_bin}")
    sys.exit(1)

# Import config
try:
    from config import *
except ImportError:
    print("❌ Error: Cannot find config.py")
    sys.exit(1)

print(f"🔧 Loading configuration from: {BASE_DIR}")

class MalayalamRAG:
    def __init__(self):
        """Initialize the RAG system"""
        print("="*60)
        print("🚀 Initializing Malayalam RAG System for RAGtest")
        print("="*60)
        
        # Check for documents
        self.check_documents()
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
        
        # Setup embedding function
        self.embedding_func = embedding_functions.OllamaEmbeddingFunction(
            url="http://localhost:11434/api/embeddings",
            model_name=EMBEDDING_MODEL
        )
        
        # Get collection
        self.collection = self.client.get_or_create_collection(
            name="malayalam_documents",
            embedding_function=self.embedding_func
        )
        
        print(f"✅ Vector DB initialized at: {VECTOR_DB_DIR}")
    
    def check_documents(self):
        """Check if documents exist - includes PDFs"""
        print(f"\n📁 Checking documents in: {MALAYALAM_DOCS_DIR}")
        
        if not MALAYALAM_DOCS_DIR.exists():
            print(f"❌ Directory not found!")
            print(f"   Please create: {MALAYALAM_DOCS_DIR}")
            sys.exit(1)
        
        # Check for both DOCX and PDF files
        docx_files = list(MALAYALAM_DOCS_DIR.glob("*.docx"))
        pdf_files = list(MALAYALAM_DOCS_DIR.glob("*.pdf"))
        
        print(f"✅ Found {len(docx_files)} .docx file(s) and {len(pdf_files)} .pdf file(s):")
        
        for doc_file in docx_files:
            print(f"   📝 {doc_file.name}")
        
        for pdf_file in pdf_files:
            print(f"   📄 {pdf_file.name}")
        
        if not docx_files and not pdf_files:
            print(f"❌ No documents found!")
            print(f"   Please add Malayalam Word/PDF documents to: {MALAYALAM_DOCS_DIR}")
            sys.exit(1)
        
        return docx_files + pdf_files
    
    def extract_text(self, filepath):
        """Extract text from .docx or .pdf file using Unstructured for PDFs"""
        try:
            if str(filepath).lower().endswith('.pdf'):
                # Use Unstructured for PDF with Malayalam OCR
                return self._extract_from_pdf_unstructured(filepath)
            else:
                # Existing DOCX extraction
                doc = Document(filepath)
                paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
                
                if not paragraphs:
                    print(f"   ⚠️  No text found in {filepath.name}")
                    return ""
                
                text = "\n".join(paragraphs)
                print(f"   Extracted {len(text):,} characters from {filepath.name}")
                
                # For DOCX files, we need to track page numbers (approximate)
                # Assuming roughly 300 words per page
                words_per_page = 300
                total_words = len(text.split())
                total_pages = max(1, (total_words + words_per_page - 1) // words_per_page)
                
                # Return text with page markers for DOCX
                return {
                    'text': text,
                    'pages': self._approximate_docx_pages(text, total_pages),
                    'file_type': 'DOCX'
                }
                
        except Exception as e:
            print(f"   ❌ Error reading {filepath.name}: {e}")
            return ""
    
    def _approximate_docx_pages(self, text, total_pages):
        """Approximate page divisions for DOCX files"""
        words = text.split()
        if not words:
            return {}
        
        words_per_page = len(words) // total_pages
        pages = {}
        
        for page_num in range(1, total_pages + 1):
            start_idx = (page_num - 1) * words_per_page
            end_idx = page_num * words_per_page if page_num < total_pages else len(words)
            page_words = words[start_idx:end_idx]
            pages[page_num] = " ".join(page_words)
        
        return pages
    
    def _extract_from_pdf_unstructured(self, pdf_path):
        """Extract text from PDF using Unstructured with Malayalam OCR and page numbers"""
        try:
            print(f"   📄 Processing PDF with Unstructured (Malayalam OCR): {pdf_path.name}")
            
            # Import here to avoid dependency issues
            from unstructured.partition.pdf import partition_pdf
            
            # Extract with Malayalam OCR and page numbers
            elements = partition_pdf(
                filename=str(pdf_path),
                strategy="hi_res",          # Uses OCR for scanned PDFs
                languages=["mal", "eng"],   # Malayalam + English
                ocr_languages="mal+eng",    # OCR both languages
                extract_images_in_pdf=False,  # Don't extract images for indexing
                infer_table_structure=True,  # Extract tables
                max_partition=1500,
                include_page_breaks=True,    # Include page breaks to track pages
                extract_element_types=["Title", "NarrativeText", "Table"],
            )
            
            # Group text by page number
            pages = {}
            text_parts = []
            
            for elem in elements:
                if hasattr(elem, 'text') and elem.text.strip():
                    text = elem.text.strip()
                    
                    # Get page number from metadata
                    page_num = 1
                    if hasattr(elem, 'metadata') and elem.metadata:
                        page_num = getattr(elem.metadata, 'page_number', 1)
                    
                    # Store in pages dictionary
                    if page_num not in pages:
                        pages[page_num] = []
                    pages[page_num].append(text)
                    
                    # Also store in flat list with page marker
                    text_parts.append(f"[Page {page_num}] {text}")
            
            # Combine text with page markers
            combined_text = "\n\n".join(text_parts)
            
            # Combine pages into single strings per page
            page_contents = {}
            for page_num, page_texts in pages.items():
                page_contents[page_num] = " ".join(page_texts)
            
            print(f"   ✅ Extracted {len(combined_text):,} characters from {len(pages)} pages with Malayalam OCR")
            
            return {
                'text': combined_text,
                'pages': page_contents,
                'file_type': 'PDF'
            }
            
        except ImportError as e:
            print(f"   ❌ Unstructured not installed. Install with: pip install 'unstructured[pdf,ocr]'")
            return ""
        except Exception as e:
            print(f"   ❌ Error extracting from PDF {pdf_path.name}: {e}")
            return ""
    
    def chunk_text(self, extracted_data):
        """
        Word-based chunking with overlap, preserving page numbers.
        Each chunk contains CHUNK_SIZE words.
        Consecutive chunks overlap by CHUNK_OVERLAP words.
        """
        if not extracted_data or not extracted_data.get('text'):
            return [], []
        
        text = extracted_data['text']
        pages = extracted_data.get('pages', {})
        file_type = extracted_data.get('file_type', 'UNKNOWN')
        
        if not text or not text.strip():
            return [], []
        
        # If we have page information, use it to create chunks with page metadata
        if pages:
            chunks = []
            page_numbers = []  # Track which page each chunk belongs to
            
            # Process each page separately
            for page_num, page_text in pages.items():
                if not page_text.strip():
                    continue
                
                page_words = page_text.split()
                start = 0
                total_words = len(page_words)
                
                while start < total_words:
                    end = start + CHUNK_SIZE
                    chunk_words = page_words[start:end]
                    chunk = " ".join(chunk_words)
                    
                    # Only add non-empty chunks
                    if chunk.strip():
                        chunks.append(chunk)
                        page_numbers.append(page_num)
                    
                    # Move start forward with overlap
                    start += (CHUNK_SIZE - CHUNK_OVERLAP)
            
            return chunks, page_numbers
        else:
            # Fallback to old method without page numbers
            words = text.split()
            chunks = []
            page_numbers = []  # Will be empty for DOCX without page tracking
            
            start = 0
            total_words = len(words)
            
            while start < total_words:
                end = start + CHUNK_SIZE
                chunk_words = words[start:end]
                chunk = " ".join(chunk_words)
                
                if chunk.strip():
                    chunks.append(chunk)
                    page_numbers.append(1)  # Default page 1
                
                start += (CHUNK_SIZE - CHUNK_OVERLAP)
            
            return chunks, page_numbers
    
    def index_documents(self):
        """Index all documents with batching to prevent timeouts"""
        print(f"\n📄 Checking existing index...")
        
        if self.collection.count() > 0:
            count = self.collection.count()
            print(f"✅ Already indexed: {count} chunks")
            print("   To re-index, delete the 'vector_db' folder")
            return True
        
        print("No existing index found. Creating new index (this will take 10-15 minutes)...")
        
        docx_files = list(MALAYALAM_DOCS_DIR.glob("*.docx"))
        pdf_files = list(MALAYALAM_DOCS_DIR.glob("*.pdf"))
        all_files = docx_files + pdf_files
        
        print(f"\nIndexing {len(all_files)} document(s)...")
        
        total_chunks_added = 0
        failed_batches = 0
        
        # Process ONE DOCUMENT at a time
        for doc_idx, doc_file in enumerate(all_files, 1):
            print(f"\n{'='*60}")
            file_type = "PDF" if str(doc_file).lower().endswith('.pdf') else "DOCX"
            print(f"📄 {file_type} DOCUMENT {doc_idx}/{len(all_files)}: {doc_file.name}")
            print(f"{'='*60}")
            
            # Extract text (handles both DOCX and PDF)
            extracted_data = self.extract_text(doc_file)
            
            if not extracted_data:
                print(f"   ⚠️  Skipping (no text extracted)")
                continue
            
            # Create chunks with page numbers
            chunks, page_numbers = self.chunk_text(extracted_data)
            
            if not chunks:
                print(f"   ⚠️  No chunks created")
                continue
            
            print(f"   📊 Created {len(chunks)} chunks from {len(set(page_numbers))} pages")
            
            # Process in BATCHES (BGE-M3 needs this!)
            BATCH_SIZE = 15  # Process 15 chunks at a time
            total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE
            
            print(f"   ⏳ Processing in {total_batches} batches of {BATCH_SIZE}...")
            
            for batch_idx in range(0, len(chunks), BATCH_SIZE):
                batch_end = min(batch_idx + BATCH_SIZE, len(chunks))
                batch_chunks = chunks[batch_idx:batch_end]
                batch_page_nums = page_numbers[batch_idx:batch_end]
                batch_num = (batch_idx // BATCH_SIZE) + 1
                
                # Prepare this batch with page numbers in metadata
                batch_metadata = []
                batch_ids = []
                
                for i in range(len(batch_chunks)):
                    batch_metadata.append({
                        "source": doc_file.name,
                        "file_type": file_type,
                        "chunk_idx": batch_idx + i,
                        "total_chunks": len(chunks),
                        "doc_index": doc_idx,
                        "batch": batch_num,
                        "page_number": batch_page_nums[i]  # Store page number in metadata
                    })
                    batch_ids.append(f"{file_type.lower()}{doc_idx}_ch{batch_idx + i:04d}")
                
                # Try to add this batch (with retry logic)
                max_retries = 2
                for retry in range(max_retries):
                    try:
                        start_time = time.time()
                        
                        print(f"   🔄 Batch {batch_num}/{total_batches}: Adding {len(batch_chunks)} chunks...", end="", flush=True)
                        
                        self.collection.add(
                            documents=batch_chunks,
                            metadatas=batch_metadata,
                            ids=batch_ids
                        )
                        
                        elapsed = time.time() - start_time
                        print(f" ✅ ({elapsed:.1f}s)")
                        
                        total_chunks_added += len(batch_chunks)
                        
                        # Small delay between batches
                        if batch_end < len(chunks):
                            time.sleep(0.5)
                        
                        break  # Success, exit retry loop
                        
                    except Exception as e:
                        if retry < max_retries - 1:
                            wait_time = (retry + 1) * 5
                            print(f" ❌ Failed. Retry {retry+1} in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            print(f" ❌ Permanent fail: {str(e)[:80]}")
                            failed_batches += 1
            
            print(f"   ✅ Document complete: {len(chunks)} chunks indexed")
        
        # Final summary
        print(f"\n{'='*60}")
        print("📊 INDEXING COMPLETE")
        print(f"{'='*60}")
        print(f"   Documents processed:    {len(all_files)}")
        print(f"   Total chunks indexed:   {total_chunks_added}")
        print(f"   Failed batches:         {failed_batches}")
        if total_chunks_added + failed_batches * BATCH_SIZE > 0:
            success_rate = (total_chunks_added / (total_chunks_added + failed_batches * BATCH_SIZE)) * 100
            print(f"   Success rate:           {success_rate:.1f}%")
        print(f"   Vector DB location:     {VECTOR_DB_DIR}")
        print(f"{'='*60}")
        
        if total_chunks_added > 0:
            return True
        else:
            print("❌ No chunks could be indexed!")
            return False
    
    def ask_question(self, question):
        """Ask a question and get answer with page numbers"""
        print(f"\n" + "="*60)
        print(f"❓ QUESTION: {question}")
        print("="*60)
        
        # Step 1: Retrieve relevant chunks
        print("\n🔍 Step 1: Searching vector database...")
        results = self.collection.query(
            query_texts=[question],
            n_results=TOP_K_RESULTS
        )
        
        # DEBUG: Show what was retrieved
        if results['documents'] and results['documents'][0]:
            print(f"✅ Found {len(results['documents'][0])} relevant chunks")
            
            print("\n📄 Retrieved chunks:")
            for i, (chunk, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                source_type = metadata.get('file_type', 'DOCX')
                page_num = metadata.get('page_number', 'N/A')
                print(f"\n  Chunk {i+1} (from: {metadata['source']} [{source_type}] - Page {page_num}):")
                print(f"    {chunk[:150]}..." if len(chunk) > 150 else f"    {chunk}")
        else:
            print("❌ No relevant chunks found!")
            return "നൽകിയിട്ടുള്ള പാഠ്യപദ്ധതി പ്രകാരം ഈ ചോദ്യത്തിനുള്ള ഉത്തരം അതിൽ നിന്ന് ലഭ്യമല്ല."
        
        # Prepare context with page numbers - include ALL retrieved chunks
        context_chunks = results['documents'][0]
        metadatas = results['metadatas'][0]
        
        # Build context with page references for ALL chunks
        context_with_pages = []
        
        for i, (chunk, metadata) in enumerate(zip(context_chunks, metadatas)):
            page_num = metadata.get('page_number', 'N/A')
            source = metadata.get('source', 'Unknown')
            context_with_pages.append(f"[From {source}, page {page_num}]: {chunk}")
        
        context = "\n\n".join(context_with_pages)
        
        # Step 2: Generate answer using Gemini
        print(f"\n🤖 Step 2: Generating answer with Gemini...")
        
        if not GEMINI_API_KEY:
            print("❌ Gemini API key not set!")
            print("   Run: set GEMINI_API_KEY=your_key_here")
            return "Gemini API കീ ലഭ്യമല്ല."
        
        try:
            # Configure Gemini
            genai.configure(api_key=GEMINI_API_KEY)
            
            # Create model instance
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Create Malayalam prompt that asks for natural answers WITHOUT page number phrases
            # AND asks Gemini to identify which chunks were actually used
            malayalam_prompt = f"""ഈ വിവരങ്ങൾ ഉപയോഗിച്ച് മാത്രം ചോദ്യത്തിന് ഉത്തരം നൽകുക.

വിവരങ്ങൾ:
{context}

ചോദ്യം: {question}

പ്രധാന നിർദ്ദേശങ്ങൾ:
1. വിവരങ്ങളിൽ നിന്ന് നേരിട്ട് ഉത്തരം നൽകുക
2. നിങ്ങളുടെ ഉത്തരത്തിൽ "പേജ് X ൽ പറയുന്നത്" എന്ന പോലുള്ള വാചകങ്ങൾ ഉൾപ്പെടുത്തരുത്
3. സ്വാഭാവികമായ മലയാളത്തിൽ മാത്രം ഉത്തരം എഴുതുക
4. വിവരങ്ങൾ പര്യാപ്തമല്ലെങ്കിൽ, "ഈ വിവരങ്ങളിൽ ഉത്തരം ഇല്ല" എന്ന് പറയുക

നിങ്ങളുടെ ഉത്തരത്തിന് ശേഷം, ഒരു പ്രത്യേക വരിയിൽ "USED_SOURCES:" എന്നെഴുതി തുടർന്ന് നിങ്ങൾ ഉത്തരത്തിനായി ഉപയോഗിച്ച വിവരങ്ങളുടെ സ്രോതസ്സുകളുടെ പട്ടിക നൽകുക. ഓരോ സ്രോതസ്സും [ഫയൽനാമം: പേജ് നമ്പർ] എന്ന ഫോർമാറ്റിൽ നൽകുക. ഉദാഹരണം: USED_SOURCES: [History.pdf: 8] [History.pdf: 24]

ഉത്തരം:"""
            
            # CRITICAL: Add delay to avoid rate limits
            time.sleep(4)
            
            print("   Sending request to Gemini API...")
            response = model.generate_content(
                malayalam_prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 1500,
                }
            )
            
            if response.text:
                response_text = response.text.strip()
                print(f"✅ Answer generated successfully")
                
                # Parse the response to separate answer and used sources
                if "USED_SOURCES:" in response_text:
                    parts = response_text.split("USED_SOURCES:")
                    answer = parts[0].strip()
                    sources_part = parts[1].strip()
                    
                    # Extract used sources using regex
                    used_sources = []
                    # Find all [filename: page] patterns
                    source_matches = re.findall(r'\[([^\]]+):\s*(\d+)\]', sources_part)
                    
                    for match in source_matches:
                        source_file = match[0].strip()
                        page_num = match[1].strip()
                        used_sources.append((source_file, page_num))
                    
                    # If no sources found with regex, try to parse line by line
                    if not used_sources:
                        lines = sources_part.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line and ':' in line:
                                parts = line.split(':', 1)
                                if len(parts) == 2:
                                    source_file = parts[0].strip().strip('[]')
                                    page_info = parts[1].strip()
                                    # Extract just the number
                                    page_match = re.search(r'\d+', page_info)
                                    if page_match:
                                        used_sources.append((source_file, page_match.group()))
                else:
                    # Fallback if model doesn't follow format - use all chunks
                    print("   ⚠️ Model didn't specify used sources, showing all retrieved chunks")
                    answer = response_text
                    used_sources = [(metadata.get('source', 'Unknown'), str(metadata.get('page_number', 'N/A'))) 
                                   for metadata in metadatas]
                
                # Group used sources by document name
                source_dict = {}
                for source_file, page_num in used_sources:
                    if source_file not in source_dict:
                        source_dict[source_file] = []
                    if page_num not in source_dict[source_file]:
                        source_dict[source_file].append(page_num)
                
                # Format sources with grouped page numbers
                sources_text_parts = []
                for source, page_numbers in source_dict.items():
                    # Sort page numbers numerically
                    try:
                        page_numbers.sort(key=int)
                    except ValueError:
                        page_numbers.sort()
                    
                    if len(page_numbers) == 1:
                        sources_text_parts.append(f"{source}: page {page_numbers[0]}")
                    else:
                        pages_str = ", ".join(page_numbers)
                        sources_text_parts.append(f"{source}: pages {pages_str}")
                
                sources_text = ", ".join(sources_text_parts)
                
                # Display source summary
                print("\n📚 Sources Actually Used:")
                for source, page_numbers in source_dict.items():
                    if len(page_numbers) == 1:
                        print(f"   • {source} (Page {page_numbers[0]})")
                    else:
                        pages_str = ", ".join(page_numbers)
                        print(f"   • {source} (Pages {pages_str})")
                
                return f"{answer}\n\n**Source(s):** {sources_text}"
            else:
                print("❌ Gemini returned empty response")
                return "Gemini-ന് ഉത്തരം നൽകാനായില്ല."
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gemini API error: {error_msg[:100]}")
            
            if "429" in error_msg or "quota" in error_msg:
                return "API ക്വോട്ട പൂർത്തിയായി. കുറച്ച് നിമിഷങ്ങൾക്ക് ശേഷം വീണ്ടും ശ്രമിക്കുക."
            elif "safety" in error_msg.lower():
                return "സുരക്ഷാ നിയന്ത്രണങ്ങൾ കാരണം ഉത്തരം നൽകാനായില്ല."
            else:
                return f"Gemini API പിശക്: {error_msg[:100]}"
    
    def save_answer(self, question, answer):
        """Save Q&A to file with page number information"""
        with open(ANSWERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Question: {question}\n")
            f.write(f"Answer: {answer}\n")
            f.write(f"{'='*60}\n\n")

class PDFProcessor:
    """PDF processor using Unstructured.io for Malayalam OCR"""
    
    @staticmethod
    def extract_from_pdf(pdf_path):
        """Extract text, tables, and images from PDF using Unstructured"""
        try:
            # Import here to avoid dependency issues
            from unstructured.partition.pdf import partition_pdf
            import base64
            import os
            
            print(f"🔍 Processing PDF with Unstructured: {os.path.basename(pdf_path)}")
            
            extracted_data = {
                'text': '',
                'tables': [],
                'images': [],
                'metadata': {},
                'pages': []
            }
            
            # Create temp directory for images
            temp_img_dir = tempfile.mkdtemp()
            
            # Extract with Unstructured
            elements = partition_pdf(
                filename=pdf_path,
                strategy="hi_res",
                languages=["mal", "eng"],
                ocr_languages="mal+eng",
                extract_images_in_pdf=True,
                infer_table_structure=True,
                extract_image_block_output_dir=temp_img_dir,
                extract_image_block_types=["Image", "Table"],
                max_partition=1000,
                include_page_breaks=True,
            )
            
            # Process elements
            text_parts = []
            table_counter = 0
            image_counter = 0
            pages_dict = {}
            
            for elem in elements:
                elem_type = getattr(elem, 'category', 'Unknown')
                metadata = elem.metadata.to_dict() if hasattr(elem, 'metadata') else {}
                page_num = metadata.get('page_number', 1)
                
                # Initialize page in dict
                if page_num not in pages_dict:
                    pages_dict[page_num] = []
                
                # Text content
                if elem_type in ["Title", "NarrativeText", "ListItem", "UncategorizedText"]:
                    text = elem.text.strip()
                    if text:
                        text_parts.append(f"--- Page {page_num} ---\n{text}")
                        pages_dict[page_num].append(text)
                
                # Tables
                elif elem_type == "Table":
                    table_counter += 1
                    table_text = elem.text.strip()
                    rows = [row.split('|') for row in table_text.split('\n') if row.strip()]
                    
                    table_data = {
                        'id': f'table_{table_counter}',
                        'page': page_num,
                        'table_num': table_counter,
                        'text': table_text,
                        'rows': rows,
                        'num_rows': len(rows),
                        'num_cols': len(rows[0]) if rows else 0,
                        'html': PDFProcessor._convert_table_to_html(table_text)
                    }
                    extracted_data['tables'].append(table_data)
                    text_parts.append(f"\n[Table {table_counter} on page {page_num}]:\n{table_text}")
                    pages_dict[page_num].append(f"[Table {table_counter}]: {table_text}")
                
                # Images
                elif elem_type == "Image":
                    image_counter += 1
                    # Check for image file
                    img_files = [f for f in os.listdir(temp_img_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
                    
                    for img_file in img_files:
                        img_path = os.path.join(temp_img_dir, img_file)
                        if os.path.exists(img_path):
                            with open(img_path, 'rb') as f:
                                img_base64 = base64.b64encode(f.read()).decode('utf-8')
                            
                            image_data = {
                                'id': f'image_{image_counter}',
                                'page': page_num,
                                'base64': img_base64,
                                'width': metadata.get('width', 300),
                                'height': metadata.get('height', 200)
                            }
                            extracted_data['images'].append(image_data)
                            break
            
            # Combine all text
            extracted_data['text'] = '\n\n'.join(text_parts)
            
            # Add page contents
            extracted_data['pages'] = {page: "\n".join(content) for page, content in pages_dict.items()}
            
            # Add metadata
            extracted_data['metadata'] = {
                'pages': max([getattr(elem.metadata, 'page_number', 0) for elem in elements 
                            if hasattr(elem, 'metadata')], default=0),
                'tables_extracted': table_counter,
                'images_extracted': image_counter,
                'language': 'Malayalam+English',
                'ocr_used': True
            }
            
            # Clean up temp directory
            import shutil
            shutil.rmtree(temp_img_dir, ignore_errors=True)
            
            print(f"✅ Extracted: {len(text_parts)} text blocks, {table_counter} tables, {image_counter} images")
            return extracted_data
            
        except ImportError:
            print("❌ Unstructured not installed. Install with: pip install 'unstructured[pdf,ocr]'")
            return None
        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
            return None
    
    @staticmethod
    def _convert_table_to_html(table_text):
        """Convert table text to HTML"""
        if not table_text:
            return ""
        
        lines = [line.strip() for line in table_text.split('\n') if line.strip()]
        if not lines:
            return ""
        
        html = '<table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0;">\n'
        
        for i, line in enumerate(lines):
            html += '  <tr>\n'
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            tag = 'th' if i == 0 else 'td'
            
            for cell in cells:
                cell_clean = cell.strip()
                html += f'    <{tag} style="padding: 8px; border: 1px solid #ddd;">{cell_clean}</{tag}>\n'
            
            html += '  </tr>\n'
        
        html += '</table>'
        return html
    
    @staticmethod
    def simple_search(pdf_data, question):
        """Simple search in PDF content"""
        if not pdf_data or not pdf_data.get('text'):
            return "പിഡിഎഫിൽ നിന്ന് വിവരങ്ങൾ ലഭിച്ചിട്ടില്ല."
        
        question_lower = question.lower()
        
        # Search with page numbers
        for page_num, page_text in pdf_data.get('pages', {}).items():
            if question_lower in page_text.lower():
                # Find the specific line
                lines = page_text.split('\n')
                for line in lines:
                    if question_lower in line.lower():
                        return f"**പേജ് {page_num} ൽ കണ്ടെത്തിയ വിവരം:**\n\n{line}"
        
        # Search in tables
        for table in pdf_data.get('tables', []):
            for row in table.get('rows', []):
                for cell in row:
                    cell_str = str(cell).lower() if cell else ""
                    if question_lower in cell_str:
                        return f"**ടേബിളിൽ കണ്ടെത്തിയ വിവരം (പേജ് {table['page']}):**\n\n{cell}"
        
        return "ഈ ചോദ്യത്തിനുള്ള ഉത്തരം പിഡിഎഫിൽ നിന്ന് ലഭിച്ചിട്ടില്ല."

def check_ollama():
    """Check if Ollama is running (for embeddings)"""
    try:
        import subprocess
        result = subprocess.run(["ollama", "list"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Ollama is running")
            return True
        else:
            print("❌ Ollama is not responding")
            return False
    except:
        print("❌ Cannot check Ollama status")
        return False

def check_unstructured():
    """Check if Unstructured is installed"""
    try:
        from unstructured.partition.pdf import partition_pdf
        print("✅ Unstructured is installed")
        return True
    except ImportError:
        print("❌ Unstructured not installed")
        print("   Install with: pip install 'unstructured[pdf,ocr]'")
        return False

def main():
    """Main function"""
    
    print("\n" + "="*60)
    print("🔧 SYSTEM CHECK FOR RAGtest PROJECT")
    print("="*60)
    
    # Check Ollama
    if not check_ollama():
        print("\n❌ Ollama is not running!")
        print("   Please start it in another terminal:")
        print("   $ ollama serve")
        sys.exit(1)
    
    # Check Unstructured
    if not check_unstructured():
        print("\n⚠️  Unstructured not installed - PDF OCR will not work")
        print("   Install with: pip install 'unstructured[pdf,ocr]'")
    
    # Check Gemini API key
    if not GEMINI_API_KEY:
        print("\n⚠️  GEMINI_API_KEY not found in environment")
        print("   Set it with: set GEMINI_API_KEY=your_key_here")
    
    # Initialize RAG
    rag = MalayalamRAG()
    
    # Index documents if needed
    if not rag.index_documents():
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🤖 MALAYALAM RAG SYSTEM READY")
    print("="*60)
    print("\nCommands:")
    print("  - Type your question in Malayalam")
    print("  - Type 'quit' or 'exit' to end")
    print("  - All answers saved to 'answers.txt'")
    print("  - Shows only exact pages where answer came from")
    print("="*60 + "\n")
    
    # Interactive loop
    while True:
        try:
            question = input("❓ ചോദ്യം: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q', 'അവസാനിപ്പിക്കുക']:
                print("\n👋 നന്ദി!")
                break
            
            if not question:
                continue
            
            # Get answer
            answer = rag.ask_question(question)
            
            # Save to file
            rag.save_answer(question, answer)
            
            # Display answer
            print("\n" + "="*60)
            print("💡 ANSWER:")
            print("="*60)
            print(answer)
            print("="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 പ്രോഗ്രാം നിർത്തി!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()