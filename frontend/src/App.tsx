import './App.css'

const features = [
  { label: 'Crop health', value: '94%' },
  { label: 'Prediction accuracy', value: '97.2%' },
  { label: 'Soil insights', value: '24/7' },
]

function App() {
  return (
    <main className="app-shell">
      <div className="hero-panel">
        <span className="badge">Smart farming dashboard</span>
        <h1>AgriVision AI</h1>
        <p>
          AI-powered crop monitoring, disease detection, and sustainable farm planning
          for better yields.
        </p>

        <div className="cta-row">
          <button type="button">View dashboard</button>
          <button type="button" className="secondary">
            Analyze crop
          </button>
        </div>

        <div className="stats-grid" aria-label="Project metrics">
          {features.map((item) => (
            <div key={item.label} className="stat-card">
              <strong>{item.value}</strong>
              <span>{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}

export default App
