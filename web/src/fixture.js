// Dev-only sample results (#/investigate?fixture=accept|reject) used to design and screenshot the result states.
// SIMULATED: the overlay is the repo's decoder output on a simulated leaked photo (docs/figs/overlay_example.png).
import overlay from './assets/sample-overlay.jpg'

const erf = x => { const s = Math.sign(x); x = Math.abs(x); const t = 1 / (1 + 0.3275911 * x)
  return s * (1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x)) }
const Phi = z => 0.5 * (1 + erf(z / Math.SQRT2))
const edges = Array.from({ length: 41 }, (_, i) => -5 + i * 0.25)
const null_hist = { n: 4000, edges, counts: edges.slice(0, -1).map((e, i) => Math.round(4000 * (Phi(edges[i + 1]) - Phi(e)))) }

export const SAMPLE_ACCEPT = { overlay, result: {
  accept: true, best_centre: 'C0012', p_best: 2e-17, z_best: 9.0, margin_z: 8.6, z_alpha: 4.42, n_gaps: 302, n_lines: 28,
  agree: 77, disagree: 0, n_centres: 200, candidate_centres: ['C0012'], null_hist,
  ranking_stats: [{ centre: 'C0012', z: 9.0, p: 2e-17 }, { centre: 'C0345', z: 2.1, p: 1.8e-2 }, { centre: 'C0178', z: 1.9, p: 2.7e-2 },
    { centre: 'C0061', z: 1.6, p: 5.8e-2 }, { centre: 'C0284', z: 1.4, p: 1.6e-1 }] } }

export const SAMPLE_REJECT = { overlay: null, result: {
  accept: false, best_centre: 'C0091', p_best: 0.41, z_best: 2.7, margin_z: 0.3, z_alpha: 4.42, n_gaps: 0, n_lines: 0,
  agree: 0, disagree: 0, n_centres: 200, null_hist, reason: 'Best score indistinguishable from wrong keys',
  ranking_stats: [{ centre: 'C0091', z: 2.7, p: 0.41 }, { centre: 'C0133', z: 2.4, p: 0.88 }, { centre: 'C0007', z: 2.2, p: 1 }] } }
