export default function RatioCards({ ratios, trend }) {
  const formatValue = (value, type) => {
    if (value === undefined || value === null || value === 0) return 'N/A';
    if (type === 'ratio') return `${value.toFixed(2)} x`;
    return `${value.toFixed(2)}%`;
  };

  const getTrendIndicator = (value) => {
    if (value === undefined || value === null || value === 0) return '—';
    if (value > 0) return '↑';
    if (value < 0) return '↓';
    return '—';
  };

  const getTrendColor = (value) => {
    if (value > 0) return 'green';
    if (value < 0) return 'red';
    return 'gray';
  };

  const cards = [
    {
      emoji: '📈',
      label: 'Revenue Growth',
      value: ratios?.revenue_growth,
      type: 'percentage',
      subtitle: 'Year-over-year revenue change'
    },
    {
      emoji: '💰',
      label: 'Profit Margin',
      value: ratios?.profit_margin,
      type: 'percentage',
      subtitle: 'Profit as % of revenue'
    },
    {
      emoji: '📊',
      label: 'EBITDA Margin',
      value: ratios?.ebitda_margin,
      type: 'percentage',
      subtitle: 'EBITDA as % of revenue'
    },
    {
      emoji: '⚖️',
      label: 'Debt / Equity',
      value: ratios?.debt_equity,
      type: 'ratio',
      subtitle: 'Financial leverage ratio'
    },
    {
      emoji: '💧',
      label: 'Current Ratio',
      value: ratios?.current_ratio,
      type: 'ratio',
      subtitle: 'Short-term liquidity measure'
    },
    {
      emoji: '🚀',
      label: '5-Yr CAGR',
      value: ratios?.cagr_5yr,
      type: 'percentage',
      subtitle: 'Compound annual growth rate'
    },
  ];

  const trendStatus = {
    'Growing': { emoji: '📈', color: '#10b981' },
    'Declining': { emoji: '📉', color: '#ef4444' },
    'Stable': { emoji: '➡️', color: '#f59e0b' },
  };

  const trendInfo = trendStatus[trend] || { emoji: '❓', color: '#555577' };

  return (
    <div className="ratio-grid" id="ratio-cards">
      {cards.map((card, i) => {
        const displayValue = formatValue(card.value, card.type);
        const trendIndicator = getTrendIndicator(card.value);
        const trendColor = getTrendColor(card.value);

        return (
          <div key={i} className="ratio-card fade-in" style={{ animationDelay: `${i * 0.05}s` }}>
            <div className="ratio-icon">{card.emoji}</div>
            <div style={{ fontSize: '0.85rem', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
              {card.label}
            </div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
                {displayValue}
              </div>
              <div className="trend-indicator" style={{ color: trendColor === 'green' ? '#10b981' : trendColor === 'red' ? '#ef4444' : '#555577' }}>
                {trendIndicator}
              </div>
            </div>
            <div className="ratio-subtitle">{card.subtitle}</div>
          </div>
        );
      })}
      
      {/* Overall Trend Card */}
      <div className="ratio-card fade-in" style={{ animationDelay: `${cards.length * 0.05}s`, background: `rgba(${trendInfo.color === '#10b981' ? '16, 185, 129' : trendInfo.color === '#ef4444' ? '239, 68, 68' : '245, 158, 11'}, 0.1)` }}>
        <div className="ratio-icon">{trendInfo.emoji}</div>
        <div style={{ fontSize: '0.85rem', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
          Overall Trend
        </div>
        <div style={{ fontSize: '1.5rem', fontWeight: 700, color: trendInfo.color }}>
          {trend || 'N/A'}
        </div>
        <div className="ratio-subtitle">Financial momentum indicator</div>
      </div>
    </div>
  );
}
