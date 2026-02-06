import streamlit as st
import json
import os
import base64
import hashlib
import uuid

from db import init_db, load_recipes, save_recipes
from ai_bot import ai_suggest

USER_FILE = "users.json"
IMAGE_FOLDER = "images"
VIDEO_FOLDER = "videos"

os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

init_db()

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# ---------- BG ----------
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

# ---------- USERS ----------
def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE) as f:
            return json.load(f)
    return {}

def save_users(u):
    with open(USER_FILE, "w") as f:
        json.dump(u, f, indent=4)

# ---------- AUTH ----------
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
                valid = users[u]["password"] == (p if users[u]["role"] == "admin" else hash_password(p))
                if valid:
                    st.session_state.logged_in = True
                    st.session_state.current_user = u
                    st.session_state.role = users[u]["role"]
                    st.rerun()
            st.error("Invalid credentials")

    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        cp = st.text_input("Confirm Password", type="password")
        if st.button("Create Account"):
            if nu in users:
                st.error("Username exists")
            elif np != cp:
                st.error("Passwords mismatch")
            else:
                users[nu] = {"password": hash_password(np), "role": "user"}
                save_users(users)
                st.success("Account created")

# ---------- MAIN ----------
def main_app():
    set_bg("assets/home_bg.jpg")
    st.title("🍽️ Recipe Card")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    recipes = load_recipes()

    # 🔹 ONLY ADDITION (safe)
    selected_recipe = st.query_params.get("view_recipe", None)

    # ---------- MENU (ORIGINAL LOGIC) ----------
    if st.session_state.role == "admin":
        menu = st.sidebar.selectbox(
            "Menu", ["Add Recipe", "View / Edit / Delete", "Search", "AI Assistant"]
        )
    else:
        menu = st.sidebar.selectbox(
            "Menu", ["Add Recipe", "My Recipes", "View Recipes", "Search", "AI Assistant"]
        )

    # ---------- ADD RECIPE ----------
    if menu == "Add Recipe":
        with st.form("add_recipe", clear_on_submit=True):
            name = st.text_input("Recipe Name")
            ing = st.text_area("Ingredients")
            steps = st.text_area("Steps")
            image = st.file_uploader("Image", ["jpg", "png"])
            video = st.file_uploader("Video", ["mp4"])
            submit = st.form_submit_button("Save")

        if submit and name and ing and steps:
            img = vid = ""
            if image:
                img = f"{IMAGE_FOLDER}/{uuid.uuid4()}_{image.name}"
                open(img, "wb").write(image.getbuffer())
            if video:
                vid = f"{VIDEO_FOLDER}/{uuid.uuid4()}_{video.name}"
                open(vid, "wb").write(video.getbuffer())

            recipes.append({
                "name": name,
                "ingredients": ing,
                "steps": steps,
                "image": img,
                "video": vid,
                "owner": st.session_state.current_user
            })
            save_recipes(recipes)
            st.success("Recipe added")

    # ---------- VIEW RECIPES (AI LINK WORKS HERE) ----------
    elif menu == "View Recipes":
        for r in recipes:
            if selected_recipe and r["name"] != selected_recipe:
                continue

            st.subheader(r["name"])
            st.caption(f"By {r['owner']}")
            if r["image"] and os.path.exists(r["image"]):
                st.image(r["image"], width=300)
            if r["video"] and os.path.exists(r["video"]):
                st.video(r["video"])
            st.write(r["ingredients"])
            st.write(r["steps"])
            st.divider()

        if selected_recipe:
            st.query_params.clear()

    # ---------- SEARCH ----------
    elif menu == "Search":
        q = st.text_input("Search")
        for r in recipes:
            if q.lower() in (r["name"] + r["ingredients"] + r["steps"]).lower():
                st.subheader(r["name"])
                st.write(r["ingredients"])
                st.write(r["steps"])
                st.divider()

    # ---------- AI ----------
    elif menu == "AI Assistant":
        st.subheader("🤖 AI Assistant")
        q = st.text_input("Ask using ingredients")
        if q:
            st.markdown(ai_suggest(q))

# ---------- RUN ----------
if st.session_state.logged_in:
    main_app()
else:
    auth_page()
