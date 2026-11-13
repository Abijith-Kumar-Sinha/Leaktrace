"""Visual overlay of the decoded spacing changes drawn on the leaked photo."""
import numpy as np, cv2

NOTICE = "INVESTIGATIVE LEAD - NOT PROOF"

def draw_overlay(img, dbg, bank, centre_index, delta, eps, max_side=1800):
    """Boxes are placed on the PHOTO using the estimated homography.
    green = measured displacement agrees with the top candidate's key, red = disagrees, grey = too poor to use / not shifted."""
    g = img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    out = g.copy()
    Hinv = np.linalg.inv(dbg["H"]); pg = dbg["page"]
    words = dbg["words"]
    n_ok = n_bad = 0
    S = bank.S_gap[centre_index]
    # predicted per-word dx for the candidate: cumulative sum of gap signs inside each line
    pred = {}
    for gidx, (p, ln, k) in enumerate(bank.gap_ids):
        pass
    by_line = {}
    for j, (p, ln, k) in enumerate(bank.gap_ids):
        if p == pg: by_line.setdefault(ln, []).append(S[j])
    wl = {}
    for i, w in enumerate(words): wl.setdefault(w["line"], []).append(i)
    for ln, idxs in wl.items():
        sg = np.array(by_line.get(ln, []), float)
        cum = np.concatenate([[0.0], np.cumsum(sg)]) if len(sg) else np.zeros(len(idxs))
        for k, i in enumerate(idxs):
            pred[i] = cum[k] if k < len(cum) else 0.0
    for i, w in enumerate(words):
        q = dbg["q"][i]
        pts = np.float32([[w["x0"], w["y0"]], [w["x1"], w["y0"]], [w["x1"], w["y1"]], [w["x0"], w["y1"]]])
        ph = cv2.perspectiveTransform(pts[None], Hinv)[0].astype(np.int32)
        if q <= 0.05:
            continue
        if pred.get(i, 0) == 0:
            col = (170, 170, 170)
        else:
            agree = np.sign(pred[i]) * dbg["dx"][i] > 0.25 * delta
            col = (60, 170, 60) if agree else (50, 50, 210)
            n_ok += int(agree); n_bad += int(not agree)
        cv2.polylines(out, [ph.reshape(-1, 1, 2)], True, col, 2, cv2.LINE_AA)
    dbg["agree"], dbg["disagree"] = n_ok, n_bad   # surfaced by the API next to the overlay
    h, w = out.shape[:2]
    f = min(1.0, max_side / max(h, w))
    if f < 1: out = cv2.resize(out, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    bar = np.full((34, out.shape[1], 3), (30, 30, 30), np.uint8)
    cv2.putText(bar, f"{NOTICE}  |  green: shift agrees with top candidate ({n_ok})  red: disagrees ({n_bad})", (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return np.vstack([bar, out])
