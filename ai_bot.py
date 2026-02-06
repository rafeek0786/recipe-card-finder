from db import load_recipes
import re

# Words that are NOT ingredients
STOP_WORDS = {
    "i", "have", "a", "an", "the", "with", "and", "or",
    "to", "can", "cook", "make", "using", "want", "need",
    "please", "suggest", "recipe", "recipes", "for"
}

def extract_ingredients_from_sentence(sentence: str):
    sentence = sentence.lower()
    sentence = re.sub(r"[^a-z ]", "", sentence)

    words = sentence.split()
    ingredients = [w for w in words if w not in STOP_WORDS]

    return list(set(ingredients))


def ai_suggest(user_query: str) -> str:
    recipes = load_recipes()

    if not recipes:
        return "❌ No recipes available in the database."

    user_ingredients = extract_ingredients_from_sentence(user_query)

    if not user_ingredients:
        return "❗ I couldn't understand the ingredients. Try: *I have bread and milk*"

    suggestions = []

    for r in recipes:
        recipe_ingredients = [
            i.strip().lower()
            for i in r["ingredients"].split(",")
            if i.strip()
        ]

        matched = set(user_ingredients) & set(recipe_ingredients)
        missing = set(recipe_ingredients) - set(user_ingredients)

        if matched:
            score = len(matched)
            suggestions.append((score, r, matched, missing))

    if not suggestions:
        return "😕 No matching recipes found. Try adding more ingredients."

    suggestions.sort(reverse=True, key=lambda x: x[0])

    response = "🤖 **Based on what you said, here are the best recipes:**\n\n"

    for score, r, matched, missing in suggestions[:3]:
        response += f"""
### 🍽️ {r['name']}
✅ **You have:** {", ".join(matched)}
⚠️ **Missing:** {", ".join(missing) if missing else "Nothing"}
💡 *You can cook this with minor adjustments.*
---
"""

    return response
