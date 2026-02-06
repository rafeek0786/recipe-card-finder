import streamlit as st
import json
import os
import base64
import hashlib
import uuid

from db import init_db, load_recipes, save_recipes
from ai_bot import ai_suggest

# ================= CONFIG =================
USER_FILE = "users.json"
IMAGE_FOLDER = "images"
VIDEO_FOLDER = "videos"

os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "open_ai" not in st.session_state:
    st.session_state.open_ai = False

# ================= SECURITY =================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ================= USERS =================
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {
        "admin": {"password": "admin123", "role": "admin"}
    }

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ================= AUTH =================
def auth_page():
    st.title("🔐 Login")
    users = load_users()

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if u in users:
                if users[u]["role"] == "admin":
                    valid = users[u]["password"] == p
                else:
                    valid = users[u]["password"] == hash_password(p)

                if valid:
                    st.session_state.logged_in = True
                    st.session_state.current_user = u
                    st.session_state.role = users[u]["role"]
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Invalid username or password")

    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            if nu in users:
                st.error("User already exists")
            else:
                users[nu] = {
                    "password": hash_password(np),
                    "role": "user"
                }
                save_users(users)
                st.success("Account created successfully")

# ================= MAIN APP =================
def main_app():
    st.title("🍽️ Recipe Card")

    # ---------- FLOATING AI BUTTON ----------
    st.markdown("""
    <style>
    .ai-float-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background-color: #ff4b4b;
        color: white;
        width: 65px;
        height: 65px;
        border-radius: 50%;
        font-size: 32px;
        text-align: center;
        line-height: 65px;
        cursor: pointer;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        z-index: 9999;
    }
    .ai-float-btn:hover {
        background-color: #ff0000;
    }
    </style>

    <div class="ai-float-btn" onclick="document.getElementById('aiBtn').click()">
    🤖
    </div>
    """, unsafe_allow_html=True)

    # ---------- FIXED LINE 147 ----------
    if st.button("AI", key="aiBtn"):
        st.session_state.open_ai = True

    st.sidebar.markdown(f"""
    👤 **User:** {st.session_state.current_user}  
    🛡️ **Role:** {st.session_state.role}
    """)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    recipes = load_recipes()

    # ---------- FIXED LINE 148 ----------
    if st.session_state.role == "admin":
        menu = st.sidebar.selectbox(
            "Menu",
            ["Add Recipe", "View / Edit / Delete", "Search", "AI Assistant"],
            index=3 if st.session_state.open_ai else 0
        )
    else:
        menu = st.sidebar.selectbox(
            "Menu",
            ["Add Recipe", "My Recipes", "View Recipes", "Search", "AI Assistant"],
            index=4 if st.session_state.open_ai else 0
        )

    if menu != "AI Assistant":
        st.session_state.open_ai = False

    # ================= AI =================
    if menu == "AI Assistant":
        st.subheader("🤖 AI Recipe Assistant")
        q = st.text_input("Ask about recipes")
        if q:
            st.markdown(ai_suggest(q))

# ================= RUN =================
init_db()

if not st.session_state.logged_in:
    auth_page()
else:
    main_app()
