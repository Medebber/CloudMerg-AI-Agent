import React from 'react';
import ChatWindow from './components/ChatWindow';
import './App.css';

function App() {
  return (
    <div className="page-container">
      <div className="app-box">
        <header className="app-header">
          <h1 className="main-title">CloudMerg AI-Agent</h1>
          <p className="subtitle">Qatar's Digital Future, Powered by AI</p>
        </header>
        <div className="chat-section">
          <ChatWindow />
        </div>
      </div>
    </div>
  );
}

export default App;

// npm start