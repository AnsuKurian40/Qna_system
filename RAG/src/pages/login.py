import streamlit as st
import hashlib
import re
import sqlite3
import json
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="ChatBot Login",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Modern Professional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        padding: 0 !important;
    }
    
    .stApp {
        background: #0a0e27;
        background-image: 
            radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
            radial-gradient(at 0% 100%, rgba(168, 85, 247, 0.15) 0px, transparent 50%);
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }
    
    /* Animated background particles */
    .stApp::before {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.05) 1px, transparent 1px),
            radial-gradient(circle at 80% 80%, rgba(168, 85, 247, 0.05) 1px, transparent 1px);
        background-size: 50px 50px;
        animation: float 20s ease-in-out infinite;
        pointer-events: none;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 20px;
        position: relative;
        z-index: 1;
            
    }
    
    
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .logo-container {
        text-align: center;
        margin-bottom: 36px;
        position: relative;
    }
    
    .logo {
        font-size: 56px;
        margin-bottom: 16px;
        display: inline-block;
        animation: pulse 2s ease-in-out infinite;
        filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.5));
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .logo-text {
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    
    .logo-subtext {
        color: rgba(255, 255, 255, 0.6);
        font-size: 14px;
        font-weight: 400;
        letter-spacing: 0.3px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        padding: 6px;
        border-radius: 16px;
        margin-bottom: 32px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 12px 20px;
        font-weight: 500;
        font-size: 14px;
        color: rgba(255, 255, 255, 0.6);
        transition: all 0.3s ease;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: rgba(255, 255, 255, 0.9);
        background: rgba(255, 255, 255, 0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    /* Form elements */
    h3 {
        font-size: 20px !important;
        margin-bottom: 24px !important;
        color: rgba(255, 255, 255, 0.95) !important;
        font-weight: 600 !important;
        letter-spacing: -0.3px;
    }
    
    .stTextInput > label, .stCheckbox > label {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        margin-bottom: 8px !important;
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
        font-size: 14px !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input {
    background: #ffffff !important;          /* White background */
    border: 1px solid #d1d5db !important;    /* Light gray border */
    border-radius: 12px !important;
    padding: 14px 16px !important;
    font-size: 14px !important;
    color: #000000 !important;               /* Black text */
    transition: all 0.3s ease !important;
}
            
    
    .stTextInput > div > div > input:focus {
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
    }
    
    .stCheckbox {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 24px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4) !important;
        letter-spacing: 0.3px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5) !important;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Social buttons */
    .social-divider {
        display: flex;
        align-items: center;
        margin: 32px 0 24px 0;
        color: rgba(255, 255, 255, 0.5);
        font-size: 13px;
    }
    
    .social-divider::before,
    .social-divider::after {
        content: "";
        flex: 1;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .social-divider span {
        padding: 0 16px;
    }
    
    /* Messages */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        padding: 14px 16px !important;
        font-size: 14px !important;
    }
    
    [data-baseweb="notification"] {
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 3px solid #ef4444 !important;
    }
    
    .stSuccess {
        background: rgba(34, 197, 94, 0.1) !important;
        border-left: 3px solid #22c55e !important;
        color: #86efac !important;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.1) !important;
        border-left: 3px solid #3b82f6 !important;
        color: #93c5fd !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 3px solid #ef4444 !important;
        color: #fca5a5 !important;
    }
    
    /* Form container */
    .stForm {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Glow effect on focus */
    .glow {
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from {
            box-shadow: 0 0 5px rgba(59, 130, 246, 0.2);
        }
        to {
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
        }
    }
</style>
""", unsafe_allow_html=True)

# ========== SQLITE DATABASE SETUP ==========
def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect('chatbot.db', check_same_thread=False)
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create chat_history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_message TEXT,
            bot_response TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Check if admin user exists
    c.execute("SELECT COUNT(*) FROM users WHERE email='admin@chatbot.com'")
    if c.fetchone()[0] == 0:
        admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute('''
            INSERT INTO users (email, username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin@chatbot.com', 'admin', admin_hash, 'System Administrator', 'admin'))
    
    # Check if demo user exists
    c.execute("SELECT COUNT(*) FROM users WHERE email='user@chatbot.com'")
    if c.fetchone()[0] == 0:
        user_hash = hashlib.sha256("user123".encode()).hexdigest()
        c.execute('''
            INSERT INTO users (email, username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('user@chatbot.com', 'demo_user', user_hash, 'Demo User', 'user'))
    
    conn.commit()
    return conn

# Initialize database
conn = init_database()

# ========== DATABASE FUNCTIONS ==========
def get_db_cursor():
    """Get database cursor"""
    return conn.cursor()

def register_user_db(email, username, password, full_name):
    """Register a new user in database"""
    c = get_db_cursor()
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute('''
            INSERT INTO users (email, username, password_hash, full_name)
            VALUES (?, ?, ?, ?)
        ''', (email, username, password_hash, full_name))
        conn.commit()
        return True, "Registration successful"
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: users.email" in str(e):
            return False, "Email already registered"
        elif "UNIQUE constraint failed: users.username" in str(e):
            return False, "Username already taken"
        else:
            return False, f"Registration failed: {str(e)}"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def login_user_db(email, password):
    """Authenticate user from database"""
    c = get_db_cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    c.execute('''
        SELECT id, email, username, full_name, role, created_at 
        FROM users 
        WHERE email=? AND password_hash=? AND is_active=1
    ''', (email, password_hash))
    
    user = c.fetchone()
    
    if user:
        c.execute('''
            UPDATE users SET last_login=CURRENT_TIMESTAMP WHERE id=?
        ''', (user[0],))
        conn.commit()
        
        user_dict = {
            'id': user[0],
            'email': user[1],
            'username': user[2],
            'full_name': user[3],
            'role': user[4],
            'created_at': user[5]
        }
        return True, user_dict
    else:
        return False, None

def save_chat_message(user_id, user_message, bot_response):
    """Save chat message to database"""
    c = get_db_cursor()
    c.execute('''
        INSERT INTO chat_history (user_id, user_message, bot_response)
        VALUES (?, ?, ?)
    ''', (user_id, user_message, bot_response))
    conn.commit()

def get_user_chat_history(user_id, limit=50):
    """Get user's chat history"""
    c = get_db_cursor()
    c.execute('''
        SELECT user_message, bot_response, timestamp 
        FROM chat_history 
        WHERE user_id=? 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (user_id, limit))
    return c.fetchall()

def update_password(email, new_password):
    """Update user password"""
    c = get_db_cursor()
    try:
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        c.execute('''
            UPDATE users SET password_hash=? WHERE email=?
        ''', (password_hash, email))
        conn.commit()
        return c.rowcount > 0
    except Exception as e:
        return False

# ========== SESSION STATE ==========
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# ========== HELPER FUNCTIONS ==========
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""

# ========== LOGIN PAGE ==========
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        
        # Logo and header
        st.markdown('''
            <div class="logo-container">
                <div class="logo">🤖</div>
                <div class="logo-text">SmartChat AI</div>
                <div class="logo-subtext">Your intelligent conversation companion</div>
            </div>
        ''', unsafe_allow_html=True)
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["🔐 Sign In", "📝 Sign Up", "🔑 Reset"])
        
        with tab1:
            st.subheader("Welcome Back")
            
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email Address", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                remember_me = st.checkbox("Remember me for 30 days")
                
                login_submitted = st.form_submit_button("Sign In", use_container_width=True)
                
                if login_submitted:
                    if not email or not password:
                        st.error("⚠️ Please fill in all fields")
                    elif not validate_email(email):
                        st.error("⚠️ Please enter a valid email address")
                    else:
                        success, user_data = login_user_db(email, password)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.user_data = user_data
                            
                            history = get_user_chat_history(user_data['id'])
                            st.session_state.chat_messages = []
                            for user_msg, bot_resp, timestamp in reversed(history):
                                st.session_state.chat_messages.append({"role": "user", "content": user_msg})
                                st.session_state.chat_messages.append({"role": "assistant", "content": bot_resp})
                            
                            st.success("✅ Login successful! Redirecting...")
                            #st.balloons()
                            #time.sleep(1)
                            st.switch_page("pages/chatbot.py")
                        else:
                            st.error("❌ Invalid credentials. Please try again.")
        
        with tab2:
            st.subheader("Create Account")
            
            with st.form("register_form", clear_on_submit=False):
                full_name = st.text_input("Full Name", placeholder="John Doe")
                username = st.text_input("Username", placeholder="johndoe")
                email = st.text_input("Email Address", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="Min. 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                
                register_submitted = st.form_submit_button("Create Account", use_container_width=True)
                
                if register_submitted:
                    if not all([full_name, username, email, password, confirm_password]):
                        st.error("⚠️ Please fill in all fields")
                    elif not validate_email(email):
                        st.error("⚠️ Invalid email format")
                    elif password != confirm_password:
                        st.error("⚠️ Passwords don't match")
                    else:
                        is_valid, msg = validate_password(password)
                        if not is_valid:
                            st.error(f"⚠️ {msg}")
                        else:
                            success, message = register_user_db(email, username, password, full_name)
                            if success:
                                st.success(f"✅ {message}")
                                st.info("🎉 Switch to Sign In tab to access your account")
                            else:
                                st.error(f"❌ {message}")
        
        with tab3:
            st.subheader("Reset Password")
            
            with st.form("reset_form", clear_on_submit=False):
                email = st.text_input("Email Address", placeholder="you@example.com")
                new_password = st.text_input("New Password", type="password", placeholder="Min. 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                
                reset_submitted = st.form_submit_button("Reset Password", use_container_width=True)
                
                if reset_submitted:
                    if not email or not new_password or not confirm_password:
                        st.error("⚠️ Please fill in all fields")
                    elif not validate_email(email):
                        st.error("⚠️ Invalid email format")
                    elif new_password != confirm_password:
                        st.error("⚠️ Passwords don't match")
                    else:
                        is_valid, msg = validate_password(new_password)
                        if not is_valid:
                            st.error(f"⚠️ {msg}")
                        else:
                            success = update_password(email, new_password)
                            if success:
                                st.success("✅ Password updated successfully!")
                            else:
                                st.error("❌ Email not found")
        
        # Social login
        #st.markdown('<div class="social-divider"><span>Or continue with</span></div>', unsafe_allow_html=True)
        
        #col_a, col_b, col_c = st.columns(3)
        #with col_a:
         #   if st.button("Google", use_container_width=True):
          #      st.info("🔵 OAuth integration coming soon")
        #with col_b:
         #   if st.button("GitHub", use_container_width=True):
          #      st.info("🔵 OAuth integration coming soon")
        #with col_c:
         #   if st.button("Apple", use_container_width=True):
          #      st.info("🔵 OAuth integration coming soon")
        
        #st.markdown('</div>', unsafe_allow_html=True)

# ========== MAIN FUNCTION ==========
def main():
    if st.session_state.get('authenticated', False):
        st.switch_page("pages/chatbot.py")
    else:
        login_page()

if __name__ == "__main__":
    main()