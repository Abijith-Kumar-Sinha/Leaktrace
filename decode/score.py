"""Scoring, null distribution, p-values, accept/reject, collusion candidate set."""
from __future__ import annotations
import numpy as np
from scipy.stats import norm

def scores(bank, r_gap, q_gap, r_line, q_line, w_line=1.0, use_gap=True, use_line=True):
    """T(c) = sum_j q_j s_j(c) r_j / sum_j q_j  over visible marked positions (both channels)."""
    num = np.zeros(len(bank.centre_ids), np.float64); den = 0.0
    if use_gap:
        ig = np.nonzero(q_gap > 0)[0]
        if len(ig):
            num += bank.S_gap[:, ig].astype(np.float32) @ (q_gap[ig] * r_gap[ig]).astype(np.float32)
            den += q_gap[ig].sum()
    if use_line:
        il = np.nonzero(q_line > 0)[0]
        if len(il):
            num += w_line * (bank.S_line[:, il].astype(np.float32) @ (q_line[il] * r_line[il]).astype(np.float32))
            den += w_line * q_line[il].sum()
    return (num / den if den > 0 else num), den

def p_values(T, T0):
    """Per-centre p under the wrong-key null: empirical when resolvable, Gaussian-tail extrapolation beyond."""
    mu, sd = float(T0.mean()), float(T0.std() + 1e-12)
    z = (T - mu) / sd
    p_g = norm.sf(z)
    cnt = (T0[None, :] >= T[:, None]).sum(1)
    p_e = (1 + cnt) / (len(T0) + 1)
    return np.where(cnt >= 5, p_e, p_g), z, sd

def decide(T, T0, alpha, min_den=0.0, den=0.0):
    N = len(T)
    p, z, sd = p_values(T, T0)
    order = np.argsort(-T)
    b = int(order[0]); s = int(order[1]) if N > 1 else b
    p_best = float(min(1.0, N * p[b]))
    accept = bool(p_best < alpha and den >= min_den)
    z_alpha = float(norm.isf(alpha / N))
    cands = [int(i) for i in order[:6] if z[i] >= z_alpha]
    return dict(best=b, second=s, T_best=float(T[b]), T_second=float(T[s]), z_best=float(z[b]),
                margin_z=float((T[b] - T[s]) / sd), p_best=p_best, accept=accept,
                sigma_null=sd, candidates=cands, z_alpha=z_alpha)
