import streamlit as st
import google.generativeai as genai
import speech_recognition as sr  # Voice Input
import cv2  # Camera Integration
import easyocr  # EasyOCR for Handwritten Text Recognition
import sqlite3  # User authentication & storage
from uuid import uuid4  # Unique ID for versioning
import os

# --- API CONFIGURATION ---
GEMINI_API_KEY = "AIzaSyDOvM48IMxod_4SvEttajKXcVDblmKHyPk"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

# --- DATABASE FOR USER AUTHENTICATION ---
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def login_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

# --- INITIALIZE DATABASE ---
init_db()

# --- USER AUTHENTICATION PAGE ---
def login_page():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Lobster&family=Poppins:wght@400;700&display=swap');

            @keyframes glowing {
                0% { text-shadow: 0 0 5px #ff5e62, 0 0 10px #ff9966; }
                50% { text-shadow: 0 0 20px #ff5e62, 0 0 40px #ff9966; }
                100% { text-shadow: 0 0 5px #ff5e62, 0 0 10px #ff9966; }
            }

            .title {
                text-align: center;
                font-family: 'Orbitron', sans-serif;
                font-size: 50px;
                font-weight: bold;
                background: linear-gradient(to right, #ff9966, #ff5e62);
                -webkit-background-clip: text;
                color: transparent;
                animation: glowing 2s infinite alternate;
            }

            .subtitle {
                text-align: center;
                font-family: 'Lobster', cursive;
                font-size: 24px;
                color: #444;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }

            .description {
                text-align: center;
                font-family: 'Poppins', sans-serif;
                font-size: 18px;
                color: #666;
            }
        </style>

        <div class="title">UwU Code Generator</div>
        <div class="subtitle">Unlock the magic of UwU coding!</div>
        <div class="description">Login or Register to start your UwU coding journey!</div>
    """, unsafe_allow_html=True)

    st.subheader("🔑 Login Credentials")
    username = st.text_input("👤 Username", placeholder="Enter your username")
    password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
    
    login = st.button("🔓 Login", use_container_width=True)
    register = st.button("📝 Register", use_container_width=True)
    
    if login:
        if login_user(username, password):
            # Store authentication status in session state
            st.session_state["authenticated"] = True
            st.success("✅ Logged in successfully!")
            # Update the session state to force a rerun
            st.session_state["page_loaded"] = True
        else:
            st.error("❌ Invalid username or password")
    
    if register:
        if register_user(username, password):
            st.success("✅ Registered successfully! Please login.")
        else:
            st.error("❌ Username already exists!")

# --- CODE GENERATION FUNCTION ---
def generate_code_in_language(prompt, language):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Write {language} code for: {prompt}")
        return response.text
    except Exception as e:
        return f"Error generating code: {str(e)}"

# --- MAIN APP ---
def main():
    st.markdown("""
        <style>
            .stButton button { 
                background: linear-gradient(to right, #ff7f50, #ff4f81);
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                transition: 0.3s;
            }
            .stButton button:hover {
                background: linear-gradient(to right, #ff4f81, #ff7f50);
            }
        </style>
    """, unsafe_allow_html=True)

    # Check if the user is authenticated, if not show the login page
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        login_page()
        return
    
    # --- Dynamic & Stylish Title ---
    st.markdown("""
        <h1 style='text-align: center; 
                   font-family: "Orbitron", sans-serif; 
                   font-size: 70px; 
                   font-weight: bold;
                   color: #ff5e62;
                   text-shadow: 4px 4px 10px rgba(0,0,0,0.3);
                   animation: glowing 2s ease-in-out infinite;'>
            🚀 UwU Code Generator X 🚀
        </h1>
    """, unsafe_allow_html=True)
    
    language_choice = st.selectbox("🌍 Choose Programming Language", ["UwU", "Python", "JavaScript", "Rust", "C++", "C++ to UwU"], index=0)
    user_prompt = st.text_area("📝 Describe your vision for UwU code 🚀", placeholder="e.g. Print 'Hello, World!' in UwU language", height=150)

    # Ensure the user prompt is saved even if it is empty initially
    if "user_prompt" not in st.session_state:
        st.session_state.user_prompt = ""

    # Update the prompt from text input
    if user_prompt:
        st.session_state.user_prompt = user_prompt
    
    col1, col2 = st.columns(2)
    
    # --- Voice Input ---
    with col1:
        if st.button("🎙 Voice Input"):
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("🎙 Speak now...")
                try:
                    audio = recognizer.listen(source, timeout=5)
                    text = recognizer.recognize_google(audio)
                    # Update user_prompt in session state
                    st.session_state.user_prompt += " " + text
                    st.text_area("📝 Updated Prompt from Voice:", st.session_state.user_prompt, height=150)
                except Exception as e:
                    st.error(f"❌ Speech recognition failed: {str(e)}")
    
    # --- Camera Feed for Image Capture ---
    with col2:
        if "capturing" not in st.session_state or not st.session_state["capturing"]:
            if st.button("📸 Open Camera"):
                # Start camera feed
                st.session_state["capturing"] = True
                st.text("Camera is now open, press 'Capture Photo' to take a picture.")
            else:
                st.text("Click 'Open Camera' to start the camera feed.")

        if "capturing" in st.session_state and st.session_state["capturing"]:
            if st.button("Capture Photo"):
                cap = cv2.VideoCapture(0)
                ret, frame = cap.read()
                cap.release()
                if ret:
                    st.image(frame, channels="BGR", caption="📸 Captured Image")
                    try:
                        # Use EasyOCR for text extraction
                        reader = easyocr.Reader(['en'])
                        result = reader.readtext(frame)
                        text = " ".join([res[1] for res in result])
                        st.session_state.user_prompt += " " + text
                        st.text_area("📝 Extracted Text from Image:", st.session_state.user_prompt, height=150)
                    except Exception as e:
                        st.error(f"❌ OCR Failed: {e}")
                else:
                    st.error("❌ Failed to capture image")
    
    # --- Code Generation ---
    if st.button("✨ Generate Code!"):
        if st.session_state.user_prompt:
            generated_code = generate_code_in_language(st.session_state.user_prompt, language_choice)
            st.code(generated_code, language=language_choice.lower(), line_numbers=True)
        else:
            st.warning("⚠ Please enter a description!")
    
    # --- Footer ---
    st.markdown("""
        <div style="text-align:center; padding-top:20px;">
            <b>Made with ❤ for UwU lovers! By Nitish, Shivam, Shubham, Sourish ✨</b>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
