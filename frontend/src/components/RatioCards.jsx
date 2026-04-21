export default function RatioCards({ ratios, trend }) {
  const cards = [
    {
      label: 'Revenue Growth',
      value: `${ratios?.revenue_growth?.toFixed(2) || '0.00'}%`,
      trend: ratios?.revenue_growth > 0 ? 'positive' : ratios?.revenue_growth < 0 ? 'negative' : 'neutral',
      trendText: ratios?.revenue_growth > 0 ? '↑ Growing' : ratios?.revenue_growth < 0 ? '↓ Declining' : '→ Stable',
      icon: '📊',
    },
    {
      label: 'Profit Margin',
      value: `${ratios?.profit_margin?.toFixed(2) || '0.00'}%`,
      trend: ratios?.profit_margin > 15 ? 'positive' : ratios?.profit_margin > 5 ? 'neutral' : 'negative',
      trendText: ratios?.profit_margin > 15 ? 'Healthy' : ratios?.profit_margin > 5 ? 'Moderate' : 'Low',
      icon: '💹',
    },
    {
      label: 'Overall Trend',
      value: trend || 'N/A',
      trend: trend === 'Growing' ? 'positive' : trend === 'Declining' ? 'negative' : 'neutral',
      trendText: trend === 'Growing' ? '🚀 Positive outlook' : trend === 'Declining' ? '⚠️ Needs attention' : '→ Holding steady',
      icon: '📈',
    },
  ];

  return (
    <div className="ratio-grid" id="ratio-cards">
      {cards.map((card, i) => (
        <div key={i} className="ratio-card fade-in" style={{ animationDelay: `${i * 0.1}s` }}>
          <div className="label">{card.icon} {card.label}</div>
          <div className="value">{card.value}</div>
          <div className={`trend ${card.trend}`}>{card.trendText}</div>
        </div>
      ))}
    </div>
  );
}
