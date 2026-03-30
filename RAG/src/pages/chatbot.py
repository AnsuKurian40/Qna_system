import streamlit as st
import sys
import os
from pathlib import Path
import time
import tempfile
import base64
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

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

/* Logout button styling */
.logout-btn {
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-weight: 500 !important;
}

.logout-btn:hover {
    background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%) !important;
}

/* History panel styling */
.history-panel {
    background: #f8fafc;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    border: 1px solid #e2e8f0;
    transition: all 0.2s ease;
}

.history-panel:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
}

.history-date {
    color: #64748b;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 5px;
}

.history-question {
    color: #1e293b;
    font-weight: 500;
    margin-bottom: 3px;
}

.history-answer {
    color: #475569;
    font-size: 0.9rem;
    line-height: 1.5;
}

/* Chat container enhancements */
.chat-container {
    max-height: 500px;
    overflow-y: auto;
    padding-right: 10px;
}

.chat-container::-webkit-scrollbar {
    width: 6px;
}

.chat-container::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
}

/* New chat button styling */
.new-chat-btn {
    background: linear-gradient(135deg, #10b981 0%, #34d399 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
    margin-bottom: 15px !important;
}

.new-chat-btn:hover {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
}

/* Chat session styling */
.chat-session {
    background: #f1f5f9;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    border-left: 4px solid #3b82f6;
}

.chat-session-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.chat-session-title {
    font-weight: 600;
    color: #1e293b;
}

.chat-session-date {
    font-size: 0.8rem;
    color: #64748b;
}

/* Active chat indicator */
.active-chat {
    border-left: 4px solid #10b981;
    background: #f0fdf4;
}
</style>
""", unsafe_allow_html=True)

# ========== DATABASE FUNCTIONS ==========
def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect('chatbot.db', check_same_thread=False)
    
    # Create chat_sessions table if not exists
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Modify chat_history table to include session_id
    try:
        c.execute('ALTER TABLE chat_history ADD COLUMN session_id INTEGER')
        c.execute('ALTER TABLE chat_history ADD FOREIGN KEY (session_id) REFERENCES chat_sessions(id)')
    except:
        pass  # Column already exists
    
    conn.commit()
    return conn

def get_db_cursor():
    """Get database cursor"""
    conn = init_database()
    return conn.cursor()

def save_chat_message_db(user_id, user_message, bot_response, session_id=None):
    """Save chat message to database"""
    conn = init_database()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO chat_history (user_id, user_message, bot_response, timestamp, session_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, user_message, bot_response, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), session_id))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        st.error(f"Error saving chat: {str(e)}")
        return None
    finally:
        conn.close()

def get_user_chat_history_db(user_id, session_id=None, limit=100):
    """Get user's chat history from database"""
    conn = init_database()
    c = conn.cursor()
    try:
        if session_id:
            c.execute('''
                SELECT id, user_message, bot_response, timestamp 
                FROM chat_history 
                WHERE user_id=? AND session_id=?
                ORDER BY timestamp ASC 
                LIMIT ?
            ''', (user_id, session_id, limit))
        else:
            c.execute('''
                SELECT id, user_message, bot_response, timestamp 
                FROM chat_history 
                WHERE user_id=? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
        return c.fetchall()
    except Exception as e:
        st.error(f"Error loading chat history: {str(e)}")
        return []
    finally:
        conn.close()

def create_new_chat_session_db(user_id, session_name="New Chat"):
    """Create a new chat session"""
    conn = init_database()
    c = conn.cursor()
    try:
        # Deactivate all other sessions for this user
        c.execute('UPDATE chat_sessions SET is_active=0 WHERE user_id=?', (user_id,))
        
        # Create new session
        c.execute('''
            INSERT INTO chat_sessions (user_id, session_name, created_at, is_active)
            VALUES (?, ?, ?, ?)
        ''', (user_id, session_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        st.error(f"Error creating chat session: {str(e)}")
        return None
    finally:
        conn.close()

def get_user_chat_sessions_db(user_id, limit=20):
    """Get user's chat sessions from database"""
    conn = init_database()
    c = conn.cursor()
    try:
        c.execute('''
            SELECT id, session_name, created_at, is_active 
            FROM chat_sessions 
            WHERE user_id=? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        return c.fetchall()
    except Exception as e:
        st.error(f"Error loading chat sessions: {str(e)}")
        return []
    finally:
        conn.close()

def get_active_session_id_db(user_id):
    """Get active session ID for user"""
    conn = init_database()
    c = conn.cursor()
    try:
        c.execute('''
            SELECT id FROM chat_sessions 
            WHERE user_id=? AND is_active=1 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (user_id,))
        result = c.fetchone()
        return result[0] if result else None
    except Exception as e:
        st.error(f"Error getting active session: {str(e)}")
        return None
    finally:
        conn.close()

def switch_chat_session_db(session_id, user_id):
    """Switch to a different chat session"""
    conn = init_database()
    c = conn.cursor()
    try:
        # Deactivate all sessions
        c.execute('UPDATE chat_sessions SET is_active=0 WHERE user_id=?', (user_id,))
        
        # Activate selected session
        c.execute('UPDATE chat_sessions SET is_active=1 WHERE id=? AND user_id=?', (session_id, user_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error switching session: {str(e)}")
        return False
    finally:
        conn.close()

def delete_chat_session_db(session_id, user_id):
    """Delete a chat session and all its messages"""
    conn = init_database()
    c = conn.cursor()
    try:
        # Delete chat messages first
        c.execute('DELETE FROM chat_history WHERE session_id=?', (session_id,))
        
        # Delete the session
        c.execute('DELETE FROM chat_sessions WHERE id=? AND user_id=?', (session_id, user_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting chat session: {str(e)}")
        return False
    finally:
        conn.close()

def rename_chat_session_db(session_id, new_name, user_id):
    """Rename a chat session"""
    conn = init_database()
    c = conn.cursor()
    try:
        c.execute('UPDATE chat_sessions SET session_name=? WHERE id=? AND user_id=?', 
                 (new_name, session_id, user_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error renaming chat session: {str(e)}")
        return False
    finally:
        conn.close()

def delete_chat_history_db(user_id):
    """Delete user's all chat history from database"""
    conn = init_database()
    c = conn.cursor()
    try:
        c.execute('DELETE FROM chat_history WHERE user_id=?', (user_id,))
        c.execute('DELETE FROM chat_sessions WHERE user_id=?', (user_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting chat history: {str(e)}")
        return False
    finally:
        conn.close()

def delete_single_chat_db(chat_id):
    """Delete a single chat message from database"""
    conn = init_database()
    c = conn.cursor()
    try:
        c.execute('DELETE FROM chat_history WHERE id=?', (chat_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting chat: {str(e)}")
        return False
    finally:
        conn.close()

# ========== AUTHENTICATION CHECK ==========
def check_authentication():
    """Check if user is authenticated"""
    if not st.session_state.get('authenticated', False):
        st.warning("⚠️ You need to login first!")
        st.markdown("[Click here to login](/)")
        st.stop()

# ========== LOGOUT FUNCTION ==========
def logout_user():
    """Logout user and clear session"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("pages/login.py")

# ========== INITIALIZE SESSION STATE ==========
def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'rag_system': None,
        'initialized': False,
        'messages': [],
        'processing': False,
        'uploaded_pdf_data': None,
        'show_pdf_details': False,
        'temporary_pdf_path': None,
        'show_history': False,
        'chat_history_loaded': False,
        'current_session_id': None,
        'chat_sessions': [],
        'active_session_name': "New Chat"
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Initialize session state
initialize_session_state()

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
        if not check_unstructured_installed():
            st.error("❌ Unstructured not installed! Run: pip install 'unstructured[pdf,ocr]'")
            return None
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        st.session_state.temporary_pdf_path = tmp_file_path
        
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
        
        if pdf_data['metadata'].get('ocr_used'):
            st.success("✅ Malayalam OCR പ്രവർത്തിച്ചു")
        
        if pdf_data['metadata'].get('language'):
            st.write(f"**ഭാഷ:** {pdf_data['metadata']['language']}")

def display_extracted_tables(pdf_data):
    """Display tables extracted from PDF"""
    tables = pdf_data.get('tables', [])
    if tables:
        with st.expander(f"📊 ടേബിളുകൾ ({len(tables)})", expanded=False):
            for table_info in tables[:5]:
                st.write(f"**പേജ് {table_info.get('page', 'N/A')} - ടേബിൾ {table_info.get('table_num', 1)}**")
                
                if table_info.get('rows'):
                    try:
                        df = pd.DataFrame(table_info['rows'])
                        st.dataframe(df, use_container_width=True)
                    except:
                        st.text(table_info.get('text', ''))
                    
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
            for idx, img_info in enumerate(images[:6]):
                col_idx = idx % 3
                with cols[col_idx]:
                    if img_info.get('base64'):
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
    
    return PDFProcessor.simple_search(pdf_data, question)

# ========== FUNCTION TO INITIALIZE RAG SYSTEM ==========
def initialize_rag():
    """Initialize the Malayalam RAG system"""
    try:
        with st.spinner(" Initializing Malayalam RAG System..."):
            rag = MalayalamRAG()
            
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

# ========== FUNCTION TO PROCESS QUESTION ==========
def process_question(question):
    """Process a question and return answer"""
    if st.session_state.rag_system:
        try:
            answer = st.session_state.rag_system.ask_question(question)
            
            # Save to answers.txt
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

# ========== CHAT SESSION MANAGEMENT ==========
def create_new_chat():
    """Create a new chat session"""
    if 'user_data' in st.session_state and 'id' in st.session_state.user_data:
        user_id = st.session_state.user_data['id']
        
        # Get session name from user
        session_name = st.text_input("Enter chat name:", value=f"Chat {len(st.session_state.chat_sessions) + 1}")
        
        if st.button("Create New Chat", key="create_new_chat_btn"):
            # Create new session in database
            session_id = create_new_chat_session_db(user_id, session_name)
            
            if session_id:
                # Clear current messages
                st.session_state.messages = []
                st.session_state.current_session_id = session_id
                st.session_state.active_session_name = session_name
                
                # Reload sessions
                load_chat_sessions()
                
                st.success(f"✅ New chat '{session_name}' created!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Failed to create new chat session")

def load_chat_sessions():
    """Load user's chat sessions"""
    if 'user_data' in st.session_state and 'id' in st.session_state.user_data:
        user_id = st.session_state.user_data['id']
        sessions = get_user_chat_sessions_db(user_id)
        st.session_state.chat_sessions = sessions
        
        # Get active session ID
        active_id = get_active_session_id_db(user_id)
        st.session_state.current_session_id = active_id
        
        # Get active session name
        for session in sessions:
            if session[0] == active_id:
                st.session_state.active_session_name = session[1] or "New Chat"
                break

def switch_to_session(session_id):
    """Switch to a different chat session"""
    if 'user_data' in st.session_state and 'id' in st.session_state.user_data:
        user_id = st.session_state.user_data['id']
        
        if switch_chat_session_db(session_id, user_id):
            # Clear current messages
            st.session_state.messages = []
            st.session_state.current_session_id = session_id
            
            # Load messages for this session
            load_current_session_messages()
            
            # Update session name
            for session in st.session_state.chat_sessions:
                if session[0] == session_id:
                    st.session_state.active_session_name = session[1] or "New Chat"
                    break
            
            st.success(f"✅ Switched to chat session!")
            time.sleep(0.5)
            st.rerun()

def load_current_session_messages():
    """Load messages for current session"""
    if 'user_data' in st.session_state and 'id' in st.session_state.user_data:
        user_id = st.session_state.user_data['id']
        
        if st.session_state.current_session_id:
            chat_history = get_user_chat_history_db(user_id, st.session_state.current_session_id, limit=50)
            
            # Convert to session state format
            st.session_state.messages = []
            for chat_id, user_msg, bot_resp, timestamp in chat_history:
                st.session_state.messages.append({"role": "user", "content": user_msg, "id": chat_id})
                st.session_state.messages.append({"role": "assistant", "content": bot_resp, "id": chat_id})

# ========== DISPLAY CHAT SESSIONS IN SIDEBAR ==========
def display_chat_sessions_sidebar():
    """Display chat sessions in sidebar"""
    st.sidebar.markdown("### 💬 Chat Sessions")
    
    # New Chat Button
    if st.sidebar.button("🆕 New Chat", key="new_chat_btn", use_container_width=True, type="primary"):
        st.session_state.show_new_chat_modal = True
    
    # New Chat Modal
    if st.session_state.get('show_new_chat_modal', False):
        with st.sidebar:
            st.markdown("---")
            st.markdown("#### Create New Chat")
            session_name = st.text_input("Chat Name:", value=f"Chat {len(st.session_state.chat_sessions) + 1}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Create", key="confirm_new_chat", use_container_width=True):
                    if 'user_data' in st.session_state and 'id' in st.session_state.user_data:
                        user_id = st.session_state.user_data['id']
                        session_id = create_new_chat_session_db(user_id, session_name)
                        
                        if session_id:
                            st.session_state.messages = []
                            st.session_state.current_session_id = session_id
                            st.session_state.active_session_name = session_name
                            load_chat_sessions()
                            st.session_state.show_new_chat_modal = False
                            st.success(f"✅ New chat created!")
                            time.sleep(1)
                            st.rerun()
            with col2:
                if st.button("Cancel", key="cancel_new_chat", use_container_width=True):
                    st.session_state.show_new_chat_modal = False
                    st.rerun()
            st.markdown("---")
    
    # Display existing sessions
    if st.session_state.chat_sessions:
        for session in st.session_state.chat_sessions:
            session_id, session_name, created_at, is_active = session
            
            # Format session name
            display_name = session_name or f"Chat {session_id}"
            date_str = created_at[:10] if isinstance(created_at, str) else created_at.strftime('%Y-%m-%d')
            
            # Create a container for each session
            with st.sidebar.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Active session styling
                    if session_id == st.session_state.current_session_id:
                        st.markdown(f"**▶️ {display_name}**")
                        st.caption(f"📅 {date_str}")
                    else:
                        if st.button(f"💬 {display_name}", 
                                    key=f"session_{session_id}",
                                    use_container_width=True,
                                    help=f"Click to switch to this chat (Created: {date_str})"):
                            switch_to_session(session_id)
                
                with col2:
                    # Delete button for session
                    if st.button("🗑️", key=f"delete_session_{session_id}", 
                               help=f"Delete {display_name}"):
                        if delete_chat_session_db(session_id, st.session_state.user_data['id']):
                            load_chat_sessions()
                            if session_id == st.session_state.current_session_id:
                                # Switch to another session if available
                                if st.session_state.chat_sessions:
                                    switch_to_session(st.session_state.chat_sessions[0][0])
                                else:
                                    create_new_chat_session_db(st.session_state.user_data['id'], "New Chat")
                                    load_chat_sessions()
                            st.success(f"✅ Chat '{display_name}' deleted!")
                            time.sleep(1)
                            st.rerun()
    else:
        st.sidebar.info("No chat sessions yet. Create a new chat!")
    
    st.sidebar.divider()
    
    # Current session info
    if st.session_state.current_session_id:
        st.sidebar.markdown(f"**Current Chat:** {st.session_state.active_session_name}")
        
        # Rename current session
        if st.sidebar.button("✏️ Rename Current Chat", key="rename_chat_btn", use_container_width=True):
            st.session_state.show_rename_modal = True
        
        if st.session_state.get('show_rename_modal', False):
            new_name = st.sidebar.text_input("New name:", 
                                            value=st.session_state.active_session_name,
                                            key="rename_input")
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button("Save", key="save_rename", use_container_width=True):
                    if rename_chat_session_db(st.session_state.current_session_id, 
                                            new_name, 
                                            st.session_state.user_data['id']):
                        st.session_state.active_session_name = new_name
                        load_chat_sessions()
                        st.session_state.show_rename_modal = False
                        st.success("✅ Chat renamed!")
                        time.sleep(1)
                        st.rerun()
            with col2:
                if st.button("Cancel", key="cancel_rename", use_container_width=True):
                    st.session_state.show_rename_modal = False
                    st.rerun()
    
    st.sidebar.divider()

# ========== MAIN CHATBOT FUNCTION ==========
def main():
    # First check authentication
    check_authentication()
    
    # Get user info from session state
    user_data = st.session_state.get('user_data', {})
    
    # Load chat sessions on first load
    if 'sessions_loaded' not in st.session_state:
        load_chat_sessions()
        st.session_state.sessions_loaded = True
    
    # Load messages for current session
    if 'messages_loaded' not in st.session_state:
        load_current_session_messages()
        st.session_state.messages_loaded = True
    
    # Custom title with user info and session info
    col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
    
    with col1:
        st.title("🤖 Malayalam Q&A System")
        if st.session_state.current_session_id:
            st.markdown(f"### 💬 {st.session_state.active_session_name}")
        else:
            st.markdown(f"### Welcome, {user_data.get('full_name', 'User')}!")
    
    with col3:
        # New Chat button in header
        if st.button("🆕 New Chat", key="header_new_chat", use_container_width=True):
            st.session_state.show_new_chat_modal = True
            st.rerun()
    
    with col4:
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            logout_user()
    
    # Sidebar with user info and chat sessions
    with st.sidebar:
        # User info section
        st.markdown(f"### 👤 {user_data.get('full_name', 'User')}")
        st.markdown(f"**Username:** {user_data.get('username', 'N/A')}")
        st.markdown(f"**Email:** {user_data.get('email', 'N/A')}")
        st.markdown(f"**Role:** {user_data.get('role', 'user').title()}")
        st.markdown("---")
        
        # Chat Sessions Section
        display_chat_sessions_sidebar()
        
        # System Control
        st.markdown("### System Control")
        if not st.session_state.initialized:
            if st.button("Initialize System", type="primary", use_container_width=True):
                initialize_rag()
        else:
            st.success("✅ System Ready")
        
        # Indexed Documents
        st.markdown("#### Indexed Documents")
        docs_dir = Path("malayalam_docs")
        if docs_dir.exists():
            for doc in docs_dir.glob("*.*"):
                file_type = "📝" if str(doc).endswith('.docx') else "📄"
                st.write(f"{file_type} {doc.name}")

        st.markdown("#### Vector Store")
        if st.session_state.initialized:
            st.write(f"Total chunks: {st.session_state.rag_system.collection.count()}")
        
        # OCR STATUS SECTION
        st.divider()
        st.markdown("#### OCR Status")
        
        if check_unstructured_installed():
            st.success("✅ Unstructured OCR Available")
            
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
        
        # PDF UPLOAD SECTION
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
                if st.session_state.temporary_pdf_path and os.path.exists(st.session_state.temporary_pdf_path):
                    os.unlink(st.session_state.temporary_pdf_path)
                
                st.session_state.uploaded_pdf_data = None
                st.session_state.temporary_pdf_path = None
                st.session_state.show_pdf_details = False
                st.rerun()
        
        st.divider()
        
        # Clear current session chat (only messages, not the session)
        if st.button("🗑️ Clear Current Chat", use_container_width=True):
            st.session_state.messages = []
            st.success("Current chat cleared!")
            time.sleep(0.5)
            st.rerun()
        
        # Clear all sessions button
        if st.button("🗑️ Clear All Chats", use_container_width=True, type="secondary"):
            if 'user_data' in st.session_state and 'id' in st.session_state.user_data:
                if delete_chat_history_db(st.session_state.user_data['id']):
                    st.session_state.messages = []
                    load_chat_sessions()
                    st.success("All chats cleared!")
                    time.sleep(1)
                    st.rerun()
        
        # User Information
        st.divider()
        st.markdown("### User Information")
        st.write(f"Logged in as: **{user_data.get('username', 'User')}**")
        st.write(f"Role: **{user_data.get('role', 'user').title()}**")
        st.write(f"Member since: {user_data.get('created_at', 'N/A')[:10]}")
        
        if st.button("Logout", type="secondary", use_container_width=True):
            logout_user()
    
    # Main content area
    st.markdown("### പാഠഭാഗത്തെ സംശയങ്ങൾ ചോദിക്കുക")
    
    # ========== PDF CONTENT DISPLAY ==========
    if st.session_state.uploaded_pdf_data and st.session_state.show_pdf_details:
        st.markdown("---")
        st.subheader("📄 അപ്‌ലോഡ് ചെയ്ത PDF വിവരങ്ങൾ")
        
        pdf_data = st.session_state.uploaded_pdf_data
        
        display_pdf_summary(pdf_data)
        
        with st.expander("📝 എക്സ്ട്രാക്ടഡ് വാചകം", expanded=False):
            text_preview = pdf_data['text'][:2000] + "..." if len(pdf_data['text']) > 2000 else pdf_data['text']
            st.text_area("", text_preview, height=200, disabled=True, label_visibility="collapsed")
        
        display_extracted_tables(pdf_data)
        display_extracted_images(pdf_data)
        
        st.markdown("---")
        st.subheader("🔍 PDF-ലേക്കുള്ള ചോദ്യങ്ങൾ")
        
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
                
                st.markdown("### 💡 ഉത്തരം:")
                st.markdown(answer)
                
                # Save to database if user is logged in
                if 'user_data' in st.session_state and 'id' in st.session_state.user_data:
                    user_id = st.session_state.user_data['id']
                    save_chat_message_db(user_id, f"[PDF] {pdf_question}", answer, st.session_state.current_session_id)
                
                # Add to session state
                st.session_state.messages.append({"role": "user", "content": f"[PDF] {pdf_question}"})
                st.session_state.messages.append({"role": "assistant", "content": answer})
        
        st.markdown("---")
    
    # Display chat messages
    chat_container = st.container()

    with chat_container:
        if st.session_state.messages:
            st.subheader(f"💬 {st.session_state.active_session_name}")
            
            for i, message in enumerate(st.session_state.messages):
                if message["role"] == "user":
                    with st.chat_message("user"):
                        if message["content"].startswith("[PDF]"):
                            st.markdown(f'<div style="color: #3b82f6;">📄 {message["content"][6:]}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="malayalam-text">{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    with st.chat_message("assistant"):
                        st.markdown(f'<div class="malayalam-text">{message["content"]}</div>', unsafe_allow_html=True)
            
            st.divider()

    # Main Question Form
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
                # Add user message to session state
                st.session_state.messages.append({"role": "user", "content": question})
                
                # Process and get answer
                with st.spinner(" ഉത്തരം തിരയുന്നു..."):
                    try:
                        answer = process_question(question)
                        
                        # Add assistant message to session state
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        # Save to database if user is logged in
                        if 'user_data' in st.session_state and 'id' in st.session_state.user_data:
                            user_id = st.session_state.user_data['id']
                            save_chat_message_db(user_id, question, answer, st.session_state.current_session_id)
                        
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

if __name__ == "__main__":
    main()