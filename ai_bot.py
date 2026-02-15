
from db import load_recipes

def ai_suggest(user_query: str) -> str:
    try:
        import requests
        import streamlit as st
    except Exception:
        return "Required libraries missing."

    # 🔐 Check Hugging Face API key
    if "HF_API_KEY" not in st.secrets:
        return "Hugging Face API key not configured."

    HF_API_KEY = st.secrets["HF_API_KEY"]

    # ✅ Light & stable free model
    MODEL = "google/flan-t5-large"

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

    # 🧠 CHATGPT-LIKE PROMPT (FRIENDLY + STEP-BY-STEP)
    prompt = f"""
You are a friendly, helpful assistant like ChatGPT.

Answer in a clear and human way:
- Explain step by step
- Use simple language
- Be polite and supportive
- Format neatly using bullet points or numbering
- Use light emojis if helpful 🙂

IMPORTANT RULES:
- Use ONLY the recipes given below
- Do NOT invent new recipes
- Do NOT add ingredients not listed

User question:
{user_query}

Available recipes:
{recipe_text}

Give the answer as if you are teaching a beginner.
"""

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

        return "AI is busy. Try again later."

    except Exception:
        return "AI is busy. Try again later."
