from __future__ import annotations
import os, hashlib, json, time
import numpy as np, cv2
from common.config import RASTER_SCALE as S, DEFAULT_ALPHA, N_NULL
from common.keys import SignBank
from embed.typeset import render, rasterise
from decode import locate, measure, score

_LANG = {"en": "eng", "hi": "hin+eng"}

class Decoder:
    def __init__(self, layout, master_pages, key, centre_ids, delta, eps, n_null=N_NULL, alpha=DEFAULT_ALPHA,
                 w_line=1.0, cache_dir="outputs/cache"):
        self.layout, self.master_pages = layout, master_pages
        self.key, self.delta, self.eps, self.alpha, self.w_line = key, delta, eps, alpha, w_line
        self.bank = SignBank(key, layout, centre_ids)
        h = hashlib.sha1((str(key) + str(len(layout["words"])) + str(n_null)).encode()).hexdigest()[:12]
        os.makedirs(cache_dir, exist_ok=True)
        p = os.path.join(cache_dir, f"null_{h}.npz")
        if os.path.exists(p):
            z = np.load(p); self.null = _NB(z["g"], z["l"])
        else:
            nb = SignBank(key, layout, [f"__null__{i}" for i in range(n_null)])
            np.savez_compressed(p, g=nb.S_gap, l=nb.S_line); self.null = _NB(nb.S_gap, nb.S_line)
        self.marked_gap = self.bank.S_gap[0] != 0 if len(centre_ids) else None

    # ------------------------------------------------------------------
    def decode(self, img, use_gap=True, use_line=True, debug=False, lang=None, localiser="ocr", ocr_scales=(1.5,), deskew=False):
        t0 = time.time()
        L = self.layout
        g = locate.to_gray(img)
        norm = locate.flatten_illumination(g)
        res = dict(accept=False, reason=None, ranking=[], timing={})
        if deskew:                                   # v2: undo large in-plane rotation before OCR
            ang = locate.estimate_skew(norm)
            res["skew_deg"] = ang
            if abs(ang) > 2.0:
                norm = locate.rotate_expand(norm, ang)
        lang = lang or _LANG[L.get("lang", "en")]
        best_all = (0, [], [], 0, norm)           # (n_pairs, ocr, pairs, rotation k, image)
        for k in (0, 1, 3, 2):                    # upright first; 90 / 270 / 180 degree rotations only if upright found (almost) nothing
            im_k = norm if k == 0 else np.ascontiguousarray(np.rot90(norm, k))
            for sc in (ocr_scales if k == 0 else ocr_scales[:1]):   # v2: retry OCR at larger scales for small / blurred text
                ocr_ = locate.ocr_words(im_k, lang, upscale=sc)
                pairs_ = locate.match_to_master(ocr_, L)
                if len(pairs_) > best_all[0]: best_all = (len(pairs_), ocr_, pairs_, k, im_k)
                if len(pairs_) >= 12: break
            if best_all[0] >= 6:
                break
        _, ocr, pairs, k_, norm = best_all
        rot = 90 * k_
        res["timing"]["ocr"] = time.time() - t0
        res["rotated_by"] = rot
        if len(pairs) < 4:
            res["reason"] = "alignment_failed: too few text anchors matched the master"; return res
        pages = np.bincount([L["words"][m]["page"] for _, m in pairs]); pg = int(pages.argmax())
        pairs = [(o, m) for o, m in pairs if L["words"][m]["page"] == pg]
        H, ninl, inl = locate.estimate_H(ocr, pairs, L)
        res.update(page=pg, n_anchors=len(pairs), n_inliers=ninl)
        if H is None or ninl < 5:
            res["reason"] = "alignment_failed: no consistent geometry"; return res
        words = [w for w in L["words"] if w["page"] == pg]
        wid = {w["id"]: i for i, w in enumerate(words)}
        master = self.master_pages[pg]
        poly = measure.visible_polygon(norm.shape, H)
        blur = None
        for it in range(2):
            dx, dy, rho, ok, blur = measure.measure_words(norm, H, master, words, poly, blur_sigma=blur)
            nv = int((ok & (rho > 0.4)).sum())
            if nv < 6:
                res["reason"] = "alignment_failed: too few measurable words"; return res
            xy = np.array([[(w["x0"] + w["x1"]) / 2, (w["y0"] + w["y1"]) / 2] for w in words])
            wt = np.where(ok, np.clip((rho - 0.3) / 0.6, 0, 1), 0.0)
            order = 1 if nv >= 25 else 0
            cx, A = measure.fit_trend(xy, dx, wt, order); cy, _ = measure.fit_trend(xy, dy, wt, order)
            if it == 0:   # fold the affine part back into the image->page map and measure again
                vx, vy = A @ cx, A @ cy
                if order == 1:
                    M = np.array([[1 - cx[1] / 100, -cx[2] / 100, -cx[0]], [-cy[1] / 100, 1 - cy[2] / 100, -cy[0]], [0, 0, 1]])
                else:
                    M = np.array([[1, 0, -cx[0]], [0, 1, -cy[0]], [0, 0, 1]])
                H = M @ H
                poly = measure.visible_polygon(norm.shape, H)
        order = 2 if nv >= 160 else (1 if nv >= 25 else 0)
        cx, A = measure.fit_trend(xy, dx, wt, order); cy, _ = measure.fit_trend(xy, dy, wt, order)
        dx_r, dy_r = dx - A @ cx, dy - A @ cy
        q_w = np.where(ok & (np.abs(dx_r) < 2.0) & (np.abs(dy_r) < 2.0), np.clip((rho - 0.3) / 0.6, 0, 1), 0.0)
        # ---- per-position measurements -------------------------------------------------
        G, Lc = len(self.bank.gap_ids), len(self.bank.line_ids)
        r_gap = np.zeros(G); q_gap = np.zeros(G); r_line = np.zeros(Lc); q_line = np.zeros(Lc)
        for ln in L["pages"][pg]["lines"]:
            ids = [wid[i] for i in ln["words"]]
            for k in range(len(ids) - 1):
                j = self.bank.gap_index[(pg, ln["id"], k)]
                if not self.marked_gap[j]:
                    continue
                a, b = ids[k], ids[k + 1]
                qq = np.sqrt(q_w[a] * q_w[b])
                if qq > 0:
                    r_gap[j] = np.clip((dx_r[b] - dx_r[a]) / self.delta, -2, 2); q_gap[j] = qq
            qs = q_w[ids]
            if qs.sum() > 0:
                lj = self.bank.line_index[(pg, ln["id"])]
                r_line[lj] = np.clip(np.sum(qs * dy_r[ids]) / qs.sum() / self.eps, -2, 2)
                q_line[lj] = min(1.0, qs.sum() / 4.0) * float(self.bank.S_line[0, lj] != 0)
        T, den = score.scores(self.bank, r_gap, q_gap, r_line, q_line, self.w_line, use_gap, use_line)
        T0, _ = score.scores(self.null, r_gap, q_gap, r_line, q_line, self.w_line, use_gap, use_line)
        dec = score.decide(T, T0, self.alpha, min_den=6.0, den=den)
        ids = self.bank.centre_ids
        order_ = np.argsort(-T)[:5]
        res.update(dec); res["best_centre"] = ids[dec["best"]]
        res["ranking"] = [(ids[i], float(T[i])) for i in order_]
        res["candidate_centres"] = [ids[i] for i in dec["candidates"]]
        res["confidence"] = float(max(0.0, 1.0 - dec["p_best"]))
        res["n_gaps"], res["n_lines"] = int((q_gap > 0).sum()), int((q_line > 0).sum())
        res["blur_sigma_px"] = blur
        if not dec["accept"]:
            res["reason"] = "rejected: no statistically valid fingerprint (best score indistinguishable from wrong keys)"
        res["timing"]["total"] = time.time() - t0
        if debug:
            res["_debug"] = dict(H=H, words=words, dx=dx_r, dy=dy_r, q=q_w, norm=norm, T=T, T0=T0,
                                 r_gap=r_gap, q_gap=q_gap, r_line=r_line, q_line=q_line, page=pg)
        return res

class _NB:
    def __init__(self, g, l):
        self.S_gap, self.S_line = g, l
        self.centre_ids = list(range(len(g)))

def build_master(paper, max_questions=None):
    pdf, layout = render(paper, None, max_questions)
    return pdf, layout, rasterise(pdf)
