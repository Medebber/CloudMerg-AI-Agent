
import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import './ChatWindow2.css';

function ChatWindow() {
  // Base URL for API. In production (served by backend) keep blank so relative paths work.
  const API_BASE = process.env.REACT_APP_API_URL || '';
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Hello 👋, I am CloudMerg AI Assistant. How can I help you today?',
    },
  ]);

  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = { sender: 'user', text: input };
    const currentInput = input;
    setInput('');

    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: currentInput,
          history: messages.map((m) => [m.sender, m.text]),
        }),
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      let botText = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        botText += chunk;

        setMessages((prev) => {
          const updated = [...prev];
          if (updated[updated.length - 1]?.sender !== 'bot') {
            updated.push({ sender: 'bot', text: botText });
          } else {
            updated[updated.length - 1].text = botText;
          }
          return updated;
        });
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: 'bot', text: 'Error: backend unreachable.' },
      ]);
    }

    setIsTyping(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  // Generate timestamp
  const getTimestamp = () => {
    const now = new Date();
    return now.toLocaleString(); // date + time
  };

  return (
    <div className="chat-window">
      <div className="messages">
        {/* System message at the top */}
        <div className="system-message">
          <p>Connected to Agent</p>
          <span className="timestamp">{getTimestamp()}</span>
        </div>

        {messages.map((msg, i) => (
          <MessageBubble key={i} text={msg.text} sender={msg.sender} />
        ))}

        {/* Typing indicator with bot avatar */}
        {isTyping && (
          <div className="message-row bot">
            <div className="avatar">
              <img src="/images/robot.png" alt="Bot Avatar" />
            </div>
            <div className="typing-bubble">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Ask something..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

export default ChatWindow;
