import React, { useEffect, useMemo, useRef, useState } from 'react'
import { FilePlus2, ScanSearch, FolderOpen, ArrowRight, Maximize2, ShieldCheck, ScrollText, Search, Check, CircleAlert,
  ImageUp, KeyRound, Download, RotateCcw, Loader2, X, Menu } from 'lucide-react'
import { STR } from './i18n.js'
import { api, API } from './api.js'
import { SAMPLE_ACCEPT, SAMPLE_REJECT } from './fixture.js'

/* ---------- small hooks ---------- */
function useHashRoute() {
  const read = () => {
    const [path, q] = (window.location.hash.slice(1) || '/investigate').split('?')
    return { path, query: new URLSearchParams(q || '') }
  }
  const [r, setR] = useState(read)
  useEffect(() => { const f = () => setR(read()); window.addEventListener('hashchange', f); return () => window.removeEventListener('hashchange', f) }, [])
  return r
}
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v) } catch { return d } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)) } catch { /* private mode */ } },
}
function useAudit() {
  const [log, setLog] = useState(() => { try { return JSON.parse(sessionStorage.getItem('lt-audit') || '[]') } catch { return [] } })
  const add = e => setLog(l => { const n = [{ ...e, t: Date.now() }, ...l].slice(0, 100); try { sessionStorage.setItem('lt-audit', JSON.stringify(n)) } catch {} return n })
  return [log, add]
}

/* ---------- formatting ---------- */
function Sci({ p }) {
  if (p == null) return '—'
  if (p >= 0.995) return <>&gt;0.99</>
  if (p >= 1e-3) return <>{p.toPrecision(2)}</>
  const e = Math.floor(Math.log10(p)), m = p / 10 ** e
  return <>{m.toFixed(m < 9.95 ? (m === Math.round(m) ? 0 : 1) : 0)}<span className="x">×</span>10<sup>{e}</sup></>
}

/* ---------- brand ---------- */
// peacock feather: a fan of separate barbs splaying from the quill to a frayed, pointed tip; gold-rimmed eye on top
const BARBS = Array.from({ length: 23 }, (_, k) => {
  const f = (130 + k * (280 / 22)) * Math.PI / 180, fray = k % 2 ? 1.6 : 0
  const top = Math.max(0, -Math.sin(f)) ** 6 * 3            // pull the crown into a point
  const x = 20 + (17.5 + fray) * Math.cos(f), y = 23 + (20 + fray + top) * Math.sin(f)
  return `M20 47Q${(20 + (x - 20) * 0.35).toFixed(1)} ${(35 + (y - 35) * 0.45).toFixed(1)} ${x.toFixed(1)} ${y.toFixed(1)}`
})
function Monogram() {
  return (<svg className="mono" viewBox="0 -2 40 58" aria-hidden="true">
    <defs>
      <linearGradient id="barb" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stopColor="#0E7C70" /><stop offset=".6" stopColor="#22BE93" /><stop offset="1" stopColor="#6FE3B6" /></linearGradient>
      <radialGradient id="rim" cx="50%" cy="48%" r="52%"><stop offset=".62" stopColor="#1BB596" /><stop offset=".8" stopColor="#F0B64C" /><stop offset="1" stopColor="#B87A2F" /></radialGradient>
    </defs>
    <g stroke="url(#barb)" strokeWidth="1.35" strokeLinecap="round" fill="none">{BARBS.map((d, k) => <path key={k} d={d} />)}</g>
    <ellipse cx="20" cy="21" rx="9.6" ry="11.4" fill="url(#rim)" />
    <ellipse cx="20" cy="20.6" rx="6.6" ry="8" fill="#12A58C" />
    <ellipse cx="20" cy="20.2" rx="4.7" ry="5.8" fill="#1E7DCB" />
    <ellipse cx="20" cy="19.8" rx="2.8" ry="3.6" fill="#0A2A62" />
    <path d="M20 44C20.4 48 20.6 51.5 20.4 55.5" stroke="#E9B04A" strokeWidth="1.8" fill="none" strokeLinecap="round" />
  </svg>)
}

