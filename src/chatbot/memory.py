# src/chatbot/memory.py

from typing import List

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