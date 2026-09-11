"""
app.py

Flask backend for the Game Guide AI chatbot.
Handles serving the chat UI and proxying chat messages to the Gemini API.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

from chatbot_config import SYSTEM_PROMPT

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Please add it to your .env file."
    )

genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

# Create the model once with the fixed system instruction so every
# request is grounded in the Game Guide AI persona.
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=SYSTEM_PROMPT,
)


@app.route("/")
def index():
    """Serve the chat UI."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Receive a user message and return the model's reply."""
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    try:
        response = model.generate_content(user_message)
        reply_text = response.text
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"Failed to get a response: {exc}"}), 500

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(debug=True)
