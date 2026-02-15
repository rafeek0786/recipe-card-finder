import os
import requests

def ai_suggest(user_query):
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return "❌ AI key missing. Check Streamlit Secrets."

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful recipe assistant."},
            {"role": "user", "content": user_query}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        return "❌ AI error. Try again later."

    return response.json()["choices"][0]["message"]["content"]
