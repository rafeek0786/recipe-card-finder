from db import load_recipes
import re
from difflib import SequenceMatcher

# ---------------- CONSTANTS ----------------
STOP_WORDS = {
    "i", "have", "a", "an", "the", "with", "and", "or",
    "to", "can", "cook", "make", "using", "want", "need",
    "please", "suggest", "recipe", "recipes", "for", "something"
}

SYNONYMS = {
    "rice": ["basmati", "rawrice"],
    "tomato": ["tomatoes"],
    "chilli": ["chili"],
    "potato": ["potatoes"],
    "egg": ["eggs"]
}

# ---------------- UTILITIES ----------------
def normalize(text):
    return re.sub(r"[^a-z]", "", text.lower())

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def expand_synonyms(word):
    for k, v in SYNONYMS.items():
        if word == k or word in v:
            return [k] + v
    return [word]

# ---------------- INTENT DETECTION ----------------
def detect_intent(query: str) -> str:
    q = query.lower()

    if any(w in q for w in ["how to", "how do", "steps", "method"]):
        return "how_to"

    if any(w in q for w in ["idea", "ideas", "suggest", "what can i"]):
        return "ideas"

    return "suggest"

# ---------------- INGREDIENT EXTRACTION ----------------
def extract_user_ingredients(sentence: str):
    sentence = re.sub(r"[^a-z ]", "", sentence.lower())
    words = sentence.split()

    ingredients = []
    for w in words:
        if w not in STOP_WORDS:
            ingredients.extend(expand_synonyms(normalize(w)))

    return list(set(ingredients))

def extract_recipe_ingredients(text: str):
    return [normalize(line) for line in text.splitlines() if line.strip()]

# ---------------- AI CORE ----------------
def ai_suggest(user_query: str) -> str:
    recipes = load_recipes()

    if not recipes:
        return "No recipes available."

    intent = detect_intent(user_query)
    user_ing = extract_user_ingredients(user_query)

    matches = []

    for r in recipes:
        recipe_ing = extract_recipe_ingredients(r["ingredients"])
        score = 0

        for ui in user_ing:
            for ri in recipe_ing:
                if ui in ri or ri in ui or similarity(ui, ri) > 0.7:
                    score += 1

        # Intent-based weighting
        if intent == "how_to" and score > 0:
            score += 1  # prioritize exact recipes
        if intent == "ideas":
            score += 0.5  # broader suggestions

        if score > 0:
            matches.append((score, r["name"]))

    if not matches:
        return "No related recipes found."

    matches.sort(reverse=True, key=lambda x: x[0])

    # 🔒 OLD OUTPUT STYLE (UNCHANGED)
    response = "✨ Suggested Recipes\n\n"
    for _, name in matches[:5]:
        response += f"• {name}\n\n"

    return response.strip()
