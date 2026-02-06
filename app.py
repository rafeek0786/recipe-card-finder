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

init_db()

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "selected_recipe" not in st.session_state:
    st.session_state.selected_recipe = None

# ================= BACKGROUND =================
def set_bg(image):
    if not os.path.exists(image):
        return
    with open(image, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ================= SECURITY =================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ================= USERS =================
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ================= AUTH =================
def auth_page():
    set_bg("assets/login_bg.jpg")
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
        cp = st.text_input("Confirm Password", type="password")

        if st.button("Create Account"):
            if nu in users:
                st.error("Username already exists")
            elif np != cp:
                st.error("Passwords do not match")
            elif not nu or not np:
                st.error("All fields required")
            else:
                users[nu] = {
                    "password": hash_password(np),
                    "role": "user"
                }
                save_users(users)
                st.success("Account created successfully")

# ================= MAIN APP =================
def main_app():
    set_bg("assets/home_bg.jpg")
    st.title("🍽️ Recipe Card")

    st.sidebar.markdown(f"""
    👤 **User:** {st.session_state.current_user}  
    🛡️ **Role:** {st.session_state.role}
    """)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    recipes = load_recipes()

    # ================= MENU =================
    if st.session_state.role == "admin":
        menu = st.sidebar.selectbox(
            "Menu", ["Add Recipe", "View / Edit / Delete", "Search", "AI Assistant"]
        )
    else:
        menu = st.sidebar.selectbox(
            "Menu", ["Add Recipe", "My Recipes", "View Recipes", "Search", "AI Assistant"]
        )

    # ================= VIEW RECIPES =================
    if menu == "View Recipes":
        if st.session_state.selected_recipe:
            recipes = [
                r for r in recipes
                if r["name"] == st.session_state.selected_recipe
            ]
            st.session_state.selected_recipe = None

        for r in recipes:
            st.subheader(r["name"])
            st.caption(f"By {r['owner']}")

            if r["image"] and os.path.exists(r["image"]):
                st.image(r["image"], width=300)

            if r["video"] and os.path.exists(r["video"]):
                st.video(r["video"])

            st.write(r["ingredients"])
            st.write(r["steps"])
            st.divider()

    # ================= AI ASSISTANT =================
    elif menu == "AI Assistant":
        st.subheader("🤖 AI Recipe Assistant")
        st.caption("Ask questions based on your recipe database")

        user_query = st.text_input("Ask me anything about your recipes")

        if user_query:
            with st.spinner("Thinking..."):
                suggested = ai_suggest(user_query)

            if suggested:
                st.markdown("✨ Suggested Recipes")
                for name in suggested:
                    if st.button(name, key=f"ai_{name}"):
                        st.session_state.selected_recipe = name
                        st.rerun()
            else:
                st.info("No related recipes found.")

# ================= RUN =================
if st.session_state.logged_in:
    main_app()
else:
    auth_page()
