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
if "update_msg" not in st.session_state:
    st.session_state.update_msg = False
if "delete_msg" not in st.session_state:
    st.session_state.delete_msg = False

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

    # ================= ADD RECIPE =================
    if menu == "Add Recipe":
        with st.form("add_recipe", clear_on_submit=True):
            name = st.text_input("Recipe Name")
            ing = st.text_area("Ingredients")
            steps = st.text_area("Steps")
            image = st.file_uploader("Image", ["jpg", "png"])
            video = st.file_uploader("Video", ["mp4"])
            submit = st.form_submit_button("Save")

        if submit:
            if not name or not ing or not steps:
                st.error("All fields required")
                return

            if any(r["name"] == name for r in recipes):
                st.error("Recipe name already exists")
                return

            img = vid = ""
            if image:
                img_name = f"{uuid.uuid4()}_{image.name}"
                img = f"{IMAGE_FOLDER}/{img_name}"
                with open(img, "wb") as f:
                    f.write(image.getbuffer())

            if video:
                vid_name = f"{uuid.uuid4()}_{video.name}"
                vid = f"{VIDEO_FOLDER}/{vid_name}"
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

    # ================= VIEW / EDIT / DELETE & MY RECIPES =================
    elif menu in ["View / Edit / Delete", "My Recipes"]:
        data = recipes if menu == "View / Edit / Delete" else [
            r for r in recipes if r["owner"] == st.session_state.current_user
        ]

        if not data:
            st.info("No recipes available")
            return

        if st.session_state.update_msg:
            st.success("✅ Updated successfully")
            st.session_state.update_msg = False

        if st.session_state.delete_msg:
            st.success("🗑️ Deleted successfully")
            st.session_state.delete_msg = False

        choice = st.selectbox("Select Recipe", [r["name"] for r in data])
        r = next(x for x in recipes if x["name"] == choice)

        if r["image"] and os.path.exists(r["image"]):
            st.image(r["image"], width=300)

        if r["video"] and os.path.exists(r["video"]):
            st.video(r["video"])

        new_name = st.text_input("Name", r["name"])
        new_ing = st.text_area("Ingredients", r["ingredients"])
        new_steps = st.text_area("Steps", r["steps"])

        col1, col2 = st.columns(2)
        if col1.button("Update"):
            r["name"] = new_name
            r["ingredients"] = new_ing
            r["steps"] = new_steps
            save_recipes(recipes)
            st.session_state.update_msg = True
            st.rerun()

        if col2.button("Delete"):
            recipes[:] = [x for x in recipes if x["name"] != r["name"]]
            save_recipes(recipes)
            st.session_state.delete_msg = True
            st.rerun()

    # ================= VIEW RECIPES =================
    elif menu == "View Recipes":
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

    # ================= SEARCH =================
    elif menu == "Search":
        q = st.text_input("Search recipes")
        if st.button("Search") and q:
            found = False
            for r in recipes:
                if q.lower() in (r["name"] + r["ingredients"] + r["steps"]).lower():
                    found = True
                    st.subheader(r["name"])

                    if r["image"] and os.path.exists(r["image"]):
                        st.image(r["image"], width=300)

                    if r["video"] and os.path.exists(r["video"]):
                        st.video(r["video"])

                    st.write(r["ingredients"])
                    st.write(r["steps"])
                    st.divider()

            if not found:
                st.warning("No matching recipes found")

    # ================= AI ASSISTANT (ENTER ONLY) =================
    elif menu == "AI Assistant":
        st.subheader("🤖 AI Recipe Assistant")
        st.caption("Type your question and press Enter")

        with st.form("ai_form", clear_on_submit=False):
            user_query = st.text_input("Ask me anything about your recipes")
            submitted = st.form_submit_button("")

        if submitted and user_query:
            with st.spinner("Thinking..."):
                st.markdown(ai_suggest(user_query))


# ================= RUN =================
if st.session_state.logged_in:
    main_app()
else:
    auth_page()
