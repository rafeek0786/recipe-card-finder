from db import load_recipes
import re
from difflib import SequenceMatcher

# ---------------- STOP WORDS ----------------
STOP_WORDS = {
    "i", "have", "a", "an", "the", "with", "and", "or",
    "to", "can", "cook", "make", "using", "want", "need",
    "please", "suggest", "recipe", "recipes", "for", "something"
}

# ---------------- SYNONYMS ----------------
SYNONYMS = {
    "rice": ["basmati", "rawrice"],
    "tomato": ["tomatoes"],
    "chilli": ["chili"],
    "potato": ["potatoes"],
    "egg": ["eggs"]
}

# ---------------- HELPERS ----------------
def normalize(text):
    return re.sub(r"[^a-z]", "", text.lower())

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def expand_synonyms(word):
    for k, v in SYNONYMS.items():
        if word == k or word in v:
            return [k] + v
    return [word]

# ---------------- EXTRACTION ----------------
def extract_user_ingredients(sentence: str):
    sentence = sentence.lower()
    sentence = re.sub(r"[^a-z ]", "", sentence)
    words = sentence.split()

    result = []
    for w in words:
        if w not in STOP_WORDS:
            result.extend(expand_synonyms(normalize(w)))

    return list(set(result))

def extract_recipe_ingredients(ingredients_text: str):
    lines = ingredients_text.splitlines()
    result = []
    for line in lines:
        if line.strip():
            result.append(normalize(line))
    return result

# ---------------- AI CORE ----------------
def ai_suggest(user_query: str) -> str:
    recipes = load_recipes()

    if not recipes:
        return "❌ No recipes available."

    user_ing = extract_user_ingredients(user_query)

    if not user_ing:
        return "❗ Please mention some ingredients."

    matches = []

    for r in recipes:
        recipe_ing = extract_recipe_ingredients(r["ingredients"])
        score = 0
        matched_items = []

        for ui in user_ing:
            for ri in recipe_ing:
                if ui in ri or ri in ui or similarity(ui, ri) > 0.7:
                    score += 1
                    matched_items.append(ui)

        if score > 0:
            matches.append({
                "score": score,
                "name": r["name"],
                "matched": list(set(matched_items))
            })

    if not matches:
        return "😔 No related recipes found."

    matches.sort(key=lambda x: x["score"], reverse=True)

    # ---------------- RESPONSE ----------------
    response = "✨ **AI Suggested Recipes**\n\n"

    for m in matches[:5]:
        response += f"• **{m['name']}**\n"
        response += f"  _Matched ingredients:_ {', '.join(m['matched'])}\n\n"

    return response.strip()
