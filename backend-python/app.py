# backend-python/app.py

import os
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS  # <-- IMPORT CORS
from src.chatbot.chain import get_chatbot_response
from src.chatbot.memory import ConversationMemory

app = Flask(__name__)
CORS(app)  # <-- ENABLE CORS FOR THE ENTIRE APP
app.secret_key = os.urandom(24)

# We no longer need the home route, as React will handle the UI
# @app.route("/")
# def home(): ...

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json["message"]
        # IMPORTANT: The session is now managed by the Node.js service,
        # so we receive the history in the request.
        raw_history = request.json.get("chat_history", [])
        
        memory = ConversationMemory()
        memory.load_history(raw_history)

        bot_response = get_chatbot_response(user_message, memory)
        
        # We also return the updated history
        memory.add_message(user_message, bot_response)
        updated_history = memory.get_raw_history()

        return jsonify({
            "response": bot_response,
            "chat_history": updated_history
        })

    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

# We no longer need the __main__ block for Gunicorn
# if __name__ == "__main__": ...