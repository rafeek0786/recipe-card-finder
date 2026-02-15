import os
import requests
import streamlit as st

def ai_suggest(user_query):
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return "❌ GROQ_API_KEY not found in Secrets"

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful recipe assistant."
            },
            {
                "role": "user",
                "content": user_query
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            return f"❌ Groq API Error: {response.text}"

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Exception: {str(e)}"
