import React, { useState, useEffect, useRef } from 'react'

const NOTICE = 'INVESTIGATIVE LEAD — NOT PROOF. LeakTrace suggests which centre\'s printed copy a photo came from. It does not show who leaked it, and a retyped paper carries no fingerprint.'

function Prepare() {
  const [paper, setPaper] = useState(null), [centres, setCentres] = useState(null)
  const [key, setKey] = useState(''), [lang, setLang] = useState('en'), [delta, setDelta] = useState(0.30), [eps, setEps] = useState(0.30)
  const [job, setJob] = useState(null), [status, setStatus] = useState(null), [err, setErr] = useState('')
  const timer = useRef(null)
  useEffect(() => () => clearInterval(timer.current), [])
  async function start() {
    setErr(''); setStatus(null)
    const fd = new FormData(); fd.append('paper', paper); fd.append('centres', centres); fd.append('key', key); fd.append('lang', lang); fd.append('delta', delta); fd.append('eps', eps)
    const r = await fetch('/api/prepare', { method: 'POST', body: fd })
    if (!r.ok) { setErr((await r.json()).detail || 'failed'); return }
    const j = await r.json(); setJob(j.case_id)
    timer.current = setInterval(async () => {
      const s = await (await fetch('/api/prepare/' + j.case_id)).json(); setStatus(s)
      if (s.state !== 'running') clearInterval(timer.current)
    }, 1500)
  }
  const pct = status ? Math.round(100 * status.done / Math.max(1, status.total)) : 0
  return (<div>
    <h2>Paper preparation</h2>
    <p className="mut">Upload the master paper and the centre list, enter the secret key, and get one fingerprinted PDF per centre. Keep the key private: it is needed again to investigate, and it is never stored by this server.</p>
    <label>Master paper (.json with title / instructions / questions, or .txt with blank-line separated paragraphs)</label><input type="file" accept=".json,.txt" onChange={e => setPaper(e.target.files[0])} />
    <label>Centre list (.csv / .txt, one centre id per line, up to 5000)</label><input type="file" accept=".csv,.txt" onChange={e => setCentres(e.target.files[0])} />
    <label>Secret key (at least 12 characters)</label><input type="password" value={key} onChange={e => setKey(e.target.value)} />
    <div className="row"><div><label>Language</label><select value={lang} onChange={e => setLang(e.target.value)}><option value="en">English</option><option value="hi">Hindi (Devanagari)</option></select></div>
      <div><label>Word-gap offset δ (pt)</label><input type="number" step="0.05" min="0.05" max="1.5" value={delta} onChange={e => setDelta(e.target.value)} /></div>
      <div><label>Line offset ε (pt)</label><input type="number" step="0.05" min="0.05" max="1.5" value={eps} onChange={e => setEps(e.target.value)} /></div></div>
    <p className="mut">Larger offsets survive worse photos but are more likely to be noticed. The default is provisional until the reader study (experiment E1) has been run with your volunteers.</p>
    <button className="go" disabled={!paper || !centres || key.length < 12} onClick={start}>Generate fingerprinted copies</button>
    {err && <p className="err">{String(err)}</p>}
    {job && <div className="card"><b>Case {job}</b> — keep this id for the investigation.
      <div className="bar" style={{ marginTop: 8 }}><div style={{ width: pct + '%' }} /></div><div className="mut">{status ? `${status.done} / ${status.total} copies (${status.state})` : 'starting…'}</div>
      {status && status.state === 'done' && <p><a href={`/api/prepare/${job}/zip`}>Download ZIP of per-centre PDFs</a></p>}
      {status && status.state === 'error' && <p className="err">{status.error}</p>}</div>}
  </div>)
}

