export default function Legend() {
  const categories = [
    { name: 'Outcome', shape: 'circle' },
    { name: 'Result', shape: 'triangle' },
    { name: 'Driver', shape: 'square' },
    { name: 'Activity', shape: 'diamond' },
    { name: 'Indicator', shape: 'hexagon' },
  ];

  const levels = [
    { name: 'Child', color: '#FC4C02' },
    { name: 'Class', color: '#007f79' },
    { name: 'School/Community', color: '#7e5aa6' },
    { name: 'System', color: '#F6B0BD' },
    { name: 'Macro', color: '#8dd3b5' },
    { name: 'None', color: '#999999' },
  ];

  return (
    <div className="legend">
      <div className="legend-section">
        <h3 className="legend-title">Shapes</h3>
        <div className="legend-items">
          {categories.map((cat) => (
            <div key={cat.name} className="legend-item">
              <div
                className={`legend-dot shape-${cat.shape}`}
                style={{ backgroundColor: '#cbd5e1' }}
              />
              <span className="legend-label">{cat.name}</span>
            </div>
          ))}
        </div>
      </div>
      
      <div className="legend-section">
        <h3 className="legend-title">Levels</h3>
        <div className="legend-items">
          {levels.map((lvl) => (
            <div key={lvl.name} className="legend-item">
              <div
                className="legend-dot shape-circle"
                style={{ backgroundColor: lvl.color }}
              />
              <span className="legend-label">{lvl.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
