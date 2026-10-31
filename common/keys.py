"""Keyed sign generation.

seed(c)  = HMAC-SHA256(k, "centre:" + id)                       (32 bytes)
bits     = HMAC-SHA256(seed(c), tag|page|index)                 (256 bits per call)

Gap channel : the gaps of one line are grouped in consecutive PAIRS (0,1),(2,3)...;
              pair p gets signs (+s,-s) with s taken from a keyed bit.  A pair therefore
              displaces exactly one word by +-delta and leaves the line width unchanged
              (justified margins preserved, no cumulative drift).  An odd last gap is unmarked (0).
Line channel: lines of a page are grouped in consecutive pairs; pair p gets (+s,-s).
              Neighbouring lines move in opposite directions so a global vertical
              shift of a photo cannot masquerade as a fingerprint.  An odd last line is unmarked.
"""
from __future__ import annotations
import hmac, hashlib
import numpy as np

def centre_seed(key: str | bytes, centre_id: str) -> bytes:
    k = key.encode() if isinstance(key, str) else key
    return hmac.new(k, b"centre:" + centre_id.encode(), hashlib.sha256).digest()

def _bits(seed: bytes, tag: str, page: int, idx: int) -> np.ndarray:
    d = hmac.new(seed, f"{tag}|{page}|{idx}".encode(), hashlib.sha256).digest()
    return np.unpackbits(np.frombuffer(d, dtype=np.uint8))  # 256 bits

def gap_signs(seed: bytes, page: int, line: int, n_gaps: int) -> np.ndarray:
    """Signs in {+1,-1,0} for the n_gaps gaps of one line."""
    out = np.zeros(n_gaps, dtype=np.int8)
    if n_gaps < 2:
        return out
    bits = _bits(seed, "G", page, line)
    for p in range(n_gaps // 2):
        s = 1 if bits[p % 256] else -1
        out[2 * p], out[2 * p + 1] = s, -s
    return out

def line_signs(seed: bytes, page: int, n_lines: int) -> np.ndarray:
    out = np.zeros(n_lines, dtype=np.int8)
    for p in range(n_lines // 2):
        bits = _bits(seed, "L", page, p // 256)
        s = 1 if bits[p % 256] else -1
        out[2 * p], out[2 * p + 1] = s, -s
    return out

class SignBank:
    """Dense sign matrices for many centres over one master layout.

    gap_ids[j]  = (page, line, k)   gap between word k and k+1 of that line
    line_ids[l] = (page, line)
    S_gap  : (N, G) int8     S_line : (N, L) int8
    """
    def __init__(self, key, layout: dict, centre_ids: list[str]):
        self.key, self.centre_ids = key, list(centre_ids)
        self.gap_ids, self.line_ids = [], []
        for pg in layout["pages"]:
            for ln in pg["lines"]:
                n = len(ln["words"])
                self.gap_ids += [(pg["index"], ln["id"], k) for k in range(n - 1)]
            self.line_ids += [(pg["index"], ln["id"]) for ln in pg["lines"]]
        self.gap_index = {g: i for i, g in enumerate(self.gap_ids)}
        self.line_index = {l: i for i, l in enumerate(self.line_ids)}
        N, G, L = len(self.centre_ids), len(self.gap_ids), len(self.line_ids)
        self.S_gap = np.zeros((N, G), dtype=np.int8)
        self.S_line = np.zeros((N, L), dtype=np.int8)
        per_page = {pg["index"]: [ln["id"] for ln in pg["lines"]] for pg in layout["pages"]}
        for ci, cid in enumerate(self.centre_ids):
            seed = centre_seed(key, cid)
            g = 0
            for pg in layout["pages"]:
                for ln in pg["lines"]:
                    m = len(ln["words"]) - 1
                    if m > 0:
                        self.S_gap[ci, g:g + m] = gap_signs(seed, pg["index"], ln["id"], m)
                    g += max(m, 0)
            l = 0
            for pi, lids in per_page.items():
                self.S_line[ci, l:l + len(lids)] = line_signs(seed, pi, len(lids))
                l += len(lids)

def word_offsets(layout: dict, bank: SignBank, ci: int, delta: float, eps: float):
    """Ground-truth per-word (dx, dy) in pt for centre index ci.  dx = delta*cumsum(gap signs)."""
    off = {}
    g0 = 0
    for pg in layout["pages"]:
        for ln in pg["lines"]:
            ws = ln["words"]; m = len(ws) - 1
            sg = bank.S_gap[ci, g0:g0 + max(m, 0)].astype(float)
            cum = np.concatenate([[0.0], np.cumsum(sg)]) * delta
            dy = float(bank.S_line[ci, bank.line_index[(pg["index"], ln["id"])]]) * eps
            for k, w in enumerate(ws):
                off[w] = (float(cum[k]), dy)
            g0 += max(m, 0)
    return off
