from db import load_recipes
import re
from difflib import SequenceMatcher

STOP_WORDS = {
    "i", "have", "a", "an", "the", "with", "and", "or",
    "to", "can", "cook", "make", "using", "want", "need",
    "please", "suggest", "recipe", "recipes", "for", "something",
    "what", "is", "are", "of"
}

SYNONYMS = {
    "rice": ["basmati", "rawrice"],
    "tomato": ["tomatoes"],
    "chilli": ["chili"],
    "potato": ["potatoes"],
    "egg": ["eggs"],
    "bread": ["toast"]
}

SPELLING_FIX = {
    "tamato": "tomato",
    "tomoto": "tomato",
    "tommato": "tomato"
}

def normalize(text):
    return re.sub(r"[^a-z]", "", text.lower())

def fix_spelling(word):
    return SPELLING_FIX.get(word, word)

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# ---------------- INTENT DETECTION ----------------
def detect_intent(query: str) -> str:
    q = query.lower()

    if any(w in q for w in ["how to", "how do", "steps", "method"]):
        return "how_to"

    if any(w in q for w in ["ingredient", "ingredients", "contains", "what is in"]):
        return "ingredients"

    return "suggest"

# ---------------- EXTRACTION ----------------
def extract_user_ingredients(sentence: str):
    sentence = re.sub(r"[^a-z ]", "", sentence.lower())
    words = sentence.split()
    return [
        fix_spelling(normalize(w))
        for w in words
        if w not in STOP_WORDS
    ]

def extract_recipe_ingredients(text: str):
    return [line.strip() for line in text.splitlines() if line.strip()]

# ---------------- AI CORE ----------------
def ai_suggest(user_query: str) -> str:
    recipes = load_recipes()
    if not recipes:
        return "No recipes available."

    intent = detect_intent(user_query)
    query_norm = normalize(user_query)

    # INGREDIENTS MODE
    if intent == "ingredients":
        for r in recipes:
            name_norm = normalize(r["name"])
            if name_norm in query_norm or similarity(name_norm, query_norm) > 0.7:
                return f"### 🧾 Ingredients for {r['name']}\n\n{r['ingredients']}"
        return "Sorry, I couldn't find the ingredients for that recipe."

    # HOW-TO MODE
    if intent == "how_to":
        for r in recipes:
            name_norm = normalize(r["name"])
            if name_norm in query_norm or similarity(name_norm, query_norm) > 0.7:
                return f"### 🍳 How to cook {r['name']}\n\n{r['steps']}"
        return "Sorry, I couldn't find the cooking steps for that recipe."

    # SUGGEST MODE
    user_ing = extract_user_ingredients(user_query)
    matches = []

    for r in recipes:
        recipe_ing = extract_recipe_ingredients(r["ingredients"])
        score = 0

        for ui in user_ing:
            for ri in recipe_ing:
                if normalize(ui) in normalize(ri):
                    score += 1
                else:
                    for syn in SYNONYMS.get(ui, []):
                        if normalize(syn) in normalize(ri):
                            score += 1

        if score > 0:
            matches.append((score, r["name"]))

    if not matches:
        return "No related recipes found."

    matches.sort(reverse=True, key=lambda x: x[0])

    response = "✨ Suggested Recipes (Click to view)\n\n"
    for _, name in matches[:5]:
        response += f"[{name}]\n"

    return response.strip()
