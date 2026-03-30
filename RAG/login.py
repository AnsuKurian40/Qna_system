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

# DeepSeek-inspired custom CSS
st.markdown("""
<style>
    .main {
        padding: 0 !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        min-height: 100vh;
    }
    
    .login-container {
        display: flex;
        justify-content: center;
        align-items: flex-start;  /* Changed from center to flex-start */
        min-height: 100vh;
        padding: 0;  /* Removed padding */
        margin-top: -60px;  /* Pull the form up */
    }
    
    .login-box {
        background: white;
        border-radius: 16px;
        padding: 40px 35px;  /* Slightly reduced padding */
        width: 100%;
        max-width: 480px;  /* Slightly reduced width */
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        margin-top: 60px;  /* Ensure form is visible */
        position: relative;
        z-index: 10;
    }
    
    .logo-container {
        text-align: center;
        margin-bottom: 30px;  /* Reduced margin */
    }
    
    .logo {
        font-size: 42px;  /* Reduced size */
        color: #2563eb;
        margin-bottom: 10px;
    }
    
    .logo-text {
        font-size: 28px;  /* Reduced size */
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 6px;
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .logo-subtext {
        color: #64748b;
        font-size: 14px;
        font-weight: 400;
    }
    
    .input-field {
        margin-bottom: 20px;  /* Reduced margin */
    }
    
    .login-btn {
        width: 100%;
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 14px;  /* Reduced padding */
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 15px;
        margin-top: 10px;
    }
    
    .login-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 15px rgba(37, 99, 235, 0.2);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
        transform: translateY(-1px);
        box-shadow: 0 5px 15px rgba(37, 99, 235, 0.2);
    }
    
    .divider {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 25px 0;  /* Reduced margin */
        color: #94a3b8;
        font-size: 13px;
    }
    
    .divider::before,
    .divider::after {
        content: "";
        flex: 1;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .divider span {
        padding: 0 15px;
        background: white;
    }
    
    .social-login {
        display: flex;
        justify-content: center;
        gap: 15px;  /* Reduced gap */
        margin-bottom: 20px;  /* Reduced margin */
    }
    
    .social-btn {
        width: 45px;  /* Reduced size */
        height: 45px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 18px;  /* Reduced size */
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid #e2e8f0;
    }
    
    .social-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    .google-btn {
        background: white;
        color: #db4437;
    }
    
    .facebook-btn {
        background: white;
        color: #4267B2;
    }
    
    .github-btn {
        background: white;
        color: #333;
    }
    
    .register-link {
        text-align: center;
        margin-top: 20px;  /* Reduced margin */
        color: #64748b;
        font-size: 13px;
    }
    
    .register-link a {
        color: #2563eb;
        text-decoration: none;
        font-weight: 600;
    }
    
    .register-link a:hover {
        text-decoration: underline;
    }
    
    .error-message {
        color: #dc2626;
        background-color: #fef2f2;
        padding: 10px;  /* Reduced padding */
        border-radius: 8px;
        margin: 8px 0;  /* Reduced margin */
        border: 1px solid #fecaca;
        font-size: 13px;
    }
    
    .success-message {
        color: #059669;
        background-color: #f0fdf4;
        padding: 10px;
        border-radius: 8px;
        margin: 8px 0;
        border: 1px solid #bbf7d0;
        font-size: 13px;
    }
    
    .info-message {
        color: #2563eb;
        background-color: #eff6ff;
        padding: 10px;
        border-radius: 8px;
        margin: 8px 0;
        border: 1px solid #dbeafe;
        font-size: 13px;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        padding: 10px 14px;  /* Reduced padding */
        font-size: 14px;  /* Reduced font size */
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
    }
    
    /* Tab styling - made more compact */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #f1f5f9;
        padding: 3px;
        border-radius: 10px;
        margin-bottom: 20px;  /* Reduced margin */
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;  /* Reduced padding */
        font-weight: 500;
        font-size: 14px;  /* Reduced font size */
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* Make form titles smaller */
    h3 {
        font-size: 18px !important;
        margin-bottom: 15px !important;
    }
    
    /* Remove extra spacing in forms */
    .stForm {
        margin-top: -10px;
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    
    p {
        color: #64748b !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
    
    /* Streamlit report element removal */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .st-emotion-cache-1kyxreq {  /* Streamlit form container */
        margin-top: -10px;
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
        # Create default admin user
        admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute('''
            INSERT INTO users (email, username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin@chatbot.com', 'admin', admin_hash, 'System Administrator', 'admin'))
    
    # Check if demo user exists
    c.execute("SELECT COUNT(*) FROM users WHERE email='user@chatbot.com'")
    if c.fetchone()[0] == 0:
        # Create demo user
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
    
    # Hash the input password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Query user
    c.execute('''
        SELECT id, email, username, full_name, role, created_at 
        FROM users 
        WHERE email=? AND password_hash=? AND is_active=1
    ''', (email, password_hash))
    
    user = c.fetchone()
    
    if user:
        # Update last login
        c.execute('''
            UPDATE users SET last_login=CURRENT_TIMESTAMP WHERE id=?
        ''', (user[0],))
        conn.commit()
        
        # Convert to dictionary
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
    # Create container for login form at the top
    container = st.container()
    
    with container:
        # Add some top padding using empty space
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Create the form centered at the top
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            
            # Logo and header
            st.markdown('<div class="logo-container">', unsafe_allow_html=True)
            st.markdown('<div class="logo">🤖</div>', unsafe_allow_html=True)
            st.markdown('<div class="logo-text">SmartChat AI</div>', unsafe_allow_html=True)
            st.markdown('<div class="logo-subtext">Sign in to access your intelligent assistant</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Tabs for Login/Register
            tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Register", "🔑 Forgot"])
            
            with tab1:
                st.subheader("Login to Your Account")
                
                with st.form("login_form", clear_on_submit=False):
                    email = st.text_input("📧 Email Address", placeholder="Enter your email")
                    password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                    remember_me = st.checkbox("Remember me")
                    
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
                                
                                # Load chat history from database
                                history = get_user_chat_history(user_data['id'])
                                st.session_state.chat_messages = []
                                for user_msg, bot_resp, timestamp in reversed(history):
                                    st.session_state.chat_messages.append({"role": "user", "content": user_msg})
                                    st.session_state.chat_messages.append({"role": "assistant", "content": bot_resp})
                                
                                st.success("✅ Login successful!")
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Invalid email or password")
            
            with tab2:
                st.subheader("Create New Account")
                
                with st.form("register_form", clear_on_submit=False):
                    full_name = st.text_input("👤 Full Name", placeholder="Enter your full name")
                    username = st.text_input("👤 Username", placeholder="Choose a username")
                    email = st.text_input("📧 Email Address", placeholder="Enter your email")
                    password = st.text_input("🔒 Password", type="password", placeholder="Create a password")
                    confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
                    
                    register_submitted = st.form_submit_button("Create Account", use_container_width=True)
                    
                    if register_submitted:
                        if not all([full_name, username, email, password, confirm_password]):
                            st.error("⚠️ Please fill in all fields")
                        elif not validate_email(email):
                            st.error("⚠️ Please enter a valid email address")
                        elif password != confirm_password:
                            st.error("⚠️ Passwords do not match")
                        else:
                            is_valid, msg = validate_password(password)
                            if not is_valid:
                                st.error(f"⚠️ {msg}")
                            else:
                                success, message = register_user_db(email, username, password, full_name)
                                if success:
                                    st.success(f"✅ {message}")
                                    st.info("🎉 You can now login with your new account")
                                else:
                                    st.error(f"❌ {message}")
            
            with tab3:
                st.subheader("Reset Your Password")
                st.info("Enter your email to reset your password")
                
                with st.form("reset_form", clear_on_submit=False):
                    email = st.text_input("📧 Email Address", placeholder="Enter your registered email")
                    new_password = st.text_input("🔒 New Password", type="password", placeholder="Enter new password")
                    confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm new password")
                    
                    reset_submitted = st.form_submit_button("Reset Password", use_container_width=True)
                    
                    if reset_submitted:
                        if not email or not new_password or not confirm_password:
                            st.error("⚠️ Please fill in all fields")
                        elif not validate_email(email):
                            st.error("⚠️ Please enter a valid email address")
                        elif new_password != confirm_password:
                            st.error("⚠️ Passwords do not match")
                        else:
                            is_valid, msg = validate_password(new_password)
                            if not is_valid:
                                st.error(f"⚠️ {msg}")
                            else:
                                success = update_password(email, new_password)
                                if success:
                                    st.success("✅ Password updated successfully!")
                                else:
                                    st.error("❌ Email not found or update failed")
            
            # Social login section
            st.markdown('<div class="divider"><span>Or continue with</span></div>', unsafe_allow_html=True)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("Google", icon="🔵", use_container_width=True):
                    st.info("Google login would be implemented in production")
            with col_b:
                if st.button("Facebook", icon="🔵", use_container_width=True):
                    st.info("Facebook login would be implemented in production")
            with col_c:
                if st.button("GitHub", icon="🔵", use_container_width=True):
                    st.info("GitHub login would be implemented in production")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Add minimal content at the bottom to prevent excessive scrolling
    st.markdown("<br><br>", unsafe_allow_html=True)

# ========== DASHBOARD PAGE ==========
def dashboard():
    st.markdown("""
    <style>
        .dashboard-header {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            border: 1px solid #e2e8f0;
        }
        
        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Dashboard header
    st.markdown(f"""
    <div class="dashboard-header">
        <h2>👋 Welcome back, {st.session_state.user_data['full_name']}!</h2>
        <p>Ready to chat with your AI assistant? Ask me anything!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User info
    with st.expander("👤 Account Information", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Username", st.session_state.user_data['username'])
            st.metric("Email", st.session_state.user_data['email'])
        with col2:
            st.metric("Role", st.session_state.user_data['role'].title())
            st.metric("Member Since", st.session_state.user_data['created_at'][:10])
    
    # Chatbot interface
    st.markdown("---")
    st.subheader("💬 Chat Assistant")
    
    # Display chat messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            response = generate_response(prompt)
            st.markdown(response)
        
        # Add AI response
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        # Save to database
        save_chat_message(st.session_state.user_data['id'], prompt, response)
    
    # Sidebar with logout
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_data['full_name']}")
        st.markdown(f"**Role:** {st.session_state.user_data['role'].title()}")
        st.markdown(f"**Email:** {st.session_state.user_data['email']}")
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_data = {}
            st.session_state.chat_messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        
        # Clear chat history button
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            # Clear session state
            st.session_state.chat_messages = []
            st.success("Chat history cleared from this session!")
            st.rerun()

# ========== RESPONSE GENERATOR ==========
def generate_response(prompt):
    responses = {
        "hello": "👋 Hello! How can I assist you today?",
        "hi": "👋 Hi there! I'm your AI assistant. What can I do for you?",
        "help": "🤖 I can help you with various tasks:\n- Answer questions\n- Provide information\n- Assist with calculations\n- Offer recommendations\n\nWhat do you need help with?",
        "weather": "🌤️ I'm not connected to weather services yet, but you can ask me anything else!",
        "time": f"🕒 The current time is approximately {datetime.now().strftime('%H:%M')}",
        "date": f"📅 Today is {datetime.now().strftime('%B %d, %Y')}",
        "bye": "👋 Goodbye! Feel free to return anytime you need assistance!",
        "thanks": "😊 You're welcome! Is there anything else I can help you with?",
        "how are you": "🤖 I'm doing great, thanks for asking! Ready to help you with anything you need.",
        "what can you do": "🎯 I can help you with:\n• Answering questions\n• Providing explanations\n• Assisting with tasks\n• Offering suggestions\n• And much more!\n\nWhat would you like to know?"
    }
    
    prompt_lower = prompt.lower()
    for key in responses:
        if key in prompt_lower:
            return responses[key]
    
    # Default responses
    default_responses = [
        "🤔 I'm not sure I understand. Could you rephrase that?",
        "✨ That's an interesting question! Let me think about it...",
        "📚 I'm still learning, but I'll do my best to help you!",
        "💡 Here's what I think about that based on my knowledge:",
        "🔍 Let me analyze your question and provide the best answer I can.",
        "🎯 That's a great question! Here's what I know about that topic:"
    ]
    
    return f"{default_responses[hash(prompt) % len(default_responses)]}\n\n*You asked: '{prompt}'*"

# ========== MAIN APP ==========
def main():
    # Hide Streamlit default elements
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display:none;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    if st.session_state.authenticated:
        dashboard()
    else:
        login_page()

if __name__ == "__main__":
    main()