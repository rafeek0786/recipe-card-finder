import os
import requests

def ai_suggest(user_query):
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return "❌ GROQ_API_KEY not found. Please add it in Streamlit Secrets."

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful recipe assistant. Answer clearly and simply."
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

        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Error: {str(e)}"
