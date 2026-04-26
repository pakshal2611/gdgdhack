export default function AnomalyPanel({ anomalies }) {
  if (!anomalies || anomalies.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">✅</div>
        <p>No anomalies detected. Financial data looks consistent.</p>
      </div>
    );
  }

  const getSeverityBadge = (severity) => {
    const severityMap = {
      'high': { emoji: '🔴', label: 'High' },
      'medium': { emoji: '🟡', label: 'Medium' },
      'low': { emoji: '🟢', label: 'Low' }
    };
    return severityMap[severity] || { emoji: '⚪', label: 'Unknown' };
  };

  const capitalizeField = (field) => {
    return field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ');
  };

  const formatDeviation = (deviation) => {
    if (deviation > 0) {
      return <span className="anomaly-deviation pos">+{deviation.toFixed(1)}%</span>;
    } else if (deviation < 0) {
      return <span className="anomaly-deviation neg">{deviation.toFixed(1)}%</span>;
    }
    return <span className="anomaly-deviation">0%</span>;
  };

  return (
    <div className="card anomaly-card">
      <div className="card-header">
        <span className="card-title">⚠️ Anomaly Report</span>
        <span className="anomaly-count">{anomalies.length} issues found</span>
      </div>
      <div className="anomaly-list">
        {anomalies.map((anomaly, i) => {
          const severity = getSeverityBadge(anomaly.severity);
          return (
            <div key={i} className="anomaly-row">
              <div className={`severity-badge severity-${anomaly.severity}`}>
                {severity.emoji} {severity.label}
              </div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>{anomaly.year}</div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                {capitalizeField(anomaly.field)}
              </div>
              <div>{formatDeviation(anomaly.deviation_pct)}</div>
              <div className="anomaly-description">{anomaly.description}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
