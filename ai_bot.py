from db import load_recipes

def ai_suggest(user_query: str) -> str:
    recipes = load_recipes()

    if not recipes:
        return "No recipes found in the database yet."

    query = user_query.lower()
    matches = []

    for r in recipes:
        text = (
            r["name"] + " " +
            r["ingredients"] + " " +
            r["steps"]
        ).lower()

        score = sum(1 for word in query.split() if word in text)

        if score > 0:
            matches.append((score, r))

    if not matches:
        return "I couldn't find a matching recipe. Try using ingredient names."

    matches.sort(reverse=True, key=lambda x: x[0])

    response = "🍽️ **AI Recipe Suggestions:**\n\n"
    for score, r in matches[:3]:
        response += f"""
### {r['name']}
• Key ingredients: {r['ingredients'][:120]}...
• Suggestion: You can enhance this recipe by adjusting spices or adding herbs.
\n"""

    return response
