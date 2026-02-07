import sqlite3

DB_FILE = "recipes.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            ingredients TEXT,
            steps TEXT,
            image TEXT,
            video TEXT,
            owner TEXT
        )
    """)
    conn.commit()
    conn.close()

# LOAD all recipes
def load_recipes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT name, ingredients, steps, image, video, owner
        FROM recipes
    """)
    rows = cur.fetchall()
    conn.close()

    recipes = []
    for r in rows:
        recipes.append({
            "name": r[0],
            "ingredients": r[1],
            "steps": r[2],
            "image": r[3],
            "video": r[4],
            "owner": r[5]
        })
    return recipes

# SAVE ALL recipes (matches app.py exactly)
def save_recipes(recipes):
    conn = get_connection()
    cur = conn.cursor()

    for recipe in recipes:
        cur.execute("""
            INSERT OR REPLACE INTO recipes
            (name, ingredients, steps, image, video, owner)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            recipe["name"],
            recipe["ingredients"],
            recipe["steps"],
            recipe.get("image", ""),
            recipe.get("video", ""),
            recipe.get("owner", "")
        ))

    conn.commit()
    conn.close()

# DELETE single recipe (safe)
def delete_recipe(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM recipes WHERE name = ?", (name,))
    conn.commit()
    conn.close()
