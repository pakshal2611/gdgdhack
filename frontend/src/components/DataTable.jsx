export default function DataTable({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📊</div>
        <p>No financial data available</p>
      </div>
    );
  }

  const formatNum = (n) => {
    if (n === null || n === undefined) return '—';
    return Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  return (
    <div className="data-table-wrap">
      <table className="data-table" id="financial-data-table">
        <thead>
          <tr>
            <th>Year</th>
            <th>Revenue</th>
            <th>Profit</th>
            <th>Margin</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => {
            const margin = row.revenue > 0 ? ((row.profit / row.revenue) * 100).toFixed(1) : '0.0';
            return (
              <tr key={i} className="fade-in" style={{ animationDelay: `${i * 0.05}s` }}>
                <td>{row.year}</td>
                <td className="num">${formatNum(row.revenue)}</td>
                <td className="num">${formatNum(row.profit)}</td>
                <td className="num">{margin}%</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
