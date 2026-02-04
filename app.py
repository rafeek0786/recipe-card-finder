import streamlit as st
import json
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Recipe Card Finder", layout="centered")

DATA_FILE = "recipes.json"
IMAGE_FOLDER = "images"
VIDEO_FOLDER = "videos"

os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

# ---------------- DATA FUNCTIONS ----------------
def load_recipes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_recipes(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

recipes = load_recipes()

# ---------------- UI ----------------
st.title("🍽️ Recipe Card Finder")
st.caption("Image & Video Supported")

menu = st.sidebar.selectbox(
    "Menu",
    ["Add Recipe", "View Recipes", "Search Recipe"]
)

# ---------------- ADD RECIPE ----------------
if menu == "Add Recipe":
    st.subheader("Add New Recipe")

    name = st.text_input("Recipe Name")
    ingredients = st.text_area("Ingredients")
    steps = st.text_area("Cooking Steps")

    image = st.file_uploader(
        "Upload Recipe Image",
        type=["jpg", "png", "jpeg"]
    )

    video = st.file_uploader(
        "Upload Cooking Video (MP4)",
        type=["mp4"]
    )

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
            st.success("Recipe saved successfully!")

# ---------------- VIEW RECIPES ----------------
elif menu == "View Recipes":
    st.subheader("All Recipes")

    if not recipes:
        st.info("No recipes found")
    else:
        for r in recipes:
            st.markdown(f"### 🍲 {r['name']}")

            if r["image"]:
                st.image(r["image"], width=300)

            if r["video"]:
                st.video(r["video"])

            st.write("**Ingredients:**")
            st.write(r["ingredients"])

            st.write("**Cooking Steps:**")
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
            st.error("No matching recipe found")

