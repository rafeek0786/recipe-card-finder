from db import load_recipes

def ai_suggest(user_query: str) -> str:
    try:
        import requests
        import streamlit as st
    except Exception:
        return "Required libraries missing."

    # 🔐 Check API key
    if "HF_API_KEY" not in st.secrets:
        return "Hugging Face API key not configured."

    HF_API_KEY = st.secrets["HF_API_KEY"]
    MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

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
        "Answer ONLY using the recipes below.\n\n"
        f"User Question:\n{user_query}\n\n"
        f"Recipes:\n{recipe_text}"
    )

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{MODEL}",
            headers=headers,
            json={"inputs": prompt},
            timeout=30
        )

        result = response.json()

        if isinstance(result, list):
            return result[0].get("generated_text", "No response from AI.")

        return "AI is busy. Try again."

    except Exception:
        return "Hugging Face AI is busy. Try again later."
