import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getAnalysis, downloadExcel } from '../services/api';
import DataTable from '../components/DataTable';
import Charts from '../components/Charts';
import RatioCards from '../components/RatioCards';

export default function Dashboard() {
  const { fileId } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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
    try {
      await downloadExcel(fileId);
    } catch (err) {
      alert('Export failed: ' + (err.message || 'Unknown error'));
    }
  };

  if (loading) {
    return (
      <div className="page">
        <div className="loading-container">
          <div className="spinner" />
          <p>Analyzing financial data...</p>
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

  return (
    <div className="page" id="dashboard-page">
      <div className="dashboard-top-bar fade-in">
        <div className="page-header" style={{ marginBottom: 0 }}>
          <h1 className="page-title">Financial Dashboard</h1>
          <p className="page-subtitle">{analysis?.filename || `File #${fileId}`}</p>
        </div>
        <button className="btn btn-primary" id="export-btn" onClick={handleExport}>
          📥 Export Excel
        </button>
      </div>

      <div className="dashboard-grid">
        {/* Ratio Cards */}
        <RatioCards ratios={analysis?.ratios} trend={analysis?.trend} />

        {/* Charts */}
        <Charts data={analysis?.data} />

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
    </div>
  );
}
