# app.py

import os
from flask import Flask, render_template, request, jsonify, session
from src.chatbot.chain import get_chatbot_response
from src.chatbot.memory import ConversationMemory  # <-- IMPORT THE NEW CLASS

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route("/")
def home():
    """Render the chat interface and initialize chat history in session."""
    # We store the raw list in the session.
    session['chat_history'] = []
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat messages using the ConversationMemory class."""
    try:
        user_message = request.json["message"]
        
        # 1. Create a new memory instance for this request.
        memory = ConversationMemory()
        
        # 2. Load the previous history from the Flask session into the object.
        raw_history = session.get('chat_history', [])
        memory.load_history(raw_history)

        # 3. Pass the entire memory object to the chatbot function.
        bot_response = get_chatbot_response(user_message, memory)

        # 4. Update the memory object with the new conversation turn.
        memory.add_message(user_message, bot_response)
        
        # 5. Save the updated raw history list back to the session.
        session['chat_history'] = memory.get_raw_history()

        return jsonify({"response": bot_response})

    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)