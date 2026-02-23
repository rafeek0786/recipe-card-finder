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
    "tommato": "tomato",
    "briyani": "biryani"
}

def normalize(text):
    return re.sub(r"[^a-z]", "", str(text).lower())

def fix_spelling(word):
    return SPELLING_FIX.get(word, word)

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# ---------------- INTENT DETECTION ----------------
def detect_intent(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["how to", "steps", "method"]):
        return "how_to"
    if any(w in q for w in ["ingredient", "ingredients"]):
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
    parts = re.split(r"[,\n ]+", text.lower())
    return [normalize(p) for p in parts if p.strip()]

# ---------------- CHAT STYLE TEXT ----------------
def chat_text(recipe_name: str) -> str:
    return (
        "This recipe tastes very good and has a pleasant aroma.\n"
        "It is easy to cook and many people enjoy this food.\n"
        "This dish is suitable for regular home meals."
    )

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
            if normalize(r["name"]) in query_norm:
                return (
                    f"{chat_text(r['name'])}\n\n"
                    f"### 🧾 Ingredients for {r['name']}\n\n{r['ingredients']}"
                )
        return "No matching recipe found for your search."

    # HOW-TO MODE
    if intent == "how_to":
        for r in recipes:
            if normalize(r["name"]) in query_norm:
                return (
                    f"{chat_text(r['name'])}\n\n"
                    f"### 🍳 How to cook {r['name']}\n\n{r['steps']}"
                )
        return "No matching recipe found for your search."

    # SUGGEST MODE (SEARCH RESULT ONLY)
    matches = []

    for r in recipes:
        name_norm = normalize(r["name"])
        if name_norm in query_norm or similarity(name_norm, query_norm) > 0.7:
            matches.append(r)

    if not matches:
        return "No matching recipe found for your search."

    response = "✨ Recipes Matching Your Search\n\n"
    for r in matches:
        response += f"● {r['name']}\n{chat_text(r['name'])}\n\n"

    return response.strip()
