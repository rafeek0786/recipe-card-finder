import streamlit as st
import json
import os

# ---------------- LOGIN CREDENTIALS ----------------
USERNAME = "admin"
PASSWORD = "admin123"

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN PAGE ----------------
def login_page():
    st.title("🔐 Login")
    st.write("Please login to continue")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# ---------------- MAIN APP ----------------
def main_app():
    # CONFIG
    st.set_page_config(page_title="Recipe Card Finder", layout="centered")

    DATA_FILE = "recipes.json"
    IMAGE_FOLDER = "images"
    VIDEO_FOLDER = "videos"

    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    os.makedirs(VIDEO_FOLDER, exist_ok=True)

    # DATA FUNCTIONS
    def load_recipes():
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return []

    def save_recipes(data):
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    recipes = load_recipes()

    # UI
    st.title("🍽️ Recipe Card Finder")
    st.caption("Login Protected Application")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    menu = st.sidebar.selectbox(
        "Menu",
        ["Add Recipe", "View / Edit / Delete", "Search Recipe"]
    )

    # -------- ADD RECIPE --------
    if menu == "Add Recipe":
        st.subheader("Add New Recipe")

        name = st.text_input("Recipe Name")
        ingredients = st.text_area("Ingredients")
        steps = st.text_area("Cooking Steps")

        image = st.file_uploader("Upload Recipe Image", type=["jpg", "png", "jpeg"])
        video = st.file_uploader("Upload Cooking Video (MP4)", type=["mp4"])

        if st.button("Save Recipe"):
            if not name or not ingredients or not steps:
                st.warning("Please fill all fields")
            else:
                image_path = ""
                video_path = ""

                if image:
                    image_path = f"{IMAGE_FOLDER}/{image.name}"
                    with open(image_path, "wb") as f:
                        f.write(image.getbuffer())

                if video:
                    video_path = f"{VIDEO_FOLDER}/{video.name}"
                    with open(video_path, "wb") as f:
                        f.write(video.getbuffer())

                recipes.append({
                    "name": name,
                    "ingredients": ingredients,
                    "steps": steps,
                    "image": image_path,
                    "video": video_path
                })

                save_recipes(recipes)
                st.success("Recipe added successfully!")

    # -------- VIEW / EDIT / DELETE --------
    elif menu == "View / Edit / Delete":
        st.subheader("Manage Recipes")

        if not recipes:
            st.info("No recipes available")
        else:
            recipe_names = [r["name"] for r in recipes]
            selected = st.selectbox("Select a recipe", recipe_names)

            recipe = next(r for r in recipes if r["name"] == selected)

            if recipe["image"]:
                st.image(recipe["image"], width=300)
            if recipe["video"]:
                st.video(recipe["video"])

            new_name = st.text_input("Edit Recipe Name", recipe["name"])
            new_ingredients = st.text_area("Edit Ingredients", recipe["ingredients"])
            new_steps = st.text_area("Edit Cooking Steps", recipe["steps"])

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Update Recipe"):
                    recipe["name"] = new_name
                    recipe["ingredients"] = new_ingredients
                    recipe["steps"] = new_steps
                    save_recipes(recipes)
                    st.success("Recipe updated!")
                    st.experimental_rerun()

            with col2:
                if st.button("Delete Recipe"):
                    recipes.remove(recipe)
                    save_recipes(recipes)
                    st.warning("Recipe deleted!")
                    st.experimental_rerun()

    # -------- SEARCH --------
    elif menu == "Search Recipe":
        st.subheader("Search Recipe")

        query = st.text_input("Enter recipe name or ingredient")

        if query:
            found = False
            for r in recipes:
                if query.lower() in r["name"].lower() or query.lower() in r["ingredients"].lower():
                    st.markdown(f"### 🍲 {r['name']}")
                    if r["image"]:
                        st.image(r["image"], width=300)
                    if r["video"]:
                        st.video(r["video"])
                    st.write(r["ingredients"])
                    st.write(r["steps"])
                    st.divider()
                    found = True

            if not found:
                st.error("No recipe found")

# ---------------- APP FLOW ----------------
if not st.session_state.logged_in:
    login_page()
else:
    main_app()


