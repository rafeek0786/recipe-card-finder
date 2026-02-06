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
    lines = ingredients_text.splitlines()
    return [normalize(line) for line in lines if line.strip()]

def ai_suggest(user_query: str) -> str:
    recipes = load_recipes()
    if not recipes:
        return "No recipes available."

    user_ing = extract_user_ingredients(user_query)
    if not user_ing:
        return "Please tell me what ingredients you have."

    matches = []

    for r in recipes:
        recipe_ing = extract_recipe_ingredients(r["ingredients"])
        score = 0
        for ui in user_ing:
            for ri in recipe_ing:
                if ui in ri or ri in ui:
                    score += 1
        if score > 0:
            matches.append((score, r["name"]))

    if not matches:
        return "No related recipes found."

    matches.sort(reverse=True, key=lambda x: x[0])

    response = "✨ Suggested Recipes\n\n"
    for _, name in matches[:5]:
        response += f"• {name}\n  🔗 [View](?view_recipe={name.replace(' ', '%20')})\n\n"

    return response.strip()