/* ---------- shell ---------- */
const NAV = [
  { group: 'ops', items: [['prepare', FilePlus2], ['investigate', Search], ['cases', FolderOpen]] },
  { group: 'gov', items: [['keys', ShieldCheck], ['audit', ScrollText]] },
]
const ROUTE_KEY = { prepare: 'prepare', investigate: 'investigate', cases: 'cases', keys: 'keys', audit: 'audit' }

function Sidebar({ t, path, open, onClose }) {
  return (<aside className={'side' + (open ? ' open' : '')} aria-label="Main">
    <a className="brand" href="#/investigate" onClick={onClose}><Monogram /><span>{t.brand}</span></a>
    <button className="side-x" onClick={onClose} aria-label="Close menu"><X size={20} /></button>
    {NAV.map(g => (<nav key={g.group} className="navg">
      <h2>{t[g.group]}</h2>
      {g.items.map(([k, Icon]) => (
        <a key={k} href={'#/' + k} onClick={onClose} className={'navi' + (path === '/' + k ? ' on' : '')} aria-current={path === '/' + k ? 'page' : undefined}>
          <Icon size={21} strokeWidth={1.7} /><span>{t[ROUTE_KEY[k]]}</span></a>))}
    </nav>))}
    <footer className="side-foot"><span>{t.build}</span><span>{t.tagline}</span></footer>
  </aside>)
}

function Topbar({ t, lang, setLang, crumbs, onMenu }) {
  const [q, setQ] = useState('')
  return (<header className="top">
    <button className="menu" onClick={onMenu} aria-label="Open menu"><Menu size={22} /></button>
    <ol className="crumbs">{crumbs.map((c, i) => <li key={i}>{c}</li>)}</ol>
    <form className="search" role="search" onSubmit={e => { e.preventDefault(); window.location.hash = '#/cases?q=' + encodeURIComponent(q) }}>
      <Search size={18} strokeWidth={1.8} /><input value={q} onChange={e => setQ(e.target.value)} placeholder={t.search} aria-label={t.search} />
    </form>
    <div className="lang" role="group" aria-label="Language">
      <button className={lang === 'en' ? 'on' : ''} onClick={() => setLang('en')} lang="en">EN</button><i />
      <button className={lang === 'hi' ? 'on' : ''} onClick={() => setLang('hi')} lang="hi">हिन्दी</button>
    </div>
    <svg className="avatar" viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="14.2" fill="none" stroke="currentColor" strokeWidth="1.6" /><circle cx="16" cy="12.6" r="4.6" fill="currentColor" /><path d="M7.6 24.4c1.3-4 4.6-6 8.4-6s7.1 2 8.4 6c-2.2 2.1-5.1 3.3-8.4 3.3s-6.2-1.2-8.4-3.3z" fill="currentColor" /></svg>
  </header>)
}

function Notice({ t }) {
  return <p className="notice" role="note"><CircleAlert size={19} strokeWidth={2} /><span>{t.notice}</span></p>
}

function ServerBanner({ t, state, retry }) {
  if (state === 'ok' || state === 'checking') return null
  return (<div className={'srv ' + state} role="status">
    {state === 'waking' ? <Loader2 className="spin" size={18} /> : <CircleAlert size={18} />}
    <span>{state === 'waking' ? t.waking : t.offline}</span>
    {state === 'down' && <button onClick={retry}><RotateCcw size={15} />{t.retry}</button>}
  </div>)
}

