import os
import requests

def generate_blog(prompt):
    key = os.getenv("GEMINI_API_KEY")
    
    # Example structure for Gemini API call (replace with your specific endpoint/setup)
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gemini-pro",
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 300
    }

    response = requests.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                             headers=headers,
                             json={"contents": [{"parts": [{"text": prompt}]}]})

    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"❌ Gemini API error: {response.status_code} - {response.text}"