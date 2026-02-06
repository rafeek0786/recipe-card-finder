from db import load_recipes
import re

def extract_ingredients(text: str):
    """
    Extract words like ingredients from user query
    """
    text = text.lower()
    text = re.sub(r"[^a-zA-Z, ]", "", text)
    ingredients = [i.strip() for i in text.split(",") if i.strip()]
    return ingredients


def ai_suggest(user_query: str) -> str:
    recipes = load_recipes()

    if not recipes:
        return "❌ No recipes found in the database yet."

    user_ingredients = extract_ingredients(user_query)

    if not user_ingredients:
        return "❗ Please mention ingredients (example: bread, milk, egg)"

    results = []

    for r in recipes:
        recipe_ingredients = [
            i.strip().lower()
            for i in r["ingredients"].split(",")
            if i.strip()
        ]

        matched = set(user_ingredients) & set(recipe_ingredients)
        missing = set(recipe_ingredients) - set(user_ingredients)

        match_score = len(matched) / max(len(recipe_ingredients), 1)

        if matched:
            results.append({
                "recipe": r,
                "matched": matched,
                "missing": missing,
                "score": match_score
            })

    if not results:
        return "😕 No recipes match your ingredients. Try adding more items."

    results.sort(key=lambda x: x["score"], reverse=True)

    response = "🤖 **AI Recipe Suggestions Based on Your Ingredients**\n\n"

    for item in results[:3]:
        r = item["recipe"]
        response += f"""
### 🍽️ {r['name']}
✅ **Matching ingredients:** {", ".join(item["matched"])}
⚠️ **Missing ingredients:** {", ".join(item["missing"]) if item["missing"] else "None"}
📌 **Tip:** You can prepare this recipe with slight adjustments.
---
"""

    return response
