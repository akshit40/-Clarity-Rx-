import { useState, useEffect } from 'react';
import './ChatMessage.css';

export default function ChatMessage({ role, content, index }) {
  const isUser = role === 'user';
  const [displayText, setDisplayText] = useState(isUser ? content : '');
  const [isTyping, setIsTyping] = useState(!isUser);
  const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  useEffect(() => {
    if (isUser) return;

    let i = 0;
    const interval = setInterval(() => {
      setDisplayText(content.slice(0, i + 1));
      i++;
      if (i >= content.length) {
        clearInterval(interval);
        setIsTyping(false);
      }
    }, 15); // adjust speed here

    return () => clearInterval(interval);
  }, [content, isUser]);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    // showToast equivalent? Since this is a small component, we'll just use a tooltip or icon change if needed
  };

  return (
    <div 
      className={`chat-message ${isUser ? 'msg-user' : 'msg-ai'} ${isTyping ? 'is-typing' : ''}`}
      style={{ animationDelay: `${index * 0.05}s` }}
    >
      <div className={`msg-avatar ${isUser ? 'avatar-gradient' : ''}`}>
        {isUser ? (
          <span style={{ fontSize: '10px' }}>U</span>
        ) : (
          <span className="ai-icon">🧠</span>
        )}
      </div>
      <div className="msg-body">
        <div className="msg-header">
          <span className="msg-role font-mono">{isUser ? 'You' : 'Clarity Rx'}</span>
          <span className="msg-time">{timestamp}</span>
        </div>
        <div className="msg-content">
          {displayText}
          {!isUser && isTyping && <span className="typewriter-cursor">|</span>}
        </div>
        {!isUser && !isTyping && (
          <button className="copy-btn" onClick={handleCopy} title="Copy Advice">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            Copy
          </button>
        )}
      </div>
    </div>
  );
}
