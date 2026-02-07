from db import load_recipes
import re
from difflib import SequenceMatcher

STOP_WORDS = {
    "i", "have", "a", "an", "the", "with", "and", "or",
    "to", "can", "cook", "make", "using", "want", "need",
    "please", "suggest", "recipe", "recipes", "for", "something",
    "what", "is", "are", "of"
}

SPELLING_FIX = {
    "tamato": "tomato",
    "tomoto": "tomato",
    "tommato": "tomato",
    "briyani": "biryani"
}

def normalize(text):
    return re.sub(r"[^a-z]", "", text.lower())

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# ---------------- INTENT ----------------
def detect_intent(query: str) -> str:
    q = query.lower()

    if any(w in q for w in ["how to", "how do", "steps", "method"]):
        return "how_to"

    if any(w in q for w in ["ingredient", "ingredients", "contains", "what is in"]):
        return "ingredients"

    return "name_only"

# ---------------- AI CORE ----------------
def ai_suggest(user_query: str) -> str:
    recipes = load_recipes()
    if not recipes:
        return "No recipes available."

    intent = detect_intent(user_query)
    query_norm = normalize(user_query)

    # ✅ NAME ONLY MODE (IMPORTANT FIX)
    if intent == "name_only":
        for r in recipes:
            name_norm = normalize(r["name"])
            if name_norm == query_norm or similarity(name_norm, query_norm) > 0.7:
                return f"### 🍽️ {r['name']}"

        return "No related recipes found."

    # ✅ INGREDIENTS MODE
    if intent == "ingredients":
        for r in recipes:
            if similarity(normalize(r["name"]), query_norm) > 0.6:
                return f"### 🧾 Ingredients for {r['name']}\n\n{r['ingredients']}"
        return "Sorry, I couldn't find the ingredients for that recipe."

    # ✅ HOW-TO MODE
    if intent == "how_to":
        for r in recipes:
            if similarity(normalize(r["name"]), query_norm) > 0.6:
                return f"### 🍳 How to cook {r['name']}\n\n{r['steps']}"
        return "Sorry, I couldn't find the cooking steps for that recipe."
