import streamlit as st
import json
import os
import sqlite3
import base64

# ---------- BACKGROUND ----------
def set_bg(image):
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

# ---------- FILES ----------
USER_FILE = "users.json"
IMAGE_FOLDER = "images"
VIDEO_FOLDER = "videos"
DB_FILE = "recipes.db"

os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# ---------- USERS ----------
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            ingredients TEXT,
            steps TEXT,
            image TEXT,
            video TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_recipe(name, ingredients, steps, image, video):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO recipes (name, ingredients, steps, image, video) VALUES (?, ?, ?, ?, ?)",
        (name, ingredients, steps, image, video)
    )
    conn.commit()
    conn.close()

def get_recipes():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM recipes")
    data = c.fetchall()
    conn.close()
    return data

# 🔐 IMPORTANT: DATABASE INITIALIZED ON APP START
init_db()

# ---------- AUTH ----------
def auth_page():
    set_bg("assets/login_bg.jpg")
    st.title("🔐 Login System")

    tab1, tab2 = st.tabs(["Login", "Create Account"])
    users = load_users()

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if u in users and users[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.session_state.role = users[u]["role"]
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        cp = st.text_input("Confirm Password", type="password")

        if st.button("Create Account"):
            if nu in users:
                st.error("Username exists")
            elif np != cp:
                st.error("Passwords do not match")
            else:
                users[nu] = {"password": np, "role": "user"}
                save_users(users)
                st.success("Account created")

# ---------- MAIN APP ----------
def main_app():
    set_bg("assets/home_bg.jpg")
    st.title("🍽️ Recipe Card Finder")
    st.caption(f"User: {st.session_state.current_user} | Role: {st.session_state.role}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    recipes = get_recipes()

    if st.session_state.role == "admin":
        menu = st.sidebar.selectbox(
            "Menu",
            ["Add Recipe", "View Recipes", "Edit / Delete Recipes", "Search"]
        )
    else:
        menu = st.sidebar.selectbox(
            "Menu",
            ["Add Recipe", "View Recipes", "Search"]
        )

    if menu == "Add Recipe":
        name = st.text_input("Recipe Name")
        ingredients = st.text_area("Ingredients")
        steps = st.text_area("Steps")

        image = st.file_uploader("Image", ["jpg", "png", "jpeg"])
        video = st.file_uploader("Video", ["mp4"])

        if st.button("Save Recipe"):
            if name and ingredients and steps:
                img_path, vid_path = "", ""

                if image:
                    img_path = f"{IMAGE_FOLDER}/{image.name}"
                    with open(img_path, "wb") as f:
                        f.write(image.getbuffer())

                if video:
                    vid_path = f"{VIDEO_FOLDER}/{video.name}"
                    with open(vid_path, "wb") as f:
                        f.write(video.getbuffer())

                add_recipe(name, ingredients, steps, img_path, vid_path)
                st.success("Recipe saved permanently")
            else:
                st.warning("Fill all fields")

    elif menu == "View Recipes":
        for r in recipes:
            st.subheader(r[1])
            if r[4]:
                st.image(r[4], width=300)
            if r[5]:
                st.video(r[5])
            st.write(r[2])
            st.write(r[3])
            st.divider()

    elif menu == "Edit / Delete Recipes" and st.session_state.role == "admin":
        if not recipes:
            st.info("No recipes available")
            return

        names = [r[1] for r in recipes]
        selected = st.selectbox("Select Recipe", names)
        recipe = next(r for r in recipes if r[1] == selected)

        new_name = st.text_input("Recipe Name", recipe[1])
        new_ing = st.text_area("Ingredients", recipe[2])
        new_steps = st.text_area("Steps", recipe[3])

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Update Recipe"):
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute(
                    "UPDATE recipes SET name=?, ingredients=?, steps=? WHERE id=?",
                    (new_name, new_ing, new_steps, recipe[0])
                )
                conn.commit()
                conn.close()
                st.success("Recipe updated")
                st.rerun()

        with col2:
            if st.button("Delete Recipe"):
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("DELETE FROM recipes WHERE id=?", (recipe[0],))
                conn.commit()
                conn.close()
                st.warning("Recipe deleted")
                st.rerun()

    elif menu == "Search":
        q = st.text_input("Search")
        for r in recipes:
            if q.lower() in r[1].lower() or q.lower() in r[2].lower():
                st.subheader(r[1])
                st.write(r[2])
                st.write(r[3])
                st.divider()

# ---------- RUN ----------
if st.session_state.logged_in:
    main_app()
else:
    auth_page()
