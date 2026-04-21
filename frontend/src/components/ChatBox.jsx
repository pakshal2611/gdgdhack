import { useState, useRef, useEffect } from 'react';
import { sendChat } from '../services/api';

export default function ChatBox({ fileId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !fileId || loading) return;

    const userMsg = { role: 'user', content: input.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const result = await sendChat(fileId, userMsg.content);
      setMessages((prev) => [...prev, { role: 'ai', content: result.answer }]);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to get response';
      setMessages((prev) => [...prev, { role: 'ai', content: `Error: ${msg}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container" id="chat-box">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <p>Ask anything about the financial data</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble ${msg.role}`}>
            <div className="bubble-label">{msg.role === 'user' ? 'You' : 'AI Copilot'}</div>
            {msg.content}
          </div>
        ))}

        {loading && (
          <div className="chat-bubble ai">
            <div className="bubble-label">AI Copilot</div>
            <div className="typing-dots">
              <span /><span /><span />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-wrap">
        <input
          className="chat-input"
          id="chat-input-field"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={fileId ? 'Ask about the financial data...' : 'Select a file first'}
          disabled={!fileId || loading}
        />
        <button
          className="btn btn-primary"
          id="chat-send-btn"
          onClick={handleSend}
          disabled={!input.trim() || !fileId || loading}
        >
          Send
        </button>
      </div>
    </div>
  );
}
