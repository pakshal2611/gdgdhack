import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import ChatBox from '../components/ChatBox';

export default function ChatPage() {
  const [searchParams] = useSearchParams();
  const [fileId, setFileId] = useState(searchParams.get('file') || '');
  const [files, setFiles] = useState([]);

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem('uploadedFiles') || '[]');
    setFiles(stored);
    if (!fileId && stored.length > 0) {
      setFileId(String(stored[0].id));
    }
  }, []);

  return (
    <div className="page" id="chat-page">
      <div className="page-header fade-in">
        <h1 className="page-title">AI Chat</h1>
        <p className="page-subtitle">Ask questions about your financial data using RAG-powered AI</p>
      </div>

      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        <div className="chat-file-select fade-in">
          <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Analyzing:</label>
          <select
            value={fileId}
            onChange={(e) => setFileId(e.target.value)}
            id="chat-file-selector"
          >
            <option value="">Select a file</option>
            {files.map((f) => (
              <option key={f.id} value={f.id}>{f.filename}</option>
            ))}
          </select>
        </div>

        <ChatBox fileId={fileId ? Number(fileId) : null} />
      </div>
    </div>
  );
}
