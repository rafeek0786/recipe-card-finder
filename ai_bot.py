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

def detect_intent(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["how to", "steps", "method"]):
        return "how_to"
    if "ingredient" in q:
        return "ingredients"
    return "suggest"

def extract_user_ingredients(sentence: str):
    sentence = re.sub(r"[^a-z ]", "", sentence.lower())
    words = sentence.split()
    return [fix_spelling(normalize(w)) for w in words if w not in STOP_WORDS]

def extract_recipe_ingredients(text: str):
    return [line.strip() for line in text.splitlines() if line.strip()]

def ai_suggest(user_query: str) -> str:
    recipes = load_recipes()
    if not recipes:
        return "No recipes available."

    intent = detect_intent(user_query)
    query_norm = normalize(user_query)

    if intent == "ingredients":
        for r in recipes:
            if similarity(normalize(r["name"]), query_norm) > 0.7:
                return f"### Ingredients\n{r['ingredients']}"

    if intent == "how_to":
        for r in recipes:
            if similarity(normalize(r["name"]), query_norm) > 0.7:
                return f"### Steps\n{r['steps']}"

    user_ing = extract_user_ingredients(user_query)
    matches = []

    for r in recipes:
        score = 0
        for ui in user_ing:
            if ui in r["ingredients"].lower():
                score += 1
        if score > 0:
            matches.append((score, r["name"]))

    if not matches:
        return "No related recipes found."

    matches.sort(reverse=True)
    return "✨ Suggested Recipes\n" + "\n".join([f"- {m[1]}" for m in matches[:5]])
