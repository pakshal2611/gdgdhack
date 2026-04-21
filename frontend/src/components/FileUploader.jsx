import { useState, useRef } from 'react';
import { uploadFile } from '../services/api';

export default function FileUploader({ onUploadSuccess }) {
  const [dragging, setDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [statusType, setStatusType] = useState('');
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef(null);

  const handleDrag = (e) => { e.preventDefault(); e.stopPropagation(); };
  const handleDragIn = (e) => { handleDrag(e); setDragging(true); };
  const handleDragOut = (e) => { handleDrag(e); setDragging(false); };

  const handleDrop = (e) => {
    handleDrag(e);
    setDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file) => {
    const ext = file.name.split('.').pop().toLowerCase();
    const allowed = ['pdf', 'xlsx', 'xls', 'csv', 'png', 'jpg', 'jpeg'];
    if (!allowed.includes(ext)) {
      setStatus('Unsupported file type. Please upload PDF, Excel, or Image files.');
      setStatusType('error');
      return;
    }

    setUploading(true);
    setProgress(0);
    setStatus('Uploading and processing...');
    setStatusType('');

    try {
      const result = await uploadFile(file, setProgress);
      setStatus(`✅ ${result.filename} uploaded — ${result.rows_extracted} rows extracted`);
      setStatusType('success');
      if (onUploadSuccess) onUploadSuccess(result);
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Upload failed';
      setStatus(`❌ ${msg}`);
      setStatusType('error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div
      className={`upload-zone ${dragging ? 'drag-over' : ''}`}
      onDragOver={handleDrag}
      onDragEnter={handleDragIn}
      onDragLeave={handleDragOut}
      onDrop={handleDrop}
      onClick={() => !uploading && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.xlsx,.xls,.csv,.png,.jpg,.jpeg"
        onChange={handleFileInput}
        style={{ display: 'none' }}
        id="file-upload-input"
      />
      <div className="upload-icon">📄</div>
      <h3>Drop your financial document here</h3>
      <p>Supports PDF, Excel (.xlsx/.xls/.csv), and Images (.png/.jpg)</p>

      {uploading && (
        <div className="upload-progress">
          <div className="progress-bar-track">
            <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}

      {status && (
        <div className={`upload-status ${statusType}`}>{status}</div>
      )}
    </div>
  );
}
