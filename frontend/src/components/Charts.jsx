import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  ComposedChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload || !payload.length) return null;
  return (
    <div style={{
      background: 'rgba(17,17,39,0.95)', border: '1px solid rgba(99,102,241,0.3)',
      borderRadius: '10px', padding: '12px 16px', backdropFilter: 'blur(10px)',
    }}>
      <p style={{ color: '#8888aa', fontSize: '0.8rem', marginBottom: '4px' }}>{label}</p>
      {payload.map((p, i) => {
        let displayValue = p.value;
        if (typeof p.value === 'number') {
          if (p.name && p.name.includes('%')) {
            displayValue = p.value.toFixed(2);
          } else if (p.value > 100) {
            displayValue = `$${Number(p.value).toLocaleString()}`;
          }
        }
        return (
          <p key={i} style={{ color: p.color, fontWeight: 600, fontSize: '0.95rem' }}>
            {p.name}: {displayValue}
          </p>
        );
      })}
    </div>
  );
};

const ChartCard = ({ title, children }) => (
  <div className="card chart-card fade-in">
    <div className="card-header">
      <span className="card-title">{title}</span>
    </div>
    {children}
  </div>
);

export default function Charts({ data, yoyData }) {
  if (!data || data.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📊</div>
        <p>No data available</p>
      </div>
    );
  }

  // Prepare data with profit margin for chart 4
  const dataWithMargin = data.map(d => ({
    ...d,
    profit_margin_pct: d.revenue > 0 ? ((d.profit / d.revenue) * 100) : 0
  }));

  return (
    <div className="charts-grid">
      {/* Chart 1: Revenue Trend */}
      <ChartCard title="📈 Revenue Trend">
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
            <defs>
              <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="year" stroke="#555577" fontSize={12} />
            <YAxis stroke="#555577" fontSize={12} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
            <Tooltip content={<CustomTooltip />} />
            <Area type="monotone" dataKey="revenue" stroke="#6366f1" fill="url(#revGrad)" strokeWidth={2.5} name="Revenue" />
          </AreaChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Chart 2: Profit Trend */}
      <ChartCard title="💰 Profit Trend">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="year" stroke="#555577" fontSize={12} />
            <YAxis stroke="#555577" fontSize={12} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
            <Tooltip content={<CustomTooltip />} />
            <Line type="monotone" dataKey="profit" stroke="#10b981" strokeWidth={2.5} name="Profit" dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Chart 3: Revenue vs Profit Comparison */}
      <ChartCard title="📊 Revenue vs Profit (YoY)">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="year" stroke="#555577" fontSize={12} />
            <YAxis stroke="#555577" fontSize={12} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="revenue" fill="#6366f1" name="Revenue" />
            <Bar dataKey="profit" fill="#10b981" name="Profit" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Chart 4: Revenue with Profit Margin % */}
      <ChartCard title="📉 Revenue with Profit Margin %">
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={dataWithMargin} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="year" stroke="#555577" fontSize={12} />
            <YAxis stroke="#555577" fontSize={12} yAxisId="left" tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
            <YAxis stroke="#555577" fontSize={12} yAxisId="right" orientation="right" tickFormatter={(v) => `${v.toFixed(0)}%`} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="revenue" fill="#6366f1" opacity={0.7} name="Revenue" yAxisId="left" />
            <Line type="monotone" dataKey="profit_margin_pct" stroke="#f59e0b" strokeWidth={2.5} name="Profit Margin %" yAxisId="right" />
          </ComposedChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}
