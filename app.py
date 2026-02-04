from ai_helper import generate_recipe

import streamlit as st
import json
import os
def set_bg(image):
    import base64
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
def input_style():
    st.markdown("""
    <style>
    input {
        background-color: white !important;
        color: black !important;
        border-radius: 8px !important;
        padding: 8px !important;
        border: 1px solid #ccc !important;
    }

    label {
        color: white !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)


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

# ---------- LOAD & SAVE USERS ----------
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------- LOGIN / SIGNUP ----------
def auth_page():
    set_bg("assets/login_bg.jpg")
    st.title("🔐 Login System")

    tab1, tab2 = st.tabs(["Login", "Create Account"])
    users = load_users()

    # ----- LOGIN -----
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in users and users[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.session_state.role = users[username]["role"]
                st.success("Login successful")
                st.rerun()

            else:
                st.error("Invalid credentials")

    # ----- SIGN UP -----
    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Create Account"):
            if not new_user or not new_pass:
                st.warning("All fields required")
            elif new_user in users:
                st.error("Username already exists")
            elif new_pass != confirm:
                st.error("Passwords do not match")
            else:
                users[new_user] = {
                    "password": new_pass,
                    "role": "user"
                }
                save_users(users)
                st.success("Account created. Please login.")

# ---------- RECIPES ----------
def load_recipes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_recipes(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------- MAIN APP ----------
def main_app():
    set_bg("assets/home_bg.jpg")
    st.title("🍽️ Recipe Card Finder")
    st.caption(f"User: {st.session_state.current_user} | Role: {st.session_state.role}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.session_state.role = ""
        st.rerun()


    recipes = load_recipes()

    # ----- MENU BASED ON ROLE -----
    if st.session_state.role == "admin":
        menu = st.sidebar.selectbox(
            "Menu",
            ["Add Recipe", "View / Edit / Delete", "Search"]
        )

    else:
        menu = st.sidebar.selectbox(
            "Menu",
            ["Add Recipe", "View Recipes", "Search"]
        )

    # ----- ADD RECIPE (ALL USERS) -----
    if menu == "Add Recipe":
        name = st.text_input("Recipe Name")
        ingredients = st.text_area("Ingredients")
        steps = st.text_area("Cooking Steps")

        image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
        video = st.file_uploader("Upload Video", type=["mp4"])

        if st.button("Save Recipe"):
            if name and ingredients and steps:
                img_path = ""
                vid_path = ""

                if image:
                    img_path = f"{IMAGE_FOLDER}/{image.name}"
                    with open(img_path, "wb") as f:
                        f.write(image.getbuffer())

                if video:
                    vid_path = f"{VIDEO_FOLDER}/{video.name}"
                    with open(vid_path, "wb") as f:
                        f.write(video.getbuffer())

                recipes.append({
                    "name": name,
                    "ingredients": ingredients,
                    "steps": steps,
                    "image": img_path,
                    "video": vid_path
                })
                save_recipes(recipes)
                st.success("Recipe added")
            else:
                st.warning("Fill all fields")

    # ----- VIEW / EDIT / DELETE (ADMIN ONLY) -----
    elif menu == "View / Edit / Delete":
        if recipes:
            names = [r["name"] for r in recipes]
            choice = st.selectbox("Select Recipe", names)
            recipe = next(r for r in recipes if r["name"] == choice)

            name = st.text_input("Name", recipe["name"])
            ing = st.text_area("Ingredients", recipe["ingredients"])
            steps = st.text_area("Steps", recipe["steps"])

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Update"):
                    recipe["name"] = name
                    recipe["ingredients"] = ing
                    recipe["steps"] = steps
                    save_recipes(recipes)
                    st.success("Updated")
                    st.experimental_rerun()

            with col2:
                if st.button("Delete"):
                    recipes.remove(recipe)
                    save_recipes(recipes)
                    st.warning("Deleted")
                    st.experimental_rerun()
        else:
            st.info("No recipes")

    # ----- VIEW ONLY (NORMAL USER) -----
    elif menu == "View Recipes":
        for r in recipes:
            st.subheader(r["name"])
            if r["image"]:
                st.image(r["image"], width=300)
            if r["video"]:
                st.video(r["video"])
            st.write(r["ingredients"])
            st.write(r["steps"])
            st.divider()

    # ----- SEARCH (ALL USERS) -----
    elif menu == "Search":
        q = st.text_input("Search")
        for r in recipes:
            if q.lower() in r["name"].lower() or q.lower() in r["ingredients"].lower():
                st.subheader(r["name"])
                if r["image"]:
                    st.image(r["image"], width=300)
                if r["video"]:
                    st.video(r["video"])
                st.write(r["ingredients"])
                st.write(r["steps"])
                st.divider()
                st.subheader("AI Test")

user_text = st.text_input("Type anything")

if st.button("Use AI"):
    result = generate_recipe(user_text)
    st.write(result)


# ---------- RUN ----------
if st.session_state.logged_in:
    main_app()
else:
    auth_page()

