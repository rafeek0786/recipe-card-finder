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

# ---------------- PERMANENT SAVE ----------------
def save_recipe(recipe):
    conn = get_connection()
    cur = conn.cursor()
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

# ---------------- SYNC DATABASE (FIX DELETE) ----------------
def save_recipes(recipes):
    conn = get_connection()
    cur = conn.cursor()

    # 1️⃣ Get existing recipe names in DB
    cur.execute("SELECT name FROM recipes")
    db_names = {row[0] for row in cur.fetchall()}

    # 2️⃣ Names coming from app
    app_names = {r["name"] for r in recipes}

    # 3️⃣ Delete removed recipes
    to_delete = db_names - app_names
    for name in to_delete:
        cur.execute("DELETE FROM recipes WHERE name = ?", (name,))

    # 4️⃣ Insert / Update current recipes
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

def delete_recipe(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM recipes WHERE name = ?", (name,))
    conn.commit()
    conn.close()
