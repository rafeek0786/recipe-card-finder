import streamlit as st
import json
import os

st.set_page_config(page_title="Recipe Card Finder", layout="centered")

DATA_FILE = "recipes.json"
IMAGE_FOLDER = "images"
VIDEO_FOLDER = "videos"

os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

def load_recipes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_recipes(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

recipes = load_recipes()

st.title("🍽️ Recipe Card Finder")
st.caption("Full CRUD Application (Create, Read, Update, Delete)")

menu = st.sidebar.selectbox(
    "Menu",
    ["Add Recipe", "View Recipes", "Search Recipe", "Edit Recipe", "Delete Recipe"]
)

# ---------------- ADD RECIPE ----------------
if menu == "Add Recipe":
    st.subheader("Add New Recipe")

    name = st.text_input("Recipe Name")
    ingredients = st.text_area("Ingredients")
    steps = st.text_area("Cooking Steps")

    image = st.file_uploader("Upload Recipe Image", type=["jpg", "png", "jpeg"])
    video = st.file_uploader("Upload Cooking Video (MP4)", type=["mp4"])

    if st.button("Save Recipe"):
        if name and ingredients and steps:
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
        else:
            st.warning("Please fill all fields")

# ---------------- VIEW RECIPES ----------------
elif menu == "View Recipes":
    st.subheader("All Recipes")

    if not recipes:
        st.info("No recipes available")
    else:
        for r in recipes:
            st.markdown(f"### 🍲 {r['name']}")
            if r["image"]:
                st.image(r["image"], width=300)
            if r["video"]:
                st.video(r["video"])
            st.write("**Ingredients:**")
            st.write(r["ingredients"])
            st.write("**Steps:**")
            st.write(r["steps"])
            st.divider()

# ---------------- SEARCH ----------------
elif menu == "Search Recipe":
    st.subheader("Search Recipe")

    query = st.text_input("Enter recipe name or ingredient")

    if query:
        found = False
        for r in recipes:
            if query.lower() in r["name"].lower() or query.lower() in r["ingredients"].lower():
                st.markdown(f"### 🍽️ {r['name']}")
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

# ---------------- EDIT RECIPE ----------------
elif menu == "Edit Recipe":
    st.subheader("Edit Recipe")

    if not recipes:
        st.info("No recipes to edit")
    else:
        names = [r["name"] for r in recipes]
        selected = st.selectbox("Select Recipe", names)

        recipe = next(r for r in recipes if r["name"] == selected)

        new_name = st.text_input("Recipe Name", recipe["name"])
        new_ingredients = st.text_area("Ingredients", recipe["ingredients"])
        new_steps = st.text_area("Cooking Steps", recipe["steps"])

        if st.button("Update Recipe"):
            recipe["name"] = new_name
            recipe["ingredients"] = new_ingredients
            recipe["steps"] = new_steps
            save_recipes(recipes)
            st.success("Recipe updated successfully!")

# ---------------- DELETE RECIPE ----------------
elif menu == "Delete Recipe":
    st.subheader("Delete Recipe")

    if not recipes:
        st.info("No recipes to delete")
    else:
        names = [r["name"] for r in recipes]
        selected = st.selectbox("Select Recipe to Delete", names)

        if st.button("Delete Recipe"):
            recipes = [r for r in recipes if r["name"] != selected]
            save_recipes(recipes)
            st.success("Recipe deleted successfully!")

