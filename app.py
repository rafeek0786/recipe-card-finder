import streamlit as st
from db import add_recipe, load_recipes, delete_recipe, search_recipes

# 🔊 VOICE IMPORTS (ADDED)
from gtts import gTTS
import tempfile

st.set_page_config(page_title="Recipe App", layout="centered")

# 🔊 TEXT TO SPEECH FUNCTION (ADDED)
def speak_text(text):
    tts = gTTS(text=text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name


# ---------------- SIDEBAR MENU ----------------
menu = st.sidebar.selectbox(
    "Menu",
    ["Add Recipe", "View Recipes", "Search"]
)

# ---------------- ADD RECIPE ----------------
if menu == "Add Recipe":
    st.title("➕ Add Recipe")

    name = st.text_input("Recipe Name")
    ingredients = st.text_area("Ingredients")
    steps = st.text_area("Steps")

    if st.button("Save Recipe"):
        if name and ingredients and steps:
            add_recipe(name, ingredients, steps)
            st.success("Recipe added successfully!")
        else:
            st.warning("Please fill all fields.")

# ---------------- VIEW RECIPES ----------------
elif menu == "View Recipes":
    st.title("📖 View Recipes")

    recipes = load_recipes()

    if not recipes:
        st.info("No recipes available.")
    else:
        for r in recipes:
            st.subheader(r["name"])
            st.write("**Ingredients:**")
            st.write(r["ingredients"])
            st.write("**Steps:**")
            st.write(r["steps"])

            # 🔊 VOICE BUTTON (ADDED)
            if st.button(f"🔊 Listen to {r['name']} steps"):
                audio = speak_text(r["steps"])
                st.audio(audio, format="audio/mp3")

            if st.button(f"❌ Delete {r['name']}"):
                delete_recipe(r["name"])
                st.success("Recipe deleted. Refresh to see changes.")
                st.stop()

            st.markdown("---")

# ---------------- SEARCH ----------------
elif menu == "Search":
    st.title("🔍 Search Recipes")

    query = st.text_input("Enter recipe name")

    if query:
        results = search_recipes(query)

        if not results:
            st.warning("No matching recipes found.")
        else:
            for r in results:
                st.subheader(r["name"])
                st.write("**Ingredients:**")
                st.write(r["ingredients"])
                st.write("**Steps:**")
                st.write(r["steps"])

                # 🔊 VOICE BUTTON (ADDED)
                if st.button(f"🔊 Listen to {r['name']} steps"):
                    audio = speak_text(r["steps"])
                    st.audio(audio, format="audio/mp3")

                st.markdown("---")
