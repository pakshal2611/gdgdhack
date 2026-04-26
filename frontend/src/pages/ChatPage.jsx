import { useState, useRef, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { getFiles, sendChat, getChatHistory } from '../services/api';

export default function ChatPage() {
  const [searchParams] = useSearchParams();
  
  // State
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [eli15Mode, setEli15Mode] = useState(false);
  const [selectedFileId, setSelectedFileId] = useState(searchParams.get('file') || '');
  const [files, setFiles] = useState([]);
  const messagesEndRef = useRef(null);

  // Load files on mount
  useEffect(() => {
    const loadFiles = async () => {
      try {
        const data = await getFiles();
        setFiles(data.files || []);
        // If file ID from URL, set it; otherwise use first file
        if (!selectedFileId && data.files && data.files.length > 0) {
          setSelectedFileId(String(data.files[0].id));
        }
      } catch (err) {
        // Fallback to localStorage
        const stored = JSON.parse(localStorage.getItem('uploadedFiles') || '[]');
        setFiles(stored);
        if (!selectedFileId && stored.length > 0) {
          setSelectedFileId(String(stored[0].id));
        }
      }
    };
    loadFiles();
  }, []);

  // Load chat history when file ID changes
  useEffect(() => {
    if (!selectedFileId) {
      setMessages([]);
      return;
    }

    const loadHistory = async () => {
      try {
        const data = await getChatHistory(selectedFileId);
        const loadedMessages = (data.history || []).map(msg => ({
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.created_at)
        }));
        setMessages(loadedMessages);
      } catch (err) {
        console.error('Failed to load chat history:', err);
        setMessages([]);
      }
    };
    loadHistory();
  }, [selectedFileId]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim() || !selectedFileId || loading) return;

    const userQuery = input.trim();
    const userMsg = { role: 'user', content: userQuery, timestamp: new Date() };
    
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const result = await sendChat(selectedFileId, userQuery, eli15Mode);
      const assistantMsg = { role: 'assistant', content: result.answer, timestamp: new Date() };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to get response';
      const errorMsg = { role: 'assistant', content: `Error: ${msg}`, timestamp: new Date() };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const handleQuestionClick = (question) => {
    setInput(question);
  };

  const formatTime = (date) => {
    if (!date) return '';
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const suggestedQuestions = [
    "What is the revenue trend over the last 5 years?",
    "Which year had the highest profit margin?",
    "Are there any financial anomalies I should be aware of?",
    "What is the EBITDA margin and what does it mean?",
    "Give me a summary of this company's financial health"
  ];

  return (
    <div className="page" id="chat-page">
      {/* TOP BAR */}
      <div className="chat-top-bar">
        <div className="chat-file-select">
          <label>Analyzing:</label>
          <select value={selectedFileId} onChange={(e) => setSelectedFileId(e.target.value)}>
            <option value="">Select a file...</option>
            {files.map((f) => (
              <option key={f.id} value={f.id}>{f.filename}</option>
            ))}
          </select>
        </div>

        <button
          className={`eli15-toggle ${eli15Mode ? 'active' : ''}`}
          onClick={() => setEli15Mode(!eli15Mode)}
        >
          {eli15Mode ? '🎓 Expert Mode' : '👶 Simple Mode'}
        </button>

        <button className="btn btn-ghost" onClick={clearChat}>
          🗑 Clear
        </button>
      </div>

      {/* SUGGESTED QUESTIONS */}
      {messages.length === 0 && selectedFileId && (
        <div className="suggested-questions">
          <p className="suggested-label">Try asking:</p>
          <div className="question-chips">
            {suggestedQuestions.map((question, i) => (
              <button
                key={i}
                className="question-chip"
                onClick={() => handleQuestionClick(question)}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* CHAT MESSAGES */}
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble ${msg.role === 'user' ? 'user' : 'ai'}`}>
            <div className="bubble-label">
              {msg.role === 'user' ? 'You' : '🧠 FinCopilot AI'}
            </div>
            <div className="bubble-content">{msg.content}</div>
            {msg.timestamp && (
              <div className="bubble-time">{formatTime(msg.timestamp)}</div>
            )}
          </div>
        ))}

        {loading && (
          <div className="chat-bubble ai">
            <div className="bubble-label">🧠 FinCopilot AI</div>
            <div className="typing-dots">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* INPUT BAR */}
      <div className="chat-input-wrap">
        <input
          className="chat-input"
          type="text"
          placeholder={
            eli15Mode
              ? 'Ask anything (simple mode on)...'
              : 'Ask about the financial data...'
          }
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          disabled={loading || !selectedFileId}
        />
        <button
          className="btn btn-primary"
          onClick={handleSend}
          disabled={loading || !input.trim() || !selectedFileId}
        >
          {loading ? '...' : '➤ Send'}
        </button>
      </div>

      {/* MODE INDICATOR */}
      {eli15Mode && (
        <div className="eli15-indicator">
          👶 Simple Mode ON — responses will use plain English
        </div>
      )}
    </div>
  );
}
