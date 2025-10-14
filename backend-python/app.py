# backend-python/app.py

import os
import logging  # <-- IMPORT LOGGING
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.chatbot.chain import get_chatbot_response
from src.chatbot.memory import ConversationMemory

# --- ADD THIS LOGGING CONFIGURATION ---
# This ensures all log messages, including tracebacks, are sent to the console.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# -----------------------------------------

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json["message"]
        raw_history = request.json.get("chat_history", [])
        
        memory = ConversationMemory()
        memory.load_history(raw_history)

        bot_response = get_chatbot_response(user_message, memory)
        
        memory.add_message(user_message, bot_response)
        updated_history = memory.get_raw_history()

        return jsonify({
            "response": bot_response,
            "chat_history": updated_history
        })

    except Exception as e:
        # Use logging.exception to capture the full error traceback in the logs
        logging.exception("An unhandled error occurred in the /chat endpoint")
        return jsonify({"error": "An internal server error occurred."}), 500