/* ---------- investigate ---------- */
function Histogram({ t, hist, rows, zAlpha }) {
  const best = rows[0]
  const zMax = Math.max(10, Math.ceil((best?.z ?? 0) + 1))
  const W = 620, H = 302, L = 62, R = 18, T = 30, B = 52
  const x = z => L + (z + 5) / (zMax + 5) * (W - L - R)
  const cmax = Math.max(...hist.counts, 1)
  const yTop = Math.pow(10, Math.ceil(Math.log10(cmax))) / (cmax < Math.pow(10, Math.ceil(Math.log10(cmax))) / 2 ? 2 : 1)
  const y = c => H - B - c / yTop * (H - B - T)
  const ticks = [-4, -2, 0, 2, 4, 6, 8, 10, 12, 14, 16, 18].filter(v => v <= zMax)
  const bw = (x(hist.edges[1]) - x(hist.edges[0])) - 1.6
  return (<svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${t.dist}: ${t.wrongKeys(hist.n)}, ${best?.centre} at z ${best?.z.toFixed(1)}`}>
    <defs>
      <linearGradient id="nullg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#B7A6FF" /><stop offset="1" stopColor="#6F5FD0" /></linearGradient>
      <linearGradient id="hitg" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stopColor="#14C79A" /><stop offset=".55" stopColor="#7BD36A" /><stop offset="1" stopColor="#FFB547" /></linearGradient>
    </defs>
    {[0, .25, .5, .75, 1].map(f => <g key={f}><line x1={L} x2={W - R} y1={y(yTop * f)} y2={y(yTop * f)} className="grid" />
      <text x={L - 10} y={y(yTop * f) + 4} className="tick" textAnchor="end">{Math.round(yTop * f).toLocaleString()}</text></g>)}
    {hist.counts.map((c, i) => c > 0 && <rect key={i} x={x(hist.edges[i]) + .8} width={bw} y={y(c)} height={H - B - y(c)} rx="1.5" fill="url(#nullg)" />)}
    <line x1={x(zAlpha)} x2={x(zAlpha)} y1={T - 8} y2={H - B} className="thr" />
    <text x={x(zAlpha) + 7} y={T + 4} className="thr-l">z = {zAlpha.toFixed(1)}</text>
    {best && <g className="hit"><rect x={x(Math.min(best.z, zMax)) - 9} width="18" y={T + 10} height={H - B - T - 10} rx="2" fill={best.z >= zAlpha ? 'url(#hitg)' : '#58707C'} />
      <text x={x(Math.min(best.z, zMax))} y={T + 2} className="hit-l" textAnchor="middle">{best.centre}</text></g>}
    <line x1={L} x2={W - R} y1={H - B} y2={H - B} className="axis" />
    {ticks.map(v => <text key={v} x={x(v)} y={H - B + 22} className="tick" textAnchor="middle">{v}</text>)}
    <text x={(L + W - R) / 2} y={H - 6} className="ax-l" textAnchor="middle">{t.zAxis}</text>
    <text x={16} y={(T + H - B) / 2} className="ax-l ax-y" textAnchor="middle" transform={`rotate(-90 16 ${(T + H - B) / 2})`}>{t.count}</text>
  </svg>)
}

function Result({ t, out, caseMeta, onNew }) {
  const r = out.result, rows = r.ranking_stats || []
  const accept = r.accept
  const zScale = Math.max(10, Math.ceil((r.z_best ?? 0) + 1))
  const total = (r.agree ?? 0) + (r.disagree ?? 0)
  return (<>
    <div className="kpis">
      <div className={'kpi verdict ' + (accept ? 'yes' : 'no')}>
        <span className="vicon">{accept ? <Check size={30} strokeWidth={3} /> : <X size={30} strokeWidth={3} />}</span>
        <div><strong>{accept ? t.found : t.rejected}</strong><span>{accept ? t.foundSub : (r.reason ? r.reason : t.rejectedSub)}</span></div>
      </div>
      <div className="kpi src"><span className="kl">{t.source}</span><span className="kv">{accept ? r.best_centre : '—'}</span></div>
      <div className="kpi pv"><span className="kl">{t.pval}</span><span className="kv"><Sci p={r.p_best} /></span></div>
      <div className="kpi stat"><span className="kl">{t.zmargin}</span><span className="kv">{r.z_best != null ? r.z_best.toFixed(1) : '—'} <em>·</em> {r.margin_z != null ? r.margin_z.toFixed(1) + 'σ' : '—'}</span></div>
    </div>
    <div className="duo">
      <section className="panel ev">
        <h2>{t.evidence}</h2>
        {out.overlay ? <a className="evimg" href={out.overlay} target="_blank" rel="noopener" title={t.enlarge}><img src={out.overlay} alt={t.evidence} /><span className="zoom"><Maximize2 size={16} /></span></a>
          : <div className="ph msg"><CircleAlert size={22} /><span>{t.noOverlay}</span></div>}
        {r.n_gaps > 0 && <p className="cap">{t.agreeCap(r.agree ?? 0, total, r.n_gaps, r.n_lines)}</p>}
      </section>
      <section className="panel dist">
        <div className="ph2"><h2>{t.dist}</h2>{r.null_hist && <span className="sub">{t.wrongKeys(r.null_hist.n)}</span>}</div>
        {r.null_hist ? <Histogram t={t} hist={r.null_hist} rows={rows} zAlpha={r.z_alpha ?? 4.4} /> : <div className="ph" />}
      </section>
    </div>
    {rows.length > 0 && <section className="panel rank">
      <div className="ph2"><h2>{t.ranked}</h2><span className="sub">{t.showing(rows.length, r.n_centres ?? caseMeta?.n_centres ?? '—')}</span></div>
      <table><thead><tr><th className="rk">{t.rank}</th><th>{t.centre}</th><th>{t.score}</th><th className="barc" /><th>{t.pval}</th><th>{t.status}</th></tr></thead>
        <tbody>{rows.map((row, i) => { const sig = accept && row.z >= (r.z_alpha ?? 4.4); return (<tr key={row.centre} className={sig ? 'sig' : ''}>
          <td className="rk">{i + 1}</td><td className="code">{row.centre}</td><td className="num">{row.z.toFixed(1)}</td>
          <td className="barc"><span className={'bar' + (sig ? '' : ' below')}><i style={{ width: Math.max(1.5, Math.min(100, Math.max(0, row.z) / zScale * 100)) + '%' }} /><b style={{ left: (r.z_alpha ?? 4.4) / zScale * 100 + '%' }} /></span></td>
          <td className="num"><Sci p={row.p} /></td><td><span className={'pill ' + (sig ? 'gold' : '')} aria-label={sig ? t.significant : t.below}><span className="full">{sig ? t.significant : t.below}</span><span className="short" aria-hidden="true">{sig ? t.sigShort : t.belowShort}</span></span></td></tr>) })}</tbody></table>
      {accept && r.candidate_centres?.length > 1 && <p className="coll">{t.collusion(r.candidate_centres.join(', '))}</p>}
    </section>}
    <div className="again"><button className="btn ghost" onClick={onNew}><RotateCcw size={17} />{t.newInv}</button></div>
  </>)
}

function FileDrop({ id, label, hint, accept, file, onFile, icon: Icon, cta }) {
  const [drag, setDrag] = useState(false)
  return (<label htmlFor={id} className={'drop' + (drag ? ' drag' : '') + (file ? ' has' : '')}
    onDragOver={e => { e.preventDefault(); setDrag(true) }} onDragLeave={() => setDrag(false)}
    onDrop={e => { e.preventDefault(); setDrag(false); if (e.dataTransfer.files[0]) onFile(e.dataTransfer.files[0]) }}>
    <Icon size={26} strokeWidth={1.5} />
    <span className="dl">{label}</span>
    <span className="dh">{file ? file.name : hint}</span>
    <span className="btn small">{cta}</span>
    <input id={id} type="file" accept={accept} onChange={e => e.target.files[0] && onFile(e.target.files[0])} />
  </label>)
}

function Investigate({ t, query, addAudit, cases, refreshCases }) {
  const [caseId, setCaseId] = useState(query.get('case') || '')
  const [key, setKey] = useState(''), [photo, setPhoto] = useState(null)
  const [busy, setBusy] = useState(false), [err, setErr] = useState(''), [out, setOut] = useState(null)
  const fixture = import.meta.env.DEV && query.get('fixture')
  useEffect(() => { if (!caseId && cases[0]) setCaseId(cases[0].case_id) }, [cases])
  const shown = fixture === 'accept' ? SAMPLE_ACCEPT : fixture === 'reject' ? SAMPLE_REJECT : out
  const meta = cases.find(c => c.case_id === caseId) || (fixture ? { case_id: 'LT-7F3A', n_centres: 200, lang: 'en' } : null)
  async function run(e) {
    e.preventDefault(); setBusy(true); setErr(''); setOut(null)
    const fd = new FormData(); fd.append('photo', photo); fd.append('case_id', caseId); fd.append('key', key)
    try { const o = await api('/api/decode', { method: 'POST', body: fd }); setOut(o); addAudit({ type: 'decode', case: caseId, accept: o.result.accept, centre: o.result.best_centre }) }
    catch (x) { setErr(x.message) }
    setBusy(false)
  }
  return (<>
    <div className="head">
      <h1>{t.invTitle}{meta && <span className="cid"><span className="dot">·</span>{meta.case_id}</span>}</h1>
      {meta && <div className="chips"><span>{t.centres(meta.n_centres)}</span><span>{meta.lang === 'hi' ? t.hindi : t.english}</span></div>}
      <Notice t={t} />
    </div>
    {shown ? <Result t={t} out={shown} caseMeta={meta} onNew={() => { setOut(null); if (fixture) window.location.hash = '#/investigate' }} /> :
      <form className="panel form" onSubmit={run}>
        <p className="lede">{t.invIntro}</p>
        {cases.length === 0 ? <p className="empty"><FolderOpen size={20} />{t.noCases} <a className="go" href="#/prepare">{t.prepare}<ArrowRight size={16} strokeWidth={1.8} /></a></p> : <>
          <div className="fields">
            <label className="field"><span>{t.caseL}</span>
              <select value={caseId} onChange={e => setCaseId(e.target.value)}>{cases.map(c => <option key={c.case_id} value={c.case_id}>{c.case_id} — {c.title} ({t.centres(c.n_centres)})</option>)}</select></label>
            <label className="field"><span>{t.keyL}</span>
              <span className="inp"><KeyRound size={18} /><input type="password" autoComplete="off" value={key} onChange={e => setKey(e.target.value)} /></span></label>
          </div>
          <FileDrop id="photo" label={t.photoL} hint={t.photoHint} accept="image/*" file={photo} onFile={setPhoto} icon={ImageUp} cta={t.choose} />
          {err && <p className="err" role="alert"><CircleAlert size={18} />{err}</p>}
          <button className="btn primary" disabled={!photo || !caseId || !key || busy}>{busy ? <><Loader2 className="spin" size={18} />{t.analysing}</> : <><Search size={18} />{t.analyse}</>}</button>
        </>}
      </form>}
  </>)
}

/* ---------- prepare ---------- */
function Prepare({ t, addAudit, refreshCases }) {
  const [paper, setPaper] = useState(null), [centres, setCentres] = useState(null), [key, setKey] = useState('')
  const [lang, setLang] = useState('en'), [delta, setDelta] = useState(0.30), [eps, setEps] = useState(0.30)
  const [job, setJob] = useState(null), [tok, setTok] = useState(''), [st, setSt] = useState(null), [err, setErr] = useState('')
  const timer = useRef(null)
  useEffect(() => () => clearInterval(timer.current), [])
  async function start(e) {
    e.preventDefault(); setErr(''); setSt(null)
    const fd = new FormData(); fd.append('paper', paper); fd.append('centres', centres); fd.append('key', key); fd.append('lang', lang); fd.append('delta', delta); fd.append('eps', eps)
    try {
      const j = await api('/api/prepare', { method: 'POST', body: fd }); setJob(j.case_id); setTok(j.token || '')
      timer.current = setInterval(async () => {
        try { const s = await api('/api/prepare/' + j.case_id); setSt(s)
          if (s.state !== 'running') { clearInterval(timer.current); if (s.state === 'done') { addAudit({ type: 'prepare', case: j.case_id, n: s.total }); refreshCases() } } }
        catch (x) { clearInterval(timer.current); setErr(x.message) }
      }, 1500)
    } catch (x) { setErr(x.message) }
  }
  const pct = st ? Math.round(100 * st.done / Math.max(1, st.total)) : 0
  return (<>
    <div className="head"><h1>{t.prepTitle}</h1><Notice t={t} /></div>
    <form className="panel form" onSubmit={start}>
      <p className="lede">{t.prepIntro}</p>
      <p className="samples"><span>{t.samples}</span>{[['mock-paper-english.json', t.sEn], ['mock-paper-hindi.json', t.sHi], ['centres-200.txt', t.sCentres]].map(([f, l]) =>
        <a key={f} href={import.meta.env.BASE_URL + 'samples/' + f} download><Download size={15} />{l}</a>)}</p>
      <div className="fields two">
        <FileDrop id="paper" label={t.paperL} hint={t.paperHint} accept=".json,.txt" file={paper} onFile={setPaper} icon={FilePlus2} cta={t.choose.replace(/photo|फ़ोटो/, 'file')} />
        <FileDrop id="centres" label={t.centresL} hint={t.centresHint} accept=".csv,.txt" file={centres} onFile={setCentres} icon={FolderOpen} cta={t.choose.replace(/photo|फ़ोटो/, 'file')} />
      </div>
      <div className="fields four">
        <label className="field wide"><span>{t.keyL}</span><span className="inp"><KeyRound size={18} /><input type="password" autoComplete="new-password" value={key} onChange={e => setKey(e.target.value)} /></span><small className={key && key.length < 12 ? 'warn' : ''}>{t.keyHint}</small></label>
        <label className="field"><span>{t.langL}</span><select value={lang} onChange={e => setLang(e.target.value)}><option value="en">{t.english}</option><option value="hi">{t.hindi}</option></select></label>
        <label className="field"><span>{t.deltaL}</span><input type="number" step="0.05" min="0.05" max="1.5" value={delta} onChange={e => setDelta(e.target.value)} /></label>
        <label className="field"><span>{t.epsL}</span><input type="number" step="0.05" min="0.05" max="1.5" value={eps} onChange={e => setEps(e.target.value)} /></label>
      </div>
      <p className="hint">{t.offsetHint}</p>
      {err && <p className="err" role="alert"><CircleAlert size={18} />{err}</p>}
      <button className="btn primary" disabled={!paper || !centres || key.length < 12 || (job && st?.state === 'running')}><FilePlus2 size={18} />{t.generate}</button>
      {job && <div className="job" role="status">
        <div className="jh"><strong>{t.caseId} {job}</strong><span>{t.keepId}</span></div>
        <span className="bar big"><i style={{ width: pct + '%' }} /></span>
        <span className="jc">{st ? t.copies(st.done, st.total) : t.starting}</span>
        {st?.state === 'done' && <a className="btn primary" href={`${API}/api/prepare/${job}/zip?token=${encodeURIComponent(tok)}`}><Download size={18} />{t.download}</a>}
        {st?.state === 'error' && <p className="err"><CircleAlert size={18} />{st.error}</p>}
      </div>}
    </form>
  </>)
}

/* ---------- cases / keys / audit ---------- */
function Cases({ t, cases, query }) {
  const q = (query.get('q') || '').toLowerCase()
  const list = cases.filter(c => !q || (c.case_id + ' ' + c.title).toLowerCase().includes(q))
  return (<>
    <div className="head"><h1>{t.casesTitle}</h1><Notice t={t} /></div>
    <section className="panel rank">
      <p className="lede">{t.casesIntro}</p>
      {list.length === 0 ? <p className="empty"><FolderOpen size={20} />{t.noCases} <a className="go" href="#/prepare">{t.prepare}<ArrowRight size={16} strokeWidth={1.8} /></a></p> :
        <table><thead><tr><th>{t.colCase}</th><th>{t.colPaper}</th><th>{t.colLang}</th><th className="num">{t.colCentres}</th><th>{t.colCreated}</th><th /></tr></thead>
          <tbody>{list.map(c => <tr key={c.case_id}><td className="code">{c.case_id}</td><td>{c.title}</td><td>{c.lang === 'hi' ? t.hindi : t.english}</td><td className="num">{c.n_centres}</td>
            <td>{c.created ? new Date(c.created * 1000).toLocaleString() : '—'}</td><td><a className="btn small" href={`#/investigate?case=${c.case_id}`}><Search size={15} />{t.open}</a></td></tr>)}</tbody></table>}
    </section>
  </>)
}
function Keys({ t }) {
  return (<><div className="head"><h1>{t.keysTitle}</h1><Notice t={t} /></div>
    <section className="panel"><p className="lede">{t.keysIntro}</p><ol className="rules">{t.keysRules.map((x, i) => <li key={i}>{x}</li>)}</ol></section></>)
}
function Audit({ t, log }) {
  return (<><div className="head"><h1>{t.auditTitle}</h1><Notice t={t} /></div>
    <section className="panel rank"><p className="lede">{t.auditIntro}</p>
      {log.length === 0 ? <p className="empty"><ScrollText size={20} />{t.auditEmpty}</p> :
        <table><tbody>{log.map((e, i) => <tr key={i}><td className="num">{new Date(e.t).toLocaleTimeString()}</td>
          <td>{e.type === 'prepare' ? t.evPrepare : t.evDecode}</td><td className="code">{e.case}</td>
          <td>{e.type === 'prepare' ? t.centres(e.n) : e.accept ? <span className="pill gold">{e.centre}</span> : <span className="pill">{t.rejected}</span>}</td></tr>)}</tbody></table>}
    </section></>)
}

