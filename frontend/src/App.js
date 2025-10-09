// frontend/src/App.js
import React, { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';
import './App.css';

// --- Import your logo ---
// Make sure you have a logo.png file in frontend/src/assets/
import logo from './assets/logo.png';

const SendIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" fill="white"/>
  </svg>
);

// Define the initial message outside the component
const initialMessage = { 
  sender: 'bot', 
  text: "Hi! I'm Vytal, how can I help you?" 
};

function App() {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([initialMessage]);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState('current');
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef(null);

  const API_URL = 'http://localhost:8080/api/chat';

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isLoading]);

  const startNewConversation = () => {
    setChatHistory([initialMessage]);
    setActiveConversationId('current');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const userMessage = { sender: 'user', text: message };
    const newChatHistory = [...chatHistory, userMessage];
    
    setChatHistory(newChatHistory);
    setMessage('');
    setIsLoading(true);

    try {
      const historyForApi = newChatHistory.map(msg => 
        `${msg.sender === 'user' ? 'User' : 'Assistant'}: ${msg.text}`
      );

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.text,
          chat_history: historyForApi.slice(0, -1)
        }),
      });

      if (!response.ok) throw new Error(`Network error: ${response.status}`);

      const data = await response.json();
      const botMessage = { sender: 'bot', text: data.response };
      setChatHistory(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Error:', error);
      const errorMessage = { sender: 'bot', text: 'Sorry, something went wrong. Please try again.' };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-layout">
      {/* --- Sidebar --- */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <img src={logo} alt="VytalChat Logo" className="logo" />
          <h1>VytalChat</h1>
        </div>
        <button className="new-chat-button" onClick={startNewConversation}>
          + New Chat
        </button>
        <div className="conversations-list">
          <div 
            className={`conversation-item ${activeConversationId === 'current' ? 'active' : ''}`} 
            onClick={startNewConversation}
          >
            Current Conversation
          </div>
        </div>
      </aside>

      {/* --- Main Chat Area --- */}
      <main className="chat-area">
        <div className="chat-content">
          {chatHistory.map((msg, index) => (
            <div key={index} className={`message-wrapper ${msg.sender}`}>
              <div className="avatar">
                {msg.sender === 'bot' ? 'V' : 'U'}
              </div>
              <div className="message-bubble" dangerouslySetInnerHTML={{ __html: marked.parse(msg.text) }} />
            </div>
          ))}
          {isLoading && (
            <div className="message-wrapper bot">
              <div className="avatar">V</div>
              <div className="message-bubble">Thinking...</div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
        
        <div className="input-container">
          <form className="input-form" onSubmit={handleSubmit}>
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.g.target.value)}
              placeholder="Ask Vytal anything..."
              autoComplete="off"
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !message.trim()}>
              <SendIcon />
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default App;