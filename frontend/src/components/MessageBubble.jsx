import React from 'react';
import './ChatWindow.css';

function MessageBubble({ text, sender }) {
  return (
    <div className={`message-row ${sender}`}>
      {/* Bot avatar always visible */}
      {sender === 'bot' && <div className="avatar">
        <img src="/images/robot.png" alt="Bot Avatar" />
      </div>}

      <div className={`bubble ${sender}-bubble`}>
        <p>{text}</p>
      </div>
    </div>
  );
}

export default MessageBubble;
