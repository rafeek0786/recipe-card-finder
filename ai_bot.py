def ai_suggest(user_query: str):
    recipes = load_recipes()

    if not recipes:
        return []

    user_ing = extract_user_ingredients(user_query)

    if not user_ing:
        return []

    matches = []

    for r in recipes:
        recipe_ing = extract_recipe_ingredients(r["ingredients"])

        score = 0
        for ui in user_ing:
            for ri in recipe_ing:
                if ui in ri or ri in ui:
                    score += 1

        if score > 0:
            matches.append((score, r["name"]))

    matches.sort(reverse=True, key=lambda x: x[0])

    return [name for _, name in matches[:5]]