/* ---------- app ---------- */
export default function App() {
  const { path, query } = useHashRoute()
  const [lang, setLangS] = useState(() => { const q = new URLSearchParams(window.location.hash.split('?')[1] || '').get('lang'); return q === 'hi' || q === 'en' ? q : store.get('lt-lang', 'en') })
  const setLang = l => { setLangS(l); store.set('lt-lang', l) }
  useEffect(() => { document.documentElement.lang = lang }, [lang])
  const t = STR[lang]
  const [menu, setMenu] = useState(false)
  const [log, addAudit] = useAudit()
  const [cases, setCases] = useState([]), [srv, setSrv] = useState('checking')
  async function refreshCases() {
    const slow = setTimeout(() => setSrv(s => s === 'checking' ? 'waking' : s), 2500)
    try { setCases(await api('/api/cases')); setSrv('ok') } catch { setSrv('down') } finally { clearTimeout(slow) }
  }
  useEffect(() => { refreshCases() }, [])
  const page = path.replace('/', '') || 'investigate'
  const crumbs = useMemo(() => [t[ROUTE_KEY[page]] || t.investigate, ...(query.get('case') ? [query.get('case')] : query.get('fixture') ? ['LT-7F3A'] : [])], [page, query, t])
  return (<div className="app">
    <Sidebar t={t} path={'/' + page} open={menu} onClose={() => setMenu(false)} />
    <div className="main">
      <Topbar t={t} lang={lang} setLang={setLang} crumbs={crumbs} onMenu={() => setMenu(true)} />
      <main className="content" lang={lang}>
        {!(import.meta.env.DEV && query.get('fixture')) && <ServerBanner t={t} state={srv} retry={refreshCases} />}
        {page === 'prepare' ? <Prepare t={t} addAudit={addAudit} refreshCases={refreshCases} /> :
          page === 'cases' ? <Cases t={t} cases={cases} query={query} /> :
            page === 'keys' ? <Keys t={t} /> :
              page === 'audit' ? <Audit t={t} log={log} /> :
                <Investigate t={t} query={query} addAudit={addAudit} cases={cases} refreshCases={refreshCases} />}
      </main>
    </div>
  </div>)
}
