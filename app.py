import streamlit as st
import os
import json
import base64
import hashlib

from ai_bot import ai_suggest
from db import init_db, load_recipes

init_db()

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "selected_recipe" not in st.session_state:
    st.session_state.selected_recipe = None

# ---------------- USERS ----------------
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ---------------- LOGIN ----------------
def auth_page():
    st.title("🔐 Login")
    users = load_users()

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in users:
            if users[u]["role"] == "admin":
                valid = users[u]["password"] == p
            else:
                valid = users[u]["password"] == hash_password(p)

            if valid:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.session_state.role = users[u]["role"]
                st.rerun()
            else:
                st.error("Invalid credentials")
        else:
            st.error("Invalid credentials")

# ---------------- MAIN APP ----------------
def main_app():
    st.title("🍽️ Recipe App")

    st.sidebar.write(f"👤 {st.session_state.current_user}")
    st.sidebar.write(f"🛡️ {st.session_state.role}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    recipes = load_recipes()

    # ---------- MENU (UNCHANGED) ----------
    if st.session_state.role == "admin":
        menu = st.sidebar.selectbox(
            "Menu",
            ["Add Recipe", "View / Edit / Delete", "Search", "AI Assistant"]
        )
    else:
        menu = st.sidebar.selectbox(
            "Menu",
            ["Add Recipe", "My Recipes", "View Recipes", "Search", "AI Assistant"]
        )

    # ---------- ADD RECIPE ----------
    if menu == "Add Recipe":
        st.subheader("➕ Add Recipe")
        st.info("Your existing Add Recipe logic stays here")

    # ---------- MY RECIPES ----------
    elif menu == "My Recipes":
        st.subheader("📂 My Recipes")
        st.info("Your existing My Recipes logic stays here")

    # ---------- VIEW RECIPES ----------
    elif menu == "View Recipes":
        if st.session_state.selected_recipe:
            recipes = [
                r for r in recipes
                if r["name"] == st.session_state.selected_recipe
            ]
            st.session_state.selected_recipe = None

        for r in recipes:
            st.subheader(r["name"])
            st.write(r["ingredients"])
            st.write(r["steps"])
            st.divider()

    # ---------- ADMIN VIEW / EDIT ----------
    elif menu == "View / Edit / Delete":
        st.subheader("🛠️ Manage Recipes")
        st.info("Your existing admin edit/delete logic stays here")

    # ---------- SEARCH ----------
    elif menu == "Search":
        st.subheader("🔍 Search Recipes")
        st.info("Your existing search logic stays here")

    # ---------- AI ASSISTANT (FIXED) ----------
    elif menu == "AI Assistant":
        st.subheader("🤖 AI Recipe Assistant")

        user_query = st.text_input("Ask using ingredients or sentences")

        if user_query:
            with st.spinner("Thinking..."):
                suggested = ai_suggest(user_query)

            if suggested:
                st.markdown("✨ Suggested Recipes")
                for name in suggested:
                    if st.button(name, key=f"ai_{name}"):
                        st.session_state.selected_recipe = name
                        st.session_state.menu = "View Recipes"
                        st.rerun()
            else:
                st.info("No related recipes found")

# ---------------- RUN ----------------
if st.session_state.logged_in:
    main_app()
else:
    auth_page()
