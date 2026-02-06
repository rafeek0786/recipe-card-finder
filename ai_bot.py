from db import load_recipes
import re
from difflib import SequenceMatcher

STOP_WORDS = {
    "i", "have", "a", "an", "the", "with", "and", "or",
    "to", "can", "cook", "make", "using", "want", "need",
    "please", "suggest", "recipe", "recipes", "for"
}

SYNONYMS = {
    "rice": ["basmati", "rawrice"],
    "tomato": ["tomatoes"],
    "chilli": ["chili"],
    "potato": ["potatoes"],
    "egg": ["eggs"]
}

def normalize(text):
    return re.sub(r"[^a-z]", "", text.lower())

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def expand_synonyms(word):
    for key, values in SYNONYMS.items():
        if word == key or word in values:
            return [key] + values
    return [word]

def extract_user_ingredients(sentence):
    sentence = re.sub(r"[^a-z ]", "", sentence.lower())
    words = sentence.split()

    ingredients = []
    for word in words:
        if word not in STOP_WORDS:
            ingredients.extend(expand_synonyms(normalize(word)))

    return list(set(ingredients))

def extract_recipe_ingredients(text):
    return [normalize(line) for line in text.splitlines() if line.strip()]

def ai_suggest(user_query):
    recipes = load_recipes()

    if not recipes:
        return "No recipes available."

    user_ingredients = extract_user_ingredients(user_query)

    if not user_ingredients:
        return "Please specify available ingredients."

    results = []

    for recipe in recipes:
        recipe_ingredients = extract_recipe_ingredients(recipe["ingredients"])
        score = 0
        matched = []

        for ui in user_ingredients:
            for ri in recipe_ingredients:
                if ui in ri or similarity(ui, ri) > 0.7:
                    score += 1
                    matched.append(ui)

        if score > 0:
            results.append({
                "name": recipe["name"],
                "score": score,
                "matched": list(set(matched))
            })

    if not results:
        return "No matching recipes found."

    results.sort(key=lambda x: x["score"], reverse=True)

    response = "✨ **AI Suggested Recipes**\n\n"
    for r in results[:5]:
        response += f"• **{r['name']}**\n"
        response += f"  _Matched ingredients:_ {', '.join(r['matched'])}\n\n"

    return response.strip()
