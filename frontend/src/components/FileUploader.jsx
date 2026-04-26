import { useState, useRef, useEffect } from 'react';
import { uploadFile } from '../services/api';

const STEPS = [
  '📄 Reading document…',
  '🧹 Cleaning data…',
  '📊 Computing ratios…',
  '🤖 Building AI index…',
  '✅ Ready!',
];

const MAX_SIZE_MB = 50;

function getFileIcon(filename = '') {
  const ext = filename.split('.').pop().toLowerCase();
  if (ext === 'pdf') return '📄';
  if (['xlsx', 'xls', 'csv'].includes(ext)) return '📊';
  if (['png', 'jpg', 'jpeg'].includes(ext)) return '🖼';
  return '📁';
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function FileUploader({ onUploadSuccess }) {
  const [dragging, setDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [statusType, setStatusType] = useState('');
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [currentStep, setCurrentStep] = useState(-1);
  const inputRef = useRef(null);
  const stepTimerRef = useRef(null);

  // Cycle through steps while uploading
  useEffect(() => {
    if (uploading) {
      setCurrentStep(0);
      let step = 0;
      stepTimerRef.current = setInterval(() => {
        step = Math.min(step + 1, STEPS.length - 2); // don't reach "Ready" automatically
        setCurrentStep(step);
      }, 700);
    } else {
      clearInterval(stepTimerRef.current);
    }
    return () => clearInterval(stepTimerRef.current);
  }, [uploading]);

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

    // 50 MB size check
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setStatus(`File too large. Maximum size is ${MAX_SIZE_MB}MB.`);
      setStatusType('error');
      return;
    }

    setSelectedFile(file);
    setUploading(true);
    setProgress(0);
    setStatus('');
    setStatusType('');

    try {
      const result = await uploadFile(file, setProgress);
      clearInterval(stepTimerRef.current);
      setCurrentStep(STEPS.length - 1); // jump to "Ready!"
      setStatus(`✅ ${result.filename} uploaded — ${result.rows_extracted} rows extracted`);
      setStatusType('success');
      if (onUploadSuccess) onUploadSuccess(result);
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Upload failed';
      setStatus(`❌ ${msg}`);
      setStatusType('error');
      setCurrentStep(-1);
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

      {/* Selected file preview */}
      {selectedFile && !status && (
        <div className="file-preview-row" onClick={(e) => e.stopPropagation()}>
          <span className="file-type-icon">{getFileIcon(selectedFile.name)}</span>
          <span className="file-preview-name">{selectedFile.name}</span>
          <span className="file-preview-size">{formatSize(selectedFile.size)}</span>
        </div>
      )}

      {/* Progress bar */}
      {uploading && (
        <div className="upload-progress" onClick={(e) => e.stopPropagation()}>
          <div className="progress-bar-track">
            <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}

      {/* Processing steps */}
      {uploading && currentStep >= 0 && (
        <div className="upload-steps" onClick={(e) => e.stopPropagation()}>
          {STEPS.map((label, idx) => {
            let cls = 'upload-step';
            if (idx < currentStep) cls += ' done';
            else if (idx === currentStep) cls += ' active';
            return (
              <div key={idx} className={cls}>
                <span className="step-dot" />
                {label}
              </div>
            );
          })}
        </div>
      )}

      {/* Status message */}
      {status && (
        <div className={`upload-status ${statusType}`} onClick={(e) => e.stopPropagation()}>
          {status}
        </div>
      )}
    </div>
  );
}
