// Backend base URL: empty in dev (Vite proxies /api); the GitHub Pages build sets VITE_API_BASE to the Render service.
export const API = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '')

export async function api(path, opts) {
  const r = await fetch(API + path, opts)
  if (!r.ok) {
    let msg = `HTTP ${r.status}`
    try { msg = (await r.json()).detail || msg } catch { /* non-JSON error page, e.g. a sleeping Space */ }
    const e = new Error(msg); e.status = r.status; throw e
  }
  return r.json()
}
