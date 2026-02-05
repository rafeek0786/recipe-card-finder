import streamlit as st
import json
import os
import base64
import hashlib
import uuid

# ---------- FILES ----------
USER_FILE = "users.json"
DATA_FILE = "recipes.json"
IMAGE_FOLDER = "images"
VIDEO_FOLDER = "videos"

os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# ---------- BACKGROUND (OPTIMIZED ONLY) ----------
@st.cache_data
def load_bg(image):
    if not os.path.exists(image):
        return ""
    with open(image, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_bg(image):
    encoded = load_bg(image)
    if not encoded:
        return
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

# ---------- SECURITY (UNCHANGED LOGIC) ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------- USERS ----------
@st.cache_data
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)
    load_users.clear()  # cache clear ONLY

# ---------- RECIPES ----------
@st.cache_data
def load_recipes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_recipes(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
    load_recipes.clear()  # cache clear ONLY

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
                    st.error("Invalid login")
            else:
                st.error("Invalid login")

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
    st.title("🍽️ Recipe App")
    st.caption(f"User: {st.session_state.current_user} | Role: {st.session_state.role}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.session_state.role = ""
        st.rerun()

    recipes = load_recipes()

    # ---------- MENU ----------
    if st.session_state.role == "admin":
        menu = st.sidebar.selectbox(
            "Menu", ["Add Recipe", "View / Edit / Delete", "Search"]
        )
    else:
        menu = st.sidebar.selectbox(
            "Menu", ["Add Recipe", "My Recipes", "View Recipes", "Search"]
        )

    # ---------- ADD RECIPE ----------
    if menu == "Add Recipe":
        name = st.text_input("Recipe Name")
        ing = st.text_area("Ingredients")
        steps = st.text_area("Steps")
        image = st.file_uploader("Image", ["jpg", "png"])
        video = st.file_uploader("Video", ["mp4"])

        if st.button("Save"):
            img = vid = ""
            if image:
                img = f"{IMAGE_FOLDER}/{uuid.uuid4()}_{image.name}"
                with open(img, "wb") as f:
                    f.write(image.getbuffer())
            if video:
                vid = f"{VIDEO_FOLDER}/{uuid.uuid4()}_{video.name}"
                with open(vid, "wb") as f:
                    f.write(video.getbuffer())

            recipes.append({
                "name": name,
                "ingredients": ing,
                "steps": steps,
                "image": img,
                "video": vid,
                "owner": st.session_state.current_user
            })

            save_recipes(recipes)
            st.success("Recipe added successfully")
            st.rerun()

    # ---------- ADMIN VIEW / EDIT / DELETE ----------
    elif menu == "View / Edit / Delete":
        if not recipes:
            st.info("No recipes available")
            return

        names = [r["name"] for r in recipes]
        choice = st.selectbox("Select Recipe", names)
        r = next(x for x in recipes if x["name"] == choice)

        r["name"] = st.text_input("Name", r["name"])
        r["ingredients"] = st.text_area("Ingredients", r["ingredients"])
        r["steps"] = st.text_area("Steps", r["steps"])

        col1, col2 = st.columns(2)
        if col1.button("Update"):
            save_recipes(recipes)
            st.success("Updated successfully")
            st.rerun()

        if col2.button("Delete"):
            recipes.remove(r)
            save_recipes(recipes)
            st.warning("Deleted successfully")
            st.rerun()

    # ---------- MY RECIPES ----------
    elif menu == "My Recipes":
        my = [r for r in recipes if r["owner"] == st.session_state.current_user]
        if not my:
            st.info("No recipes uploaded by you")
            return

        names = [r["name"] for r in my]
        choice = st.selectbox("Your Recipes", names)
        r = next(x for x in my if x["name"] == choice)

        r["name"] = st.text_input("Name", r["name"])
        r["ingredients"] = st.text_area("Ingredients", r["ingredients"])
        r["steps"] = st.text_area("Steps", r["steps"])

        col1, col2 = st.columns(2)
        if col1.button("Update"):
            save_recipes(recipes)
            st.success("Updated successfully")
            st.rerun()

        if col2.button("Delete"):
            recipes.remove(r)
            save_recipes(recipes)
            st.warning("Deleted successfully")
            st.rerun()

    # ---------- VIEW RECIPES ----------
    elif menu == "View Recipes":
        if not recipes:
            st.info("No recipes found")
            return

        for r in recipes:
            st.subheader(r["name"])
            st.caption(f"By: {r['owner']}")
            if r["image"]:
                st.image(r["image"], width=300)
            if r["video"]:
                st.video(r["video"])
            st.write("**Ingredients:**")
            st.write(r["ingredients"])
            st.write("**Steps:**")
            st.write(r["steps"])
            st.divider()

    # ---------- SEARCH ----------
    elif menu == "Search":
        q = st.text_input("Search by recipe name")
        for r in recipes:
            if q.lower() in r["name"].lower():
                st.subheader(r["name"])
                st.caption(f"By: {r['owner']}")
                st.write(r["ingredients"])
                st.write(r["steps"])
                st.divider()

# ---------- RUN ----------
if st.session_state.logged_in:
    main_app()
else:
    auth_page()
