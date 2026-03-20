import './ChatMessage.css';

export default function ChatMessage({ role, content, index }) {
  const isUser = role === 'user';

  return (
    <div 
      className={`chat-message ${isUser ? 'msg-user' : 'msg-ai'}`}
      style={{ animationDelay: `${index * 0.05}s` }}
    >
      <div className="msg-avatar">
        {isUser ? (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        ) : (
          <span className="ai-icon">🧠</span>
        )}
      </div>
      <div className="msg-body">
        <span className="msg-role font-mono">{isUser ? 'You' : 'Clarity Rx'}</span>
        <div className="msg-content">{content}</div>
      </div>
    </div>
  );
}
