from db import load_recipes

def ai_suggest(user_query: str) -> str:
    try:
        import streamlit as st
        from groq import Groq
    except Exception:
        return "Groq library not installed."

    # 🔐 Read API key safely
    if "GROQ_API_KEY" not in st.secrets:
        return "Groq API key not configured."

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

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
            max_tokens=400
        )
        return response.choices[0].message.content

    except Exception:
        return "Groq AI is busy. Try again later."
