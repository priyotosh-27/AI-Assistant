from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import requests

# Load API key from .env
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)

def get_ai_response(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost:5000",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mistralai/mistral-7b-instruct",  # ✅ FREE, WORKING MODEL
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        result = response.json()

        # Safe handling of response
        if "choices" in result:
            return result["choices"][0]["message"]["content"].strip()
        elif "error" in result:
            return f"⚠️ API Error: {result['error'].get('message', 'Unknown error')}"
        else:
            return f"⚠️ Unexpected response: {result}"
    except Exception as e:
        return f"⚠️ Exception: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    ai_response = ""
    if request.method == "POST":
        user_input = request.form["user_input"]
        action = request.form["action"]

        # Define prompt type
        if action == "question":
            prompt = f"Answer this factual question: {user_input}"
        elif action == "summary":
            prompt = f"Summarize this: {user_input}"
        elif action == "creative":
            prompt = f"Write a short story or poem based on: {user_input}"
        else:
            prompt = user_input

        # Get response from OpenRouter
        ai_response = get_ai_response(prompt)

        # Save feedback if provided
        feedback = request.form.get("feedback")
        if feedback:
            with open("feedback.txt", "a", encoding="utf-8") as f:
                f.write(f"Input: {user_input}\nResponse: {ai_response}\nFeedback: {feedback}\n\n")

    return render_template("index.html", response=ai_response)

if __name__ == "__main__":
    app.run(debug=True)
