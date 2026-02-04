import streamlit as st
import json
import os

st.set_page_config(page_title="Recipe Card Finder", layout="centered")

DATA_FILE = "recipes.json"
IMAGE_FOLDER = "images"

os.makedirs(IMAGE_FOLDER, exist_ok=True)

def load_recipes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_recipes(recipes):
    with open(DATA_FILE, "w") as f:
        json.dump(recipes, f, indent=4)

recipes = load_recipes()

st.title("🍽️ Recipe Card Finder")
st.caption("Version 1.0")

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
    image = st.file_uploader("Upload Recipe Image", type=["jpg", "png", "jpeg"])

    if st.button("Save Recipe"):
        if name and ingredients and steps:
            image_path = ""
            if image:
                image_path = f"{IMAGE_FOLDER}/{image.name}"
                with open(image_path, "wb") as f:
                    f.write(image.getbuffer())

            recipes.append({
                "name": name,
                "ingredients": ingredients,
                "steps": steps,
                "image": image_path
            })
            save_recipes(recipes)
            st.success("Recipe saved successfully!")
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
            st.write("**Ingredients:**")
            st.write(r["ingredients"])
            st.write("**Steps:**")
            st.write(r["steps"])
            st.divider()

# ---------------- SEARCH ----------------
elif menu == "Search Recipe":
    st.subheader("Search Recipe")

    keyword = st.text_input("Enter recipe name or ingredient")

    if keyword:
        found = False
        for r in recipes:
            if keyword.lower() in r["name"].lower() or keyword.lower() in r["ingredients"].lower():
                st.markdown(f"### 🍽️ {r['name']}")
                if r["image"]:
                    st.image(r["image"], width=300)
                st.write(r["ingredients"])
                st.write(r["steps"])
                st.divider()
                found = True
        if not found:
            st.error("No recipe found")
