# app.py
import streamlit as st
import sys
import os
from pathlib import Path
import time
import tempfile

# ========== ADD THESE IMPORTS ==========
import base64
import pandas as pd
# =======================================

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import your MalayalamRAG class
from main import MalayalamRAG, PDFProcessor

# Set page config
st.set_page_config(
    page_title="Malayalam Document Question Answering",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Malayalam font and better styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Malayalam:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans Malayalam', sans-serif;
}

.main {
    background-color: #ffffff;
}

h1, h2, h3 {
    color: #1f2937;
    font-weight: 600;
}

.section-box {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.question {
    color: #111827;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.answer {
    color: #1f2937;
    line-height: 1.7;
}

.stButton button {
    border-radius: 4px;
    font-weight: 500;
}

.sidebar-title {
    font-weight: 600;
    margin-bottom: 0.5rem;
}

/* Table styling */
.dataframe {
    width: 100%;
    border-collapse: collapse;
}

.dataframe th, .dataframe td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

.dataframe th {
    background-color: #f2f2f2;
    font-weight: 600;
}

/* Image styling */
.extracted-image {
    max-width: 100%;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    margin: 10px 0;
}

.pdf-info-box {
    background-color: #f0f9ff;
    border-left: 4px solid #3b82f6;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 0 4px 4px 0;
}

/* Malayalam text styling */
.malayalam-text {
    font-family: 'Noto Sans Malayalam', sans-serif;
    line-height: 1.8;
    font-size: 16px;
}

/* Chat message styling */
.stChatMessage {
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
}

.stChatMessage.user {
    background-color: #f3f4f6;
    border-left: 4px solid #3b82f6;
}

.stChatMessage.assistant {
    background-color: #fef3c7;
    border-left: 4px solid #f59e0b;
}

/* Form styling */
.stForm {
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 1rem;
    background-color: #f9fafb;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = None
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'processing' not in st.session_state:
    st.session_state.processing = False
# ========== ADDED SESSION STATES ==========
if 'uploaded_pdf_data' not in st.session_state:
    st.session_state.uploaded_pdf_data = None
if 'show_pdf_details' not in st.session_state:
    st.session_state.show_pdf_details = False
if 'temporary_pdf_path' not in st.session_state:
    st.session_state.temporary_pdf_path = None
# ==========================================

# Function to initialize the RAG system
def initialize_rag():
    """Initialize the Malayalam RAG system"""
    try:
        with st.spinner(" Initializing Malayalam RAG System..."):
            rag = MalayalamRAG()
            
            # Check if indexing is needed
            if rag.collection.count() == 0:
                st.info(" Indexing documents (this may take 10-15 minutes)...")
                success = rag.index_documents()
                if not success:
                    st.error("Failed to index documents!")
                    return None
            
            st.session_state.rag_system = rag
            st.session_state.initialized = True
            st.success(" RAG System Initialized Successfully!")
            return rag
    except Exception as e:
        st.error(f" Error initializing RAG system: {str(e)}")
        return None

# ========== PDF PROCESSING FUNCTIONS ==========

def check_unstructured_installed():
    """Check if Unstructured is installed"""
    try:
        from unstructured.partition.pdf import partition_pdf
        return True
    except ImportError:
        return False

def process_uploaded_pdf(uploaded_file):
    """Process uploaded PDF file using Unstructured"""
    try:
        # Check if Unstructured is installed
        if not check_unstructured_installed():
            st.error("❌ Unstructured not installed! Run: pip install 'unstructured[pdf,ocr]'")
            return None
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Store path for cleanup
        st.session_state.temporary_pdf_path = tmp_file_path
        
        # Process PDF with Unstructured
        with st.spinner("📄 PDF പ്രോസസ്സ് ചെയ്യുന്നു (Malayalam OCR ഉപയോഗിച്ച്)..."):
            pdf_data = PDFProcessor.extract_from_pdf(tmp_file_path)
            
            if pdf_data:
                st.session_state.uploaded_pdf_data = pdf_data
                return pdf_data
            else:
                st.error("PDF പ്രോസസ്സ് ചെയ്യാനായില്ല! Malayalam OCR പ്രവർത്തിക്കുന്നില്ല.")
                return None
                
    except Exception as e:
        st.error(f"പിഡിഎഫ് പ്രോസസ്സ് ചെയ്യുന്നതിൽ പിശക്: {str(e)[:100]}")
        return None

def display_pdf_summary(pdf_data):
    """Display summary of extracted PDF content"""
    with st.expander("📊 പിഡിഎഫ് വിവരങ്ങൾ", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📄 പേജുകൾ", pdf_data['metadata'].get('pages', 0))
        
        with col2:
            st.metric("📊 ടേബിളുകൾ", pdf_data['metadata'].get('tables_extracted', 0))
        
        with col3:
            st.metric("🖼️ ചിത്രങ്ങൾ", pdf_data['metadata'].get('images_extracted', 0))
        
        # Show metadata
        if pdf_data['metadata'].get('ocr_used'):
            st.success("✅ Malayalam OCR പ്രവർത്തിച്ചു")
        
        if pdf_data['metadata'].get('language'):
            st.write(f"**ഭാഷ:** {pdf_data['metadata']['language']}")

def display_extracted_tables(pdf_data):
    """Display tables extracted from PDF"""
    tables = pdf_data.get('tables', [])
    if tables:
        with st.expander(f"📊 ടേബിളുകൾ ({len(tables)})", expanded=False):
            for table_info in tables[:5]:  # Show first 5 tables
                st.write(f"**പേജ് {table_info.get('page', 'N/A')} - ടേബിൾ {table_info.get('table_num', 1)}**")
                
                # Display table
                if table_info.get('rows'):
                    # Convert to DataFrame for nice display
                    try:
                        df = pd.DataFrame(table_info['rows'])
                        st.dataframe(df, use_container_width=True)
                    except:
                        # Display as text if DataFrame fails
                        st.text(table_info.get('text', ''))
                    
                    # Show table stats
                    cols1, cols2 = st.columns(2)
                    with cols1:
                        st.caption(f"വരികൾ: {table_info.get('num_rows', 0)}")
                    with cols2:
                        st.caption(f"നിരകൾ: {table_info.get('num_cols', 0)}")
                    
                    st.divider()
            
            if len(tables) > 5:
                st.info(f"കൂടുതൽ {len(tables) - 5} ടേബിളുകൾ ലഭ്യമാണ്")

def display_extracted_images(pdf_data):
    """Display images extracted from PDF"""
    images = pdf_data.get('images', [])
    if images:
        with st.expander(f"🖼️ ചിത്രങ്ങൾ ({len(images)})", expanded=False):
            cols = st.columns(3)
            for idx, img_info in enumerate(images[:6]):  # Show first 6 images
                col_idx = idx % 3
                with cols[col_idx]:
                    if img_info.get('base64'):
                        # Display image
                        st.image(f"data:image/png;base64,{img_info['base64']}", 
                                caption=f"പേജ് {img_info.get('page', 'N/A')}", 
                                use_column_width=True)
                        st.caption(f"{img_info.get('width', 0)}x{img_info.get('height', 0)} pixels")
            
            if len(images) > 6:
                st.info(f"കൂടുതൽ {len(images) - 6} ചിത്രങ്ങൾ ലഭ്യമാണ്")

def ask_question_about_pdf(question, pdf_data):
    """Ask question about uploaded PDF content"""
    if not pdf_data or not pdf_data.get('text'):
        return "പിഡിഎഫിൽ നിന്ന് വിവരങ്ങൾ ലഭിച്ചിട്ടില്ല."
    
    # Use PDFProcessor's search function
    return PDFProcessor.simple_search(pdf_data, question)

# ====================================================

# Function to process question
def process_question(question):
    """Process a question and return answer"""
    if st.session_state.rag_system:
        try:
            answer = st.session_state.rag_system.ask_question(question)
            
            # Save to answers.txt (as per your original code)
            with open("answers.txt", "a", encoding="utf-8") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Question: {question}\n")
                f.write(f"Answer: {answer}\n")
                f.write(f"{'='*60}\n\n")
            
            return answer
        except Exception as e:
            return f" Error: {str(e)}"
    else:
        return " Please initialize the RAG system first."

# Sidebar
with st.sidebar:
    st.markdown("### System Control")

    if not st.session_state.initialized:
        if st.button("Initialize System", type="primary", use_container_width=True):
            initialize_rag()
    else:
        st.success("System Ready")

        st.markdown("#### Indexed Documents")
        docs_dir = Path("malayalam_docs")
        if docs_dir.exists():
            for doc in docs_dir.glob("*.*"):
                file_type = "📝" if str(doc).endswith('.docx') else "📄"
                st.write(f"{file_type} {doc.name}")

        st.markdown("#### Vector Store")
        st.write(f"Total chunks: {st.session_state.rag_system.collection.count()}")
    
    # ========== OCR STATUS SECTION ==========
    st.divider()
    st.markdown("#### OCR Status")
    
    if check_unstructured_installed():
        st.success("✅ Unstructured OCR Available")
        
        # Check Tesseract languages
        try:
            import pytesseract
            langs = pytesseract.get_languages(config='')
            if 'mal' in langs:
                st.success("✅ Malayalam OCR Supported")
            else:
                st.warning("⚠️ Malayalam OCR not configured")
                st.caption("Install: tesseract-ocr-mal package")
        except:
            st.info("ℹ️ Tesseract not configured")
    else:
        st.error("❌ Unstructured not installed")
        st.code("pip install 'unstructured[pdf,ocr]'")
    # ========================================
    
    # ========== PDF UPLOAD SECTION ==========
    st.divider()
    st.markdown("### 📄 PDF Upload")
    
    uploaded_file = st.file_uploader(
        "PDF ഫയൽ അപ്‌ലോഡ് ചെയ്യുക",
        type=['pdf'],
        help="പിഡിഎഫ് ഫയൽ അപ്‌ലോഡ് ചെയ്ത് ഉടൻ തന്നെ ചോദ്യങ്ങൾ ചോദിക്കാം"
    )
    
    if uploaded_file is not None:
        if st.button("📊 PDF വിശകലനം ചെയ്യുക", use_container_width=True):
            pdf_data = process_uploaded_pdf(uploaded_file)
            if pdf_data:
                st.success(f"✅ PDF വിശകലനം പൂർത്തിയായി!")
                st.session_state.show_pdf_details = True
                st.rerun()
    
    # Clear uploaded PDF button
    if st.session_state.uploaded_pdf_data:
        if st.button("🗑️ അപ്‌ലോഡ് ചെയ്ത PDF മായ്‌ക്കുക", use_container_width=True):
            # Clean up temporary file
            if st.session_state.temporary_pdf_path and os.path.exists(st.session_state.temporary_pdf_path):
                os.unlink(st.session_state.temporary_pdf_path)
            
            st.session_state.uploaded_pdf_data = None
            st.session_state.temporary_pdf_path = None
            st.session_state.show_pdf_details = False
            st.rerun()
    # ==============================================

    st.divider()

    if st.button("Clear Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    # Vector DB info
    if st.session_state.initialized:
        st.subheader(" Vector Database")
        count = st.session_state.rag_system.collection.count()
        st.write(f"Chunks indexed: {count}")
    
    # Clear chat button
    st.divider()
    if st.button(" Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    # System info
    st.divider()
    st.subheader(" About")
    st.write("""
    **Malayalam RAG QnA System**
    
    Using:
    - Ollama for embeddings
    - ChromaDB for vector storage
    - Gemini AI for answer generation
    - Unstructured.io for PDF OCR
    
    Features:
    - Malayalam OCR for PDFs
    - Table extraction
    - Image extraction
    - Chat history
    
    All answers are saved to `answers.txt`
    """)

# Main content area
st.title("Malayalam Q&A System")
st.markdown("### പാഠഭാഗത്തെ സംശയങ്ങൾ ചോദിക്കുക")

# ========== PDF CONTENT DISPLAY ==========
if st.session_state.uploaded_pdf_data and st.session_state.show_pdf_details:
    st.markdown("---")
    st.subheader("📄 അപ്‌ലോഡ് ചെയ്ത PDF വിവരങ്ങൾ")
    
    pdf_data = st.session_state.uploaded_pdf_data
    
    # Display PDF summary
    display_pdf_summary(pdf_data)
    
    # Display text preview
    with st.expander("📝 എക്സ്ട്രാക്ടഡ് വാചകം", expanded=False):
        text_preview = pdf_data['text'][:2000] + "..." if len(pdf_data['text']) > 2000 else pdf_data['text']
        st.text_area("", text_preview, height=200, disabled=True, label_visibility="collapsed")
    
    # Display tables
    display_extracted_tables(pdf_data)
    
    # Display images
    display_extracted_images(pdf_data)
    
    # Quick analysis section
    st.markdown("---")
    st.subheader("🔍 PDF-ലേക്കുള്ള ചോദ്യങ്ങൾ")
    
    # PDF Question Form (clears on submit)
    with st.form("pdf_question_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            pdf_question = st.text_input(
                "PDF-നെക്കുറിച്ചുള്ള ചോദ്യം:",
                key="pdf_question_input",
                placeholder="ഈ PDF-ലെ പ്രധാന വിവരങ്ങൾ എന്തെല്ലാം?",
                label_visibility="collapsed"
            )
        with col2:
            ask_pdf_btn = st.form_submit_button("PDF-യോട് ചോദിക്കുക", use_container_width=True)
    
    if ask_pdf_btn and pdf_question:
        with st.spinner("PDF വിശകലനം ചെയ്യുന്നു..."):
            answer = ask_question_about_pdf(pdf_question, pdf_data)
            
            # Display answer
            st.markdown("### 💡 ഉത്തരം:")
            st.markdown(answer)
            
            # Add to chat history
            st.session_state.messages.append({"role": "user", "content": f"[PDF] {pdf_question}"})
            st.session_state.messages.append({"role": "assistant", "content": answer})
    
    st.markdown("---")
# ================================================

# Display chat messages
chat_container = st.container()

with chat_container:
    if st.session_state.messages:
        st.subheader("💬 Conversation History")
        
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                with st.chat_message("user"):
                    # Check if it's a PDF question
                    if message["content"].startswith("[PDF]"):
                        st.markdown(f'<div style="color: #3b82f6;">📄 {message["content"][6:]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="malayalam-text">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                with st.chat_message("assistant"):
                    st.markdown(f'<div class="malayalam-text">{message["content"]}</div>', unsafe_allow_html=True)
        
        st.divider()

# Main Question Form (clears on submit)
st.markdown("### പുതിയ ചോദ്യം ചോദിക്കുക")

with st.form("main_question_form", clear_on_submit=True):
    col1, col2 = st.columns([6, 1])
    
    with col1:
        question = st.text_input(
            "നിങ്ങളുടെ ചോദ്യം ഇവിടെ എഴുതുക:",
            key="question_input",
            label_visibility="collapsed",
            placeholder="നിങ്ങളുടെ ചോദ്യം ഇവിടെ എഴുതുക (മലയാളത്തിൽ)"
        )
    
    with col2:
        ask_button = st.form_submit_button("ചോദിക്കുക", type="primary", use_container_width=True)
    
    if ask_button and question:
        if not st.session_state.initialized:
            st.warning(" Please initialize the RAG system from the sidebar first!")
        else:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": question})
            
            # Process and get answer
            with st.spinner(" ഉത്തരം തിരയുന്നു..."):
                try:
                    answer = process_question(question)
                    
                    # Add assistant message to chat
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                    # Rerun to show updated chat
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Show initialization prompt if not initialized
if not st.session_state.initialized:
    st.info("**Please initialize the RAG system from the sidebar to start asking questions.**")

# Footer
st.markdown("---")
st.caption("Powered by Ollama, ChromaDB & Gemini AI | PDF OCR with Unstructured.io")