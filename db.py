import sqlite3

DB_FILE = "recipes.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            name TEXT PRIMARY KEY,
            ingredients TEXT,
            steps TEXT,
            image TEXT,
            video TEXT,
            owner TEXT
        )
    """)
    conn.commit()
    conn.close()

def load_recipes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, ingredients, steps, image, video, owner FROM recipes")
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

def save_recipes(recipes):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM recipes")

    for r in recipes:
        cur.execute("""
            INSERT INTO recipes (name, ingredients, steps, image, video, owner)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            r["name"],
            r["ingredients"],
            r["steps"],
            r["image"],
            r["video"],
            r["owner"]
        ))

    conn.commit()
    conn.close()
