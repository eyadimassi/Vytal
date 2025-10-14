# src/chatbot/memory.py

from typing import List
# --- ADD THIS IMPORT ---
from langchain_core.messages import HumanMessage, AIMessage

class ConversationMemory:
    """
    A class to manage the chat history for the chatbot.
    """
    def __init__(self):
        # Initializes an empty list to store the history.
        self.history: List[str] = []

    def add_message(self, user_message: str, bot_response: str):
        """
        Adds a user message and its corresponding bot response to the history.
        """
        self.history.append(f"User: {user_message}")
        self.history.append(f"Assistant: {bot_response}")

    def get_formatted_history(self) -> str:
        """
        Returns the entire chat history as a single, formatted string,
        ready to be inserted into a prompt.
        """
        if not self.history:
            return "No previous conversation history."
        return "\n".join(self.history)

    def load_history(self, history_list: List[str]):
        """
        Loads an existing list of messages into the memory.
        This is useful for restoring state from a session.
        """
        self.history = history_list

    def get_raw_history(self) -> List[str]:
        """
        Returns the raw list of historical messages.
        This is useful for storing the state in a session.
        """
        return self.history

    def clear(self):
        """
        Clears all messages from the history.
        """
        self.history = []

    # --- ADD THIS NEW METHOD ---
    def get_langchain_history(self) -> list:
        """
        Returns the history as a list of LangChain message objects.
        """
        lc_history = []
        # Process history in pairs (user, assistant)
        for i in range(0, len(self.history), 2):
            # Ensure we don't go out of bounds if history is uneven
            if i + 1 < len(self.history):
                user_msg = self.history[i].replace("User: ", "")
                bot_msg = self.history[i+1].replace("Assistant: ", "")
                lc_history.append(HumanMessage(content=user_msg))
                lc_history.append(AIMessage(content=bot_msg))
        return lc_history