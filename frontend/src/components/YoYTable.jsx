export default function YoYTable({ yoyData }) {
  if (!yoyData || yoyData.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <span className="card-title">📋 Year-over-Year Analysis</span>
        </div>
        <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          No year-over-year data available.
        </div>
      </div>
    );
  }

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return '—';
    return `$${Number(value).toLocaleString()}`;
  };

  const formatGrowth = (value) => {
    if (value === null || value === undefined) return '—';
    if (value > 0) {
      return <span className="positive-val">+{value.toFixed(2)}%</span>;
    } else if (value < 0) {
      return <span className="negative-val">{value.toFixed(2)}%</span>;
    }
    return <span>0.00%</span>;
  };

  const formatMargin = (value) => {
    if (value === null || value === undefined) return '—';
    return `${value.toFixed(2)}%`;
  };

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">📋 Year-over-Year Analysis</span>
      </div>
      <div className="data-table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>Year</th>
              <th>Revenue</th>
              <th>Profit</th>
              <th>Rev Growth %</th>
              <th>Profit Growth %</th>
              <th>Profit Margin %</th>
            </tr>
          </thead>
          <tbody>
            {yoyData.map((row, i) => (
              <tr key={i}>
                <td className="num">{row.year}</td>
                <td className="num">{formatCurrency(row.revenue)}</td>
                <td className="num">{formatCurrency(row.profit)}</td>
                <td className="num">{formatGrowth(row.revenue_growth_pct)}</td>
                <td className="num">{formatGrowth(row.profit_growth_pct)}</td>
                <td className="num">{formatMargin(row.profit_margin_pct)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
