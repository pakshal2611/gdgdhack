import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getAnalysis, downloadExcel } from '../services/api';
import DataTable from '../components/DataTable';
import Charts from '../components/Charts';
import RatioCards from '../components/RatioCards';
import AnomalyPanel from '../components/AnomalyPanel';
import YoYTable from '../components/YoYTable';

export default function Dashboard() {
  const { fileId } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (fileId) fetchAnalysis();
  }, [fileId]);

  const fetchAnalysis = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getAnalysis(fileId);
      setAnalysis(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load analysis');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      await downloadExcel(fileId);
    } catch (err) {
      alert('Export failed: ' + (err.message || 'Unknown error'));
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="page">
        <div className="skeleton-grid">
          <div className="skeleton-card" />
          <div className="skeleton-card" />
          <div className="skeleton-card" />
          <div className="skeleton-card" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <div className="empty-state">
          <div className="empty-icon">⚠️</div>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={fetchAnalysis} style={{ marginTop: '1rem' }}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  const filename = analysis?.filename || `File #${fileId}`;
  const displayName = filename.replace('.pdf', '').replace(/_/g, ' ');

  return (
    <div className="page" id="dashboard-page">

      {/* Breadcrumb */}
      <nav className="breadcrumb fade-in">
        <span className="breadcrumb-item"><Link to="/">Home</Link></span>
        <span className="breadcrumb-item">Dashboard</span>
        <span className="breadcrumb-item">{displayName}</span>
      </nav>

      {/* Top bar */}
      <div className="dashboard-top-bar fade-in">
        <div className="page-header" style={{ marginBottom: 0 }}>
          <h1 className="page-title">📊 {displayName}</h1>
          <p className="page-subtitle">
            Financial Intelligence Report
            <button
              className="btn btn-ghost"
              id="refresh-btn"
              onClick={fetchAnalysis}
              style={{ marginLeft: '0.75rem', fontSize: '0.85rem', padding: '0.25rem 0.75rem' }}
              title="Refresh analysis"
            >
              🔄 Refresh
            </button>
          </p>
        </div>
        <button
          className="btn btn-primary"
          id="export-btn"
          onClick={handleExport}
          disabled={exporting}
        >
          {exporting ? '⏳ Generating…' : '📥 Export Excel'}
        </button>
      </div>

      <div className="dashboard-grid">
        {/* Ratio Cards */}
        <RatioCards ratios={analysis?.ratios} trend={analysis?.trend} />

        {/* Charts */}
        <Charts data={analysis?.data} yoyData={analysis?.yoy_growth} />

        {/* YoY Table */}
        <YoYTable yoyData={analysis?.yoy_growth} />

        {/* Anomaly Panel */}
        <AnomalyPanel anomalies={analysis?.anomalies} />

        {/* Data Table */}
        <div className="card fade-in">
          <div className="card-header">
            <span className="card-title">📋 Financial Data</span>
          </div>
          <DataTable data={analysis?.data} />
        </div>

        {/* AI Insights */}
        {analysis?.insights && (
          <div className="card insights-card fade-in">
            <div className="card-header">
              <span className="card-title">🧠 AI Insights</span>
            </div>
            <div className="ai-badge">✨ RAG-Powered Analysis</div>
            <div className="insights-text">{analysis.insights}</div>
          </div>
        )}
      </div>

      {/* Floating Chat Button — only on Dashboard */}
      <button
        className="fab-chat"
        id="fab-chat-btn"
        onClick={() => navigate(`/chat?file=${fileId}`)}
        title="Chat with your data"
      >
        💬
      </button>
    </div>
  );
}
