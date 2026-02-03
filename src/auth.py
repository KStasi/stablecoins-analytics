"""Authentication utilities for Streamlit app."""
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace this with a secure method in production
CORRECT_PASSWORD = os.getenv("STREAMLIT_PASSWORD")

# TODO: remove this line in production
# st.session_state["authenticated"] = True  # Bypass authentication for easier testing


def login():
    """Display login form and handle authentication."""
    st.title("🔐 Login Required")
    password = st.text_input("Enter password:", type="password")
    if st.button("Submit"):
        if password == CORRECT_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ Incorrect password. Please try again.")


def require_auth():
    """Check if user is authenticated, show login if not."""
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        # Hide sidebar, header, and navigation before authentication
        hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] {visibility: hidden;}
        [data-testid="stSidebarNav"] {visibility: hidden;}
        </style>
        """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)
        login()
        st.stop()
