from db import load_recipes
from groq import Groq
import streamlit as st

# 🔐 Read key from Streamlit Secrets (mobile-safe)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ai_suggest(user_query: str) -> str:
    recipes = load_recipes()

    if not recipes:
        return "No recipes available."

    recipe_text = ""
    for r in recipes:
        recipe_text += (
            f"Recipe Name: {r['name']}\n"
            f"Ingredients: {r['ingredients']}\n"
            f"Steps: {r['steps']}\n"
            f"---\n"
        )

    prompt = (
        "You are a helpful recipe assistant.\n\n"
        "Answer using ONLY the recipes below.\n\n"
        f"User Question:\n{user_query}\n\n"
        f"Recipes:\n{recipe_text}"
    )

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=500
        )
        return response.choices[0].message.content

    except Exception:
        return "AI is busy. Try again later."
