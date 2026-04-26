import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUploader from '../components/FileUploader';
import { getFiles, loadDemo } from '../services/api';

function getFileIcon(filename = '') {
  const ext = filename.split('.').pop().toLowerCase();
  if (ext === 'pdf') return '📄';
  if (['xlsx', 'xls', 'csv'].includes(ext)) return '📊';
  if (['png', 'jpg', 'jpeg'].includes(ext)) return '🖼';
  return '📁';
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
    });
  } catch {
    return '';
  }
}

function truncate(str, max = 30) {
  if (!str) return '';
  return str.length > max ? str.slice(0, max) + '…' : str;
}

export default function UploadPage() {
  const navigate = useNavigate();
  const [recentFiles, setRecentFiles] = useState([]);
  const [demoLoading, setDemoLoading] = useState(false);
  const [demoError, setDemoError] = useState('');

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      const result = await getFiles();
      setRecentFiles(result.files || []);
    } catch {
      const stored = JSON.parse(localStorage.getItem('uploadedFiles') || '[]');
      setRecentFiles(stored);
    }
  };

  const handleUploadSuccess = (result) => {
    const stored = JSON.parse(localStorage.getItem('uploadedFiles') || '[]');
    const newFile = {
      id: result.file_id,
      filename: result.filename,
      rows: result.rows_extracted,
      upload_time: new Date().toISOString(),
    };
    stored.unshift(newFile);
    localStorage.setItem('uploadedFiles', JSON.stringify(stored.slice(0, 20)));
    localStorage.setItem('lastFileId', result.file_id);
    setTimeout(() => navigate(`/dashboard/${result.file_id}`), 1500);
  };

  const handleLoadDemo = async () => {
    setDemoLoading(true);
    setDemoError('');
    try {
      const result = await loadDemo();
      localStorage.setItem('lastFileId', result.file_id);
      navigate(`/dashboard/${result.file_id}`);
    } catch (err) {
      setDemoError(err.response?.data?.detail || 'Failed to load demo data');
    } finally {
      setDemoLoading(false);
    }
  };

  const handleDeleteFile = (id) => {
    const stored = JSON.parse(localStorage.getItem('uploadedFiles') || '[]');
    const updated = stored.filter((f) => f.id !== id);
    localStorage.setItem('uploadedFiles', JSON.stringify(updated));
    setRecentFiles((prev) => prev.filter((f) => f.id !== id));
  };

  return (
    <div className="page" id="upload-page">
      <div className="hero fade-in">
        <h1>Financial Intelligence Copilot</h1>
        <p>Upload financial documents and get AI-powered insights, interactive analysis, and exportable reports</p>
      </div>

      <div style={{ maxWidth: '700px', margin: '0 auto' }}>
        <FileUploader onUploadSuccess={handleUploadSuccess} />

        {/* Sample Data Button */}
        <div className="sample-data-section">
          <button
            className="btn btn-secondary"
            id="load-demo-btn"
            onClick={handleLoadDemo}
            disabled={demoLoading}
          >
            {demoLoading ? '⏳ Loading…' : '🎯 Load Sample Data'}
          </button>
          <p className="sample-data-note">Try the app instantly with sample financial data</p>
          {demoError && <p style={{ color: 'var(--danger)', fontSize: '0.85rem', marginTop: '0.4rem' }}>{demoError}</p>}
        </div>
      </div>

      {recentFiles.length > 0 && (
        <div className="file-list fade-in" style={{ maxWidth: '700px', margin: '2rem auto 0' }}>
          <h3>📁 Recent Uploads</h3>
          {recentFiles.map((f) => (
            <div key={f.id} className="file-item">
              <div className="file-item-top">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', minWidth: 0 }}>
                  <span className="file-type-icon">{getFileIcon(f.filename)}</span>
                  <div style={{ minWidth: 0 }}>
                    <span className="file-name" title={f.filename}>
                      {truncate(f.filename, 30)}
                    </span>
                    {f.upload_time && (
                      <div className="file-meta">{formatDate(f.upload_time)}</div>
                    )}
                  </div>
                </div>
                <button
                  className="btn btn-ghost"
                  style={{ fontSize: '1rem', padding: '0.3rem 0.6rem' }}
                  onClick={() => handleDeleteFile(f.id)}
                  title="Remove from list"
                >
                  🗑
                </button>
              </div>
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