function Investigate() {
  const [cases, setCases] = useState([]), [caseId, setCaseId] = useState(''), [key, setKey] = useState(''), [photo, setPhoto] = useState(null)
  const [busy, setBusy] = useState(false), [out, setOut] = useState(null), [err, setErr] = useState('')
  useEffect(() => { fetch('/api/cases').then(r => r.json()).then(c => { setCases(c); if (c[0]) setCaseId(c[0].case_id) }).catch(() => {}) }, [])
  async function run() {
    setBusy(true); setErr(''); setOut(null)
    const fd = new FormData(); fd.append('photo', photo); fd.append('case_id', caseId); fd.append('key', key)
    try { const r = await fetch('/api/decode', { method: 'POST', body: fd }); if (!r.ok) throw new Error((await r.json()).detail); setOut(await r.json()) } catch (e) { setErr(e.message) }
    setBusy(false)
  }
  const r = out && out.result
  return (<div>
    <h2>Investigation dashboard</h2>
    <label>Case</label><select value={caseId} onChange={e => setCaseId(e.target.value)}>{cases.map(c => <option key={c.case_id} value={c.case_id}>{c.case_id} — {c.title} ({c.n_centres} centres)</option>)}</select>
    <label>Secret key used for that case</label><input type="password" value={key} onChange={e => setKey(e.target.value)} />
    <label>Photo of the leaked paper (any crop; JPEG / PNG)</label><input type="file" accept="image/*" onChange={e => setPhoto(e.target.files[0])} />
    <button className="go" disabled={!photo || !caseId || !key || busy} onClick={run}>{busy ? 'Analysing… (10–30 s)' : 'Analyse photo'}</button>
    {err && <p className="err">{err}</p>}
    {r && <div className="card">
      {r.accept ? <><span className="badge ok">FINGERPRINT FOUND</span> <b style={{ fontSize: 20, marginLeft: 8 }}>Most probable source: {r.best_centre}</b></>
        : <><span className="badge no">REJECTED — no valid fingerprint</span> <p>{r.reason}. Nothing should be inferred about any centre from this photo.</p></>}
      {r.ranking && r.ranking.length > 0 && <>
        <p className="mut">Confidence {(100 * (r.confidence || 0)).toFixed(4)}% (1 − family-wise p) · p = {r.p_best?.toExponential(2)} · best-vs-wrong-key z = {r.z_best?.toFixed(1)} · margin to runner-up = {r.margin_z?.toFixed(1)} σ · positions used: {r.n_gaps} word gaps + {r.n_lines} lines</p>
        <table><thead><tr><th>#</th><th>Centre</th><th>Score T(c)</th><th></th></tr></thead><tbody>
          {r.ranking.map(([c, t], i) => <tr key={c}><td>{i + 1}</td><td>{c}</td><td>{t.toFixed(3)}</td><td><div className="bar" style={{ width: 160 }}><div style={{ width: Math.max(0, Math.min(1, t)) * 100 + '%' }} /></div></td></tr>)}</tbody></table>
        {r.accept && r.candidate_centres && r.candidate_centres.length > 1 && <p><b>Several centres score significantly ({r.candidate_centres.join(', ')}).</b> This pattern is what a collusion of copies, or a mixed copy, looks like: treat them all as the candidate set.</p>}</>}
      {out.overlay && <><h4>Decoded spacing changes on the photo</h4><img className="ov" src={out.overlay} alt="overlay" /></>}
    </div>}
    <p className="notice" style={{ marginTop: 16 }}>{NOTICE}</p>
  </div>)
}

export default function App() {
  const [tab, setTab] = useState('prep')
  return (<><div className="top"><h1>LeakTrace</h1><span style={{ opacity: .7 }}>exam-paper leak attribution · SDG 4</span></div>
    <div className="notice">{NOTICE}</div>
    <div className="tabs"><button className={tab === 'prep' ? 'on' : ''} onClick={() => setTab('prep')}>Paper preparation</button><button className={tab === 'inv' ? 'on' : ''} onClick={() => setTab('inv')}>Investigation</button></div>
    <main>{tab === 'prep' ? <Prepare /> : <Investigate />}</main></>)
}
