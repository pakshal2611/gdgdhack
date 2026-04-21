import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUploader from '../components/FileUploader';
import { getFiles } from '../services/api';

export default function UploadPage() {
  const navigate = useNavigate();
  const [recentFiles, setRecentFiles] = useState([]);

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      const result = await getFiles();
      setRecentFiles(result.files || []);
    } catch {
      // Backend might not be running yet
      const stored = JSON.parse(localStorage.getItem('uploadedFiles') || '[]');
      setRecentFiles(stored);
    }
  };

  const handleUploadSuccess = (result) => {
    // Store in localStorage for quick access
    const stored = JSON.parse(localStorage.getItem('uploadedFiles') || '[]');
    const newFile = { id: result.file_id, filename: result.filename, rows: result.rows_extracted };
    stored.unshift(newFile);
    localStorage.setItem('uploadedFiles', JSON.stringify(stored.slice(0, 20)));

    // Navigate to dashboard after short delay
    setTimeout(() => navigate(`/dashboard/${result.file_id}`), 1500);
  };

  return (
    <div className="page" id="upload-page">
      <div className="hero fade-in">
        <h1>Financial Intelligence Copilot</h1>
        <p>Upload financial documents and get AI-powered insights, interactive analysis, and exportable reports</p>
      </div>

      <div style={{ maxWidth: '700px', margin: '0 auto' }}>
        <FileUploader onUploadSuccess={handleUploadSuccess} />
      </div>

      {recentFiles.length > 0 && (
        <div className="file-list fade-in" style={{ maxWidth: '700px', margin: '2rem auto 0' }}>
          <h3>📁 Recent Uploads</h3>
          {recentFiles.map((f) => (
            <div key={f.id} className="file-item">
              <span className="file-name">{f.filename}</span>
              <div className="file-actions">
                <button className="btn btn-ghost" onClick={() => navigate(`/dashboard/${f.id}`)}>
                  📊 Dashboard
                </button>
                <button className="btn btn-ghost" onClick={() => navigate(`/chat?file=${f.id}`)}>
                  💬 Chat
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
