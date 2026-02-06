import streamlit as st
import json
import os
import hashlib

from db import init_db, load_recipes, save_recipes
from ai_bot import ai_suggest

init_db()

USER_FILE = "users.json"

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# ---------- HELPERS ----------
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def load_users():
    if os.path.exists(USER_FILE):
        return json.load(open(USER_FILE))
    return {}

def save_users(u):
    json.dump(u, open(USER_FILE, "w"), indent=4)

# ---------- AUTH ----------
def auth_page():
    st.title("🔐 Login")

    users = load_users()
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in users and users[u]["password"] == hash_password(p):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.session_state.role = users[u]["role"]
                st.rerun()
            else:
                st.error("Invalid login")

    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Create"):
            users[nu] = {"password": hash_password(np), "role": "user"}
            save_users(users)
            st.success("Account created")

# ---------- MAIN APP ----------
def main_app():
    st.title("🍽️ Recipe App")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    recipes = load_recipes()

    menu = st.sidebar.selectbox(
        "Menu",
        ["Add Recipe", "View Recipes", "My Recipes", "Edit / Delete", "Search", "AI Assistant"]
    )

    # ADD
    if menu == "Add Recipe":
        with st.form("add"):
            name = st.text_input("Name")
            ing = st.text_area("Ingredients")
            steps = st.text_area("Steps")
            if st.form_submit_button("Save"):
                recipes.append({
                    "name": name,
                    "ingredients": ing,
                    "steps": steps,
                    "image": "",
                    "video": "",
                    "owner": st.session_state.user
                })
                save_recipes(recipes)
                st.success("Saved")

    # VIEW
    elif menu == "View Recipes":
        for r in recipes:
            st.subheader(r["name"])
            st.write(r["ingredients"])
            st.write(r["steps"])
            st.divider()

    # MY RECIPES
    elif menu == "My Recipes":
        for r in recipes:
            if r["owner"] == st.session_state.user:
                st.subheader(r["name"])
                st.write(r["ingredients"])
                st.write(r["steps"])
                st.divider()

    # EDIT / DELETE
    elif menu == "Edit / Delete":
        names = [r["name"] for r in recipes if r["owner"] == st.session_state.user]
        if names:
            choice = st.selectbox("Select", names)
            r = next(x for x in recipes if x["name"] == choice)

            r["ingredients"] = st.text_area("Ingredients", r["ingredients"])
            r["steps"] = st.text_area("Steps", r["steps"])

            if st.button("Update"):
                save_recipes(recipes)
                st.success("Updated")

            if st.button("Delete"):
                recipes.remove(r)
                save_recipes(recipes)
                st.warning("Deleted")

    # SEARCH
    elif menu == "Search":
        q = st.text_input("Search")
        for r in recipes:
            if q.lower() in (r["name"] + r["ingredients"]).lower():
                st.subheader(r["name"])
                st.write(r["ingredients"])
                st.write(r["steps"])
                st.divider()

    # AI
    elif menu == "AI Assistant":
        q = st.text_input("Ask AI")
        if q:
            st.markdown(ai_suggest(q))

# ---------- RUN ----------
if st.session_state.logged_in:
    main_app()
else:
    auth_page()
