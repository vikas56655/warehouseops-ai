'use client';
import { useEffect, useRef, useState } from 'react';

type Scenario = { season: 'summer' | 'winter'; seed: number; shift_minutes: number; arrivals_per_hour: number; pickers: number; receivers: number; dispatchers: number };
type Zone = { zone: string; completed: number; utilization: number; peak_queue: number; total_wait_minutes_for_started: number };
type Result = { provenance: string; scenario: Scenario; arrived: number; completed: number; backlog: number; units_dispatched: number; colis_dispatched: number; mean_completed_cycle_minutes: number | null; zones: Zone[] };
type Operation = { zone: string; provenance: string; events: number; units: number; colis: number; units_per_hour: number };
const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const defaults: Scenario = {season:'winter', seed:42, shift_minutes:480, arrivals_per_hour:30, pickers:5, receivers:2, dispatchers:2};
const fields: {key: Exclude<keyof Scenario,'season'>; label: string; min: number; max: number}[] = [
  {key:'pickers',label:'Picking staff',min:1,max:100},{key:'receivers',label:'Reception staff',min:1,max:100},
  {key:'dispatchers',label:'Dispatch staff',min:1,max:100},{key:'arrivals_per_hour',label:'Orders / hour',min:1,max:300},
  {key:'shift_minutes',label:'Shift minutes',min:60,max:1440},{key:'seed',label:'Random seed',min:0,max:999999}
];
async function get<T>(path: string, signal: AbortSignal): Promise<T> {
  const response = await fetch(url+path,{signal,cache:'no-store'});
  if (!response.ok) throw new Error('API returned '+response.status);
  return response.json() as Promise<T>;
}
function simulate(scenario: Scenario, signal: AbortSignal) {
  return get<Result>('/api/v1/simulation/run?'+new URLSearchParams(Object.entries(scenario).map(([k,v])=>[k,String(v)])),signal);
}
export default function Home() {
  const [scenario,setScenario]=useState<Scenario>(defaults);
  const [result,setResult]=useState<Result|null>(null);
  const [comparison,setComparison]=useState<Result|null>(null);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState('');
  const [health,setHealth]=useState('Checking');
  const [ops,setOps]=useState<Operation[]>([]);
  const [opsStatus,setOpsStatus]=useState('Loading');
  const active=useRef<AbortController|null>(null);
  useEffect(()=>{
    const controller=new AbortController();
    get<{status:string}>('/health/live',controller.signal).then(()=>setHealth('Online')).catch(()=>{if(!controller.signal.aborted)setHealth('Unavailable')});
    get<{status:string;zones:Operation[]}>('/api/v1/operations/summary',controller.signal).then(data=>{
      setOps(data.zones);setOpsStatus(data.status==='not_initialized'?'Run database migration and import demo events.':data.zones.length?'Loaded':'No imported events yet.');
    }).catch(()=>{if(!controller.signal.aborted)setOpsStatus('Operations database unavailable.')});
    return ()=>{controller.abort();active.current?.abort()};
  },[]);
  async function run(compare:boolean) {
    active.current?.abort();
    const controller=new AbortController();active.current=controller;
    setBusy(true);setError('');setResult(null);setComparison(null);
    try {
      const current={...scenario};
      const runs=await Promise.all([simulate(current,controller.signal),compare?simulate({...current,season:current.season==='summer'?'winter':'summer'},controller.signal):Promise.resolve(null)]);
      if(!controller.signal.aborted){setResult(runs[0]);setComparison(runs[1]);setHealth('Online')}
    } catch(e) {if(!controller.signal.aborted)setError(e instanceof Error?e.message:'Simulation failed')}
    finally {if(!controller.signal.aborted)setBusy(false)}
  }
  const bottleneck=result?.zones.reduce((a,b)=>a.utilization>=b.utilization?a:b);
  return <main className="shell">
    <aside className="sidebar"><div className="brand">◈ Warehouse<span>Ops</span></div><p className="muted">Operations intelligence</p><nav><a href="#overview">Overview</a><a href="#simulation">Scenario lab</a><a href="#floor">Warehouse flow</a><a href="#records">Imported events</a></nav><div className="sidebarfoot">v0.4.0 · Control Tower</div></aside>
    <section className="content" id="overview"><header><div><p className="eyebrow">OPERATIONS INTELLIGENCE</p><h1>Warehouse Control Tower</h1><p className="muted">Explore resource constraints and seasonal workloads.</p></div><span className="pill">API: {health}</span></header>
    <div className="notice">Synthetic, uncalibrated simulation. Not live warehouse observations or employee performance.</div>
    <form className="panel" id="simulation" onSubmit={e=>{e.preventDefault();void run(false)}}>
      <p className="eyebrow">SCENARIO LAB</p><h2>Configure a shift</h2>
      <div className="controls"><label>Season<select value={scenario.season} onChange={e=>setScenario(s=>({...s,season:e.target.value as Scenario['season']}))}><option value="summer">Summer</option><option value="winter">Winter</option></select></label>
      {fields.map(f=><label key={f.key}>{f.label}<input type="number" required min={f.min} max={f.max} step="1" value={Number.isNaN(scenario[f.key])?'':scenario[f.key]} onChange={e=>setScenario(s=>({...s,[f.key]:e.target.valueAsNumber}))}/></label>)}</div>
      <div className="actions"><button type="submit" disabled={busy}>{busy?'Running…':'Run simulation'}</button><button type="submit" disabled={busy} className="secondary" onClick={e=>{if(e.currentTarget.form?.checkValidity()){e.preventDefault();void run(true)}}}>Compare seasons</button><button type="button" disabled={busy} className="secondary" onClick={()=>setScenario(defaults)}>Reset inputs</button></div>
      {error&&<p role="alert" className="error">{error}. Verify that the API is running and CORS is configured.</p>}
    </form>
    {result?<><p className="eyebrow">RESULT · {result.scenario.season.toUpperCase()} · SEED {result.scenario.seed}</p><div className="cards">
    {[['Orders arrived',result.arrived],['Completed',result.completed],['Backlog',result.backlog],['Cycle time (min)',result.mean_completed_cycle_minutes??'—'],['Units dispatched',result.units_dispatched],['Cartons dispatched',result.colis_dispatched]].map(([label,value])=><article className="card" key={label}><p className="muted">{label}</p><strong>{value}</strong></article>)}</div>
    <div className="panel" id="floor"><p className="eyebrow">WAREHOUSE FLOW · SCHEMATIC</p><h2>Resource utilisation and queues</h2><div className="flow">{result.zones.map(z=><article key={z.zone} className="zone" style={{background:z.utilization>=.9?'#fff0e7':z.utilization>=.7?'#fff7db':'#e9f5ee'}}><h3>{z.zone}</h3><strong>{(z.utilization*100).toFixed(1)}%</strong><div className="track"><div style={{width:(z.utilization*100)+'%',background:z.utilization>=.9?'#d44924':z.utilization>=.7?'#bd8611':'#25865b'}}/></div><p>Peak queue: {z.peak_queue}</p><p>Completed: {z.completed}</p></article>)}</div><p className="muted">Highest utilisation: {bottleneck?.zone}. This is a diagnostic signal, not proof of a bottleneck.</p></div>
    {comparison&&<div className="panel"><h2>Season comparison</h2><p className="muted">Same inputs and seed; independent random streams are not guaranteed by the current model. Single-run exploratory comparison.</p><table><thead><tr><th>Metric</th><th>{result.scenario.season}</th><th>{comparison.scenario.season}</th></tr></thead><tbody>{(['arrived','completed','backlog','colis_dispatched','mean_completed_cycle_minutes'] as const).map(k=><tr key={k}><td>{k.replaceAll('_',' ')}</td><td>{result[k]??'—'}</td><td>{comparison[k]??'—'}</td></tr>)}</tbody></table></div>}
    </>:<p className="muted" aria-live="polite">{busy?'Running simulation…':'Run a scenario to display backend results.'}</p>}
    <div className="panel" id="records"><p className="eyebrow">PERSISTED DATA</p><h2>Imported operational events</h2><p className="muted">{opsStatus}</p>{ops.length>0&&<div className="table-scroll"><table><thead><tr><th>Zone</th><th>Source</th><th>Events</th><th>Units</th><th>Cartons</th><th>Units / activity hour</th></tr></thead><tbody>{ops.map(o=><tr key={o.zone+o.provenance}><td>{o.zone}</td><td>{o.provenance}</td><td>{o.events}</td><td>{o.units}</td><td>{o.colis}</td><td>{o.units_per_hour}</td></tr>)}</tbody></table></div>}</div>
    <footer><a href={url+'/docs'} target="_blank" rel="noreferrer">API documentation ↗</a></footer></section></main>
}
