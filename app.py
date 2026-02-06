import streamlit as st
import streamlit.components.v1 as components
import json
import os
import hashlib

# ================== CONFIG ==================
DATA_FILE = "recipes.json"
USER_FILE = "users.json"

# ================== INIT FILES ==================
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({
            "admin": {
                "password": "admin",
                "role": "admin"
            }
        }, f)

# ================== HELPERS ==================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def load_users():
    with open(USER_FILE) as f:
        return json.load(f)

def save_users(u):
    with open(USER_FILE, "w") as f:
        json.dump(u, f, indent=2)

def load_recipes():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_recipes(r):
    with open(DATA_FILE, "w") as f:
        json.dump(r, f, indent=2)

# ================== AI LOGIC ==================
def ai_suggest(sentence):
    words = set(sentence.lower().replace(",", " ").split())
    recipes = load_recipes()

    matches = []
    for r in recipes:
        ingredients = set(i.strip().lower() for i in r["ingredients"].splitlines())
        if words & ingredients:
            matches.append(r["name"])

    return list(dict.fromkeys(matches))

# ================== SESSION ==================
if "login" not in st.session_state:
    st.session_state.login = False
if "user" not in st.session_state:
    st.session_state.user = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "selected_recipe" not in st.session_state:
    st.session_state.selected_recipe = None
if "ai_open" not in st.session_state:
    st.session_state.ai_open = False

# ================== LOGIN ==================
if not st.session_state.login:
    st.title("🔐 Login")

    users = load_users()
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in users:
            stored = users[u]
            valid = (
                stored["password"] == p if stored["role"] == "admin"
                else stored["password"] == hash_password(p)
            )
            if valid:
                st.session_state.login = True
                st.session_state.user = u
                st.session_state.role = stored["role"]
                st.rerun()
        st.error("Invalid login")

    st.stop()

# ================== MAIN APP ==================
st.title("🍽️ Recipe App")
st.sidebar.write(f"👤 {st.session_state.user}")
st.sidebar.write(f"🛡️ {st.session_state.role}")

if st.sidebar.button("Logout"):
    st.session_state.login = False
    st.rerun()

menu = st.sidebar.selectbox(
    "Menu",
    ["Add Recipe", "View Recipes", "Search", "AI Assistant"]
)

recipes = load_recipes()

# ================== ADD ==================
if menu == "Add Recipe":
    with st.form("add"):
        name = st.text_input("Recipe Name")
        ingredients = st.text_area("Ingredients (one per line)")
        steps = st.text_area("Steps")
        submit = st.form_submit_button("Save")

    if submit:
        recipes.append({
            "name": name,
            "ingredients": ingredients,
            "steps": steps
        })
        save_recipes(recipes)
        st.success("Recipe added")

# ================== VIEW ==================
elif menu == "View Recipes":
    if st.session_state.selected_recipe:
        recipes = [r for r in recipes if r["name"] == st.session_state.selected_recipe]
        st.session_state.selected_recipe = None

    for r in recipes:
        st.subheader(r["name"])
        st.text(r["ingredients"])
        st.write(r["steps"])
        st.divider()

# ================== SEARCH ==================
elif menu == "Search":
    q = st.text_input("Search")
    for r in recipes:
        if q.lower() in (r["name"] + r["ingredients"]).lower():
            st.subheader(r["name"])
            st.text(r["ingredients"])
            st.write(r["steps"])
            st.divider()

# ================== AI PAGE ==================
elif menu == "AI Assistant":
    q = st.text_input("Example: I have bread and milk")
    if q:
        results = ai_suggest(q)
        for r in results:
            if st.button(f"• {r}"):
                st.session_state.selected_recipe = r
                st.rerun()

# ================== FLOATING CHAT BUBBLE ==================
components.html(
    """
    <style>
    .bubble {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background: #0d6efd;
        border-radius: 50%;
        color: white;
        font-size: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 9999;
    }
    </style>

    <div class="bubble" onclick="window.parent.postMessage('open_ai','*')">
        💬
    </div>

    <script>
    window.addEventListener("message", (e) => {
        if (e.data === "open_ai") {
            window.parent.postMessage(
                {type: "streamlit:setComponentValue", value: true},
                "*"
            );
        }
    });
    </script>
    """,
    height=0
)

# ================== BUBBLE AI ==================
if st.session_state.ai_open:
    st.subheader("💬 AI Assistant")
    q = st.text_input("Ask here", key="bubble_input")

    if q:
        res = ai_suggest(q)
        for r in res:
            if st.button(f"• {r}", key=f"bubble_{r}"):
                st.session_state.selected_recipe = r
                st.session_state.ai_open = False
                st.rerun()
