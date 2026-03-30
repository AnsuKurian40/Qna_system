import streamlit as st

# Page configuration
st.set_page_config(
    page_title="SmartChat AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    # Check if user is authenticated
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        # Redirect to chatbot
        st.switch_page("pages/chatbot.py")
    else:
        # Redirect to login
        st.switch_page("pages/login.py")

if __name__ == "__main__":
    main()