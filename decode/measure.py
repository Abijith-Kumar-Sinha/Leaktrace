"""Sub-pixel measurement of per-word displacement against the master (non-blind decoding)."""
from __future__ import annotations
import numpy as np, cv2
from common.config import RASTER_SCALE as S

def _rectify(img, H_img2pt, roi_pt):
    x0, y0, x1, y1 = roi_pt
    M = np.array([[1, 0, -x0 * S], [0, 1, -y0 * S], [0, 0, 1]]) @ np.diag([S, S, 1.0]) @ H_img2pt
    W, Hh = int(np.ceil((x1 - x0) * S)), int(np.ceil((y1 - y0) * S))
    return cv2.warpPerspective(img, M, (W, Hh), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=0)

def visible_polygon(shape, H_img2pt, inset=3):
    h, w = shape[:2]
    pts = np.float32([[inset, inset], [w - inset, inset], [w - inset, h - inset], [inset, h - inset]])
    return cv2.perspectiveTransform(pts[None], H_img2pt)[0]

def _ecc_shift(photo, master, crit):
    """Shift d (px) such that photo(x) ~= master(x - d).  Returns (dx, dy, rho)."""
    warp = np.eye(2, 3, dtype=np.float32)
    try:
        rho, warp = cv2.findTransformECC(photo, master, warp, cv2.MOTION_TRANSLATION, crit, None, 1)
    except cv2.error:
        return 0.0, 0.0, 0.0
    # findTransformECC: photo(x) = master(x + t)  ->  photo is master shifted by -t
    return -float(warp[0, 2]), -float(warp[1, 2]), float(rho)

def measure_words(img_norm, H, master_page, words, polygon, margin_pt=0.9, blur_sigma=None, crit=None, max_words=None):
    """words: master word dicts on this page.  Returns arrays dx,dy (pt), rho, ok mask, per word."""
    crit = crit or (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 40, 1e-5)
    poly = polygon.astype(np.float32).reshape(-1, 1, 2)
    sel = []
    for i, w in enumerate(words):
        corners = [(w["x0"], w["y0"]), (w["x1"], w["y0"]), (w["x1"], w["y1"]), (w["x0"], w["y1"])]
        if all(cv2.pointPolygonTest(poly, (float(cx), float(cy)), False) > 0 for cx, cy in corners):
            sel.append(i)
    n = len(words)
    dx = np.zeros(n); dy = np.zeros(n); rho = np.zeros(n); ok = np.zeros(n, bool)
    if not sel:
        return dx, dy, rho, ok, blur_sigma
    xs0 = min(words[i]["x0"] for i in sel) - 4; xs1 = max(words[i]["x1"] for i in sel) + 4
    ys0 = min(words[i]["y0"] for i in sel) - 4; ys1 = max(words[i]["y1"] for i in sel) + 4
    roi = (max(xs0, 0), max(ys0, 0), xs1, ys1)
    rect = _rectify(img_norm, H, roi).astype(np.float32)
    m_roi = master_page[int(roi[1] * S):int(roi[1] * S) + rect.shape[0], int(roi[0] * S):int(roi[0] * S) + rect.shape[1]].astype(np.float32)
    if m_roi.shape != rect.shape:
        rect = rect[:m_roi.shape[0], :m_roi.shape[1]]
    ox, oy = int(roi[0] * S), int(roi[1] * S)
    # estimate blur that best matches the photo's sharpness (once, on a sample of words)
    if blur_sigma is None:
        sample = sel[:: max(1, len(sel) // 24)][:24]
        best = (-1, 1.0)
        for sg in (0.8, 1.6, 2.4, 3.2, 4.5, 6.0):
            mb = cv2.GaussianBlur(m_roi, (0, 0), sg)
            r = []
            for i in sample:
                w = words[i]
                a, b, c, d = [int(round(v)) for v in ((w["x0"] - margin_pt) * S - ox, (w["y0"] - 1.2) * S - oy, (w["x1"] + margin_pt) * S - ox, (w["y1"] + 1.2) * S - oy)]
                if a < 0 or b < 0 or c > rect.shape[1] or d > rect.shape[0]:
                    continue
                _, _, rr = _ecc_shift(_n(rect[b:d, a:c]), _n(mb[b:d, a:c]), crit)
                r.append(rr)
            if r and np.mean(r) > best[0]:
                best = (np.mean(r), sg)
        blur_sigma = best[1]
    mb = cv2.GaussianBlur(m_roi, (0, 0), blur_sigma)
    rb = cv2.GaussianBlur(rect, (0, 0), 0.8)
    for i in sel:
        w = words[i]
        a, b, c, d = [int(round(v)) for v in ((w["x0"] - margin_pt) * S - ox, (w["y0"] - 1.2) * S - oy, (w["x1"] + margin_pt) * S - ox, (w["y1"] + 1.2) * S - oy)]
        if a < 0 or b < 0 or c > rect.shape[1] or d > rect.shape[0] or c - a < 12:
            continue
        sx, sy, r = _ecc_shift(_n(rb[b:d, a:c]), _n(mb[b:d, a:c]), crit)
        dx[i], dy[i], rho[i] = sx / S, sy / S, r
        ok[i] = r > 0.2
    return dx, dy, rho, ok, blur_sigma

def _n(p):
    p = p.astype(np.float32)
    return (p - p.mean()) / (p.std() + 1e-3)

def fit_trend(xy, d, w, order):
    """Weighted robust polynomial fit of a residual field.  order 0: constant, 1: affine, 2: quadratic."""
    x, y = xy[:, 0] / 100.0, xy[:, 1] / 100.0
    cols = [np.ones_like(x)]
    if order >= 1: cols += [x, y]
    if order >= 2: cols += [x * x, x * y, y * y]
    A = np.stack(cols, 1)
    wt = w.copy()
    coef = np.zeros(A.shape[1])
    for _ in range(4):
        Aw = A * wt[:, None]
        coef, *_ = np.linalg.lstsq(Aw.T @ A + 1e-6 * np.eye(A.shape[1]), Aw.T @ d, rcond=None)
        res = d - A @ coef
        s = 1.4826 * np.median(np.abs(res[wt > 0])) + 1e-6
        wt = w * np.clip(1 - (res / (4.685 * s)) ** 2, 0, 1) ** 2
    return coef, A
