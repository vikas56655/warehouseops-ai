'use client';
import { useEffect, useState } from 'react';
type Metric = { name: string; value: number; unit: string; provenance: string };
const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export default function Home() {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [error, setError] = useState('');
  useEffect(() => {
    fetch(`${url}/api/v1/metrics`).then(r => { if (!r.ok) throw new Error(`API ${r.status}`); return r.json(); })
      .then(setMetrics).catch(() => setError('API unavailable. Start the backend and refresh.'));
  }, []);
  return <main className="shell">
    <aside className="sidebar"><div className="brand">◈ WAREHOUSE<span>OPS</span></div><p className="muted">AI Operations Platform</p><nav><div className="active">▦ &nbsp; Control Tower</div><div>◷ &nbsp; Forecasting <small>Coming soon</small></div><div>◇ &nbsp; Anomalies <small>Coming soon</small></div><div>◎ &nbsp; AI Analyst <small>Coming soon</small></div></nav><div className="sidebarfoot">v0.1.0 · Week 1 foundation</div></aside>
    <section className="content"><header><div><p className="eyebrow">WAREHOUSE INTELLIGENCE / OVERVIEW</p><h1>Operations Control Tower</h1><p className="muted">Monitor operational signals and prepare for intelligent decisions.</p></div><span className="pill">● SYNTHETIC DEMO</span></header>
    <div className="notice">All metrics on this page are illustrative synthetic demo values, not real warehouse observations.</div>
    {error && <div className="error" role="alert">{error}</div>}
    <div className="cards">{metrics.length ? metrics.map(m => <article className="card" key={m.name}><p className="muted">{m.name}</p><strong>{m.value.toLocaleString('en-US')}{m.unit === 'percent' ? '%' : ''}</strong><p className="sub">{m.unit} · {m.provenance}</p></article>) : <p className="muted">Loading metrics…</p>}</div>
    <div className="panels"><article className="panel"><p className="eyebrow">SYSTEM STATUS</p><h2>Foundation online</h2><p className="muted">The API provides typed, provenance-labeled demonstration metrics. Real ingestion, agents, forecasting and optimization will be added in later phases.</p><div className="tags"><span>FastAPI</span><span>Next.js</span><span>PostgreSQL</span><span>Docker</span></div></article><article className="panel"><p className="eyebrow">DEVELOPMENT ROADMAP</p><h2>Next milestone</h2><p className="muted">Week 2: validated ingestion of public retail data and canonical warehouse schemas.</p><a href={`${url}/docs`} target="_blank" rel="noreferrer">Explore API documentation ↗</a></article></div>
    </section>
  </main>;
}
