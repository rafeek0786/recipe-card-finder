from db import load_recipes
import re
from difflib import SequenceMatcher

STOP_WORDS = {
    "i", "have", "a", "an", "the", "with", "and", "or",
    "to", "can", "cook", "make", "using", "want", "need",
    "please", "suggest", "recipe", "recipes", "for",
    "what", "is", "are", "of"
}

SPELLING_FIX = {
    "tamato": "tomato",
    "tomoto": "tomato",
    "tommato": "tomato",
    "briyani": "biryani"
}

# ---------- helpers ----------
def normalize(text):
    return re.sub(r"[^a-z]", "", str(text).lower())

def fix_spelling(word):
    return SPELLING_FIX.get(word, word)

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# ---------- intent detection ----------
def detect_intent(query: str) -> str:
    q = query.lower()
    if "how to" in q or "steps" in q or "method" in q:
        return "how_to"
    if "ingredient" in q or "ingredients" in q:
        return "ingredients"
    return "suggest"

# ---------- AI suggestion text ----------
def chat_text(recipe_name: str) -> str:
    return (
        "This recipe tastes very good and has a pleasant aroma. "
        "It is easy to cook and many people enjoy this food."
    )

# ---------- MAIN AI FUNCTION ----------
def ai_suggest(user_query: str) -> str:
    recipes = load_recipes()
    if not recipes:
        return "No recipes available."

    intent = detect_intent(user_query)
    query_norm = normalize(user_query)

    # ----- HOW TO MODE -----
    if intent == "how_to":
        for r in recipes:
            if normalize(r["name"]) in query_norm:
                return (
                    f"● {r['name']}\n"
                    f"{chat_text(r['name'])}\n\n"
                    f"### 🍳 How to cook {r['name']}\n\n"
                    f"{r['steps']}"
                )
        return "No matching recipe found."

    # ----- INGREDIENT MODE -----
    if intent == "ingredients":
        for r in recipes:
            if normalize(r["name"]) in query_norm:
                return (
                    f"● {r['name']}\n"
                    f"{chat_text(r['name'])}\n\n"
                    f"### 🧾 Ingredients for {r['name']}\n\n"
                    f"{r['ingredients']}"
                )
        return "No matching recipe found."

    # ----- SUGGEST MODE -----
    matches = []
    for r in recipes:
        name_norm = normalize(r["name"])
        if name_norm in query_norm or similarity(name_norm, query_norm) > 0.7:
            matches.append(r)

    if not matches:
        return "No matching recipe found."

    response = "✨ Recipes Matching Your Search\n\n"

    for r in matches:
        response += (
            f"● {r['name']}\n"
            f"  {chat_text(r['name'])}\n\n"
        )

    return response.strip()
