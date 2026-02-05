import streamlit as st
import sqlite3
import os
import base64

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

# ================= DATABASE =================
DB_FILE = "recipes.db"

def get_db():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            ingredients TEXT,
            steps TEXT,
            image TEXT,
            video TEXT,
            owner TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= FILE FOLDERS =================
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

# ================= USER FUNCTIONS =================
def get_user(username):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cur.fetchone()
    conn.close()
    return user

def create_user(username, password):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users VALUES (?, ?, 'user')",
        (username, password)
    )
    conn.commit()
    conn.close()

# ================= RECIPE FUNCTIONS =================
def add_recipe(name, ing, steps, img, vid, owner):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO recipes (name, ingredients, steps, image, video, owner)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, ing, steps, img, vid, owner))
    conn.commit()
    conn.close()

def get_all_recipes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM recipes")
    data = cur.fetchall()
    conn.close()
    return data

def update_recipe(rid, name, ing, steps):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE recipes
        SET name=?, ingredients=?, steps=?
        WHERE id=?
    """, (name, ing, steps, rid))
    conn.commit()
    conn.close()

def delete_recipe(rid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM recipes WHERE id=?", (rid,))
    conn.commit()
    conn.close()

# ================= AUTH PAGE =================
def auth_page():
    st.title("🔐 Login")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            user = get_user(u)
            if user and user[1] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = user[0]
                st.session_state.role = user[2]
                st.experimental_rerun()
            else:
                st.error("Invalid login")

    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        cp = st.text_input("Confirm Password", type="password")
        if st.button("Create Account"):
            if get_user(nu):
                st.error("Username already exists")
            elif np != cp:
                st.error("Passwords do not match")
            else:
                create_user(nu, np)
                st.success("Account created")

# ================= MAIN APP =================
def main_app():
    st.title("🍽️ Recipe App")
    st.caption(f"User: {st.session_state.current_user} | Role: {st.session_state.role}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    recipes = get_all_recipes()

    if st.session_state.role == "admin":
        menu = st.sidebar.selectbox(
            "Menu", ["Add Recipe", "View / Edit / Delete", "Search"]
        )
    else:
        menu = st.sidebar.selectbox(
            "Menu", ["Add Recipe", "My Recipes", "View Recipes", "Search"]
        )

    # ===== ADD RECIPE =====
    if menu == "Add Recipe":
        name = st.text_input("Recipe Name")
        ing = st.text_area("Ingredients")
        steps = st.text_area("Steps")
        image = st.file_uploader("Image", ["jpg", "png"])
        video = st.file_uploader("Video", ["mp4"])

        if st.button("Save"):
            img = vid = ""

            if image:
                img = f"{IMAGE_FOLDER}/{image.name}"
                with open(img, "wb") as f:
                    f.write(image.getbuffer())

            if video:
                vid = f"{VIDEO_FOLDER}/{video.name}"
                with open(vid, "wb") as f:
                    f.write(video.getbuffer())

            add_recipe(name, ing, steps, img, vid, st.session_state.current_user)
            st.success("Recipe saved permanently ✅")

    # ===== ADMIN EDIT =====
    elif menu == "View / Edit / Delete":
        if not recipes:
            st.info("No recipes found")
            st.stop()

        names = [r[1] for r in recipes]
        choice = st.selectbox("Select Recipe", names)
        r = next(x for x in recipes if x[1] == choice)

        new_name = st.text_input("Name", r[1])
        new_ing = st.text_area("Ingredients", r[2])
        new_steps = st.text_area("Steps", r[3])

        col1, col2 = st.columns(2)
        if col1.button("Update"):
            update_recipe(r[0], new_name, new_ing, new_steps)
            st.success("Updated")
            st.experimental_rerun()
        if col2.button("Delete"):
            delete_recipe(r[0])
            st.warning("Deleted")
            st.experimental_rerun()

    # ===== MY RECIPES =====
    elif menu == "My Recipes":
        my = [r for r in recipes if r[6] == st.session_state.current_user]
        if not my:
            st.info("No recipes uploaded by you")
            st.stop()

        names = [r[1] for r in my]
        choice = st.selectbox("Your Recipes", names)
        r = next(x for x in my if x[1] == choice)

        new_name = st.text_input("Name", r[1])
        new_ing = st.text_area("Ingredients", r[2])
        new_steps = st.text_area("Steps", r[3])

        col1, col2 = st.columns(2)
        if col1.button("Update"):
            update_recipe(r[0], new_name, new_ing, new_steps)
            st.success("Updated")
            st.experimental_rerun()
        if col2.button("Delete"):
            delete_recipe(r[0])
            st.warning("Deleted")
            st.experimental_rerun()

    # ===== VIEW =====
    elif menu == "View Recipes":
        for r in recipes:
            st.subheader(r[1])
            st.caption(f"By: {r[6]}")
            if r[4]:
                st.image(r[4], width=300)
            if r[5]:
                st.video(r[5])
            st.write(r[2])
            st.write(r[3])
            st.divider()

    # ===== SEARCH =====
    elif menu == "Search":
        q = st.text_input("Search recipe")
        for r in recipes:
            if q.lower() in r[1].lower():
                st.subheader(r[1])
                st.caption(f"By: {r[6]}")
                st.write(r[2])
                st.write(r[3])
                st.divider()

# ================= RUN =================
if st.session_state.logged_in:
    main_app()
else:
    auth_page()
