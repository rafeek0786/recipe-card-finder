from db import load_recipes
import re

STOP_WORDS = {
    "i", "have", "a", "an", "the", "with", "and", "or",
    "to", "can", "cook", "make", "using", "want", "need",
    "please", "suggest", "recipe", "recipes", "for", "something"
}

def normalize(text):
    return re.sub(r"[^a-z]", "", text.lower())


def extract_user_ingredients(sentence: str):
    sentence = sentence.lower()
    sentence = re.sub(r"[^a-z ]", "", sentence)
    words = sentence.split()
    return [normalize(w) for w in words if w not in STOP_WORDS]


def extract_recipe_ingredients(ingredients_text: str):
    # Handles ingredients stored line-by-line
    lines = ingredients_text.splitlines()
    return [normalize(line) for line in lines if line.strip()]


def ai_suggest(user_query: str) -> str:
    recipes = load_recipes()

    if not recipes:
        return "❌ No recipes available in your database."

    user_ing = extract_user_ingredients(user_query)

    if not user_ing:
        return "❗ Please tell me what ingredients you have."

    results = []

    for r in recipes:
        recipe_ing = extract_recipe_ingredients(r["ingredients"])

        matched = set()
        for ui in user_ing:
            for ri in recipe_ing:
                if ui in ri or ri in ui:
                    matched.add(ri)

        if matched:
            results.append((len(matched), r, matched))

    if not results:
        return "😕 I couldn’t find any recipes related to those ingredients."

    results.sort(reverse=True, key=lambda x: x[0])

    response = "🤖 **Here are recipes you can try:**\n\n"

    for score, r, matched in results[:5]:
        response += f"""
### 🍽️ {r['name']}
✅ **Related ingredients:** {", ".join(matched)}
---
"""

    return response
