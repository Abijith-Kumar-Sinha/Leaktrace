"""Pre-processing, OCR word localisation, and anchor matching against the master layout.
OCR is used ONLY to find where words are and which master word they correspond to."""
from __future__ import annotations
import re, unicodedata, difflib
import numpy as np, cv2, pytesseract

def to_gray(img):
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img

def flatten_illumination(g):
    """Divide by a smooth background estimate (removes shadows / gradients)."""
    small = cv2.resize(g, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
    bg = cv2.dilate(small, np.ones((9, 9), np.uint8))
    bg = cv2.GaussianBlur(bg, (0, 0), 6)
    bg = cv2.resize(bg, (g.shape[1], g.shape[0]), interpolation=cv2.INTER_LINEAR).astype(np.float32)
    out = np.clip(g.astype(np.float32) / np.maximum(bg, 20) * 235.0, 0, 255)
    return out.astype(np.uint8)

def norm_token(t: str) -> str:
    t = unicodedata.normalize("NFC", t).lower()
    t = "".join(ch for ch in t if unicodedata.category(ch)[0] in "LN" and unicodedata.category(ch) not in ("Mn", "Mc"))
    return t

def skeleton(t: str) -> str:
    """Script-tolerant key: base letters only (drops Devanagari matras / marks that OCR often garbles)."""
    return "".join(ch for ch in norm_token(t) if ch.isalnum())

def ocr_words(gray, lang="eng", upscale=1.5):
    im = cv2.resize(gray, None, fx=upscale, fy=upscale, interpolation=cv2.INTER_CUBIC) if upscale != 1 else gray
    d = pytesseract.image_to_data(im, lang=lang, config="--psm 6", output_type=pytesseract.Output.DICT)
    out = []
    for i, t in enumerate(d["text"]):
        t = t.strip()
        if not t:
            continue
        c = float(d["conf"][i])
        if c < 20:
            continue
        x, y, w, h = [d[k][i] / upscale for k in ("left", "top", "width", "height")]
        out.append(dict(text=t, conf=c, x0=x, y0=y, x1=x + w, y1=y + h, cx=x + w / 2, cy=y + h / 2))
    return out

def match_to_master(ocr, layout, min_len=3):
    """Longest-common-subsequence style matching of OCR tokens to master tokens.
    Returns list of (ocr_idx, master_word_id)."""
    mw = layout["words"]
    mk = [(i, skeleton(w["text"])) for i, w in enumerate(mw)]
    mk = [(i, s) for i, s in mk if len(s) >= min_len]
    ok = [(i, skeleton(o["text"])) for i, o in enumerate(ocr)]
    ok = [(i, s) for i, s in ok if len(s) >= min_len]
    sm = difflib.SequenceMatcher(None, [s for _, s in ok], [s for _, s in mk], autojunk=False)
    pairs = []
    for a, b, n in sm.get_matching_blocks():
        for t in range(n):
            pairs.append((ok[a + t][0], mk[b + t][0]))
    return pairs

def estimate_H(ocr, pairs, layout, ransac_pt=3.0):
    """Photo px -> master pt.  homography when there are enough anchors, else affine."""
    if len(pairs) < 4:
        return None, 0, pairs
    src = np.float32([[ocr[o]["cx"], ocr[o]["cy"]] for o, _ in pairs])
    dst = np.float32([[(layout["words"][m]["x0"] + layout["words"][m]["x1"]) / 2,
                       (layout["words"][m]["y0"] + layout["words"][m]["y1"]) / 2] for _, m in pairs])
    n = len(pairs)
    if n >= 30:
        H, inl = cv2.findHomography(src, dst, cv2.RANSAC, ransac_pt, maxIters=5000, confidence=0.999)
    else:
        A, inl = cv2.estimateAffine2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=ransac_pt, maxIters=3000)
        H = None if A is None else np.vstack([A, [0, 0, 1]])
    if H is None or inl is None:
        return None, 0, pairs
    inl = inl.ravel().astype(bool)
    return H, int(inl.sum()), [p for p, k in zip(pairs, inl) if k]


def estimate_skew(gray, max_angle=45.0):
    """In-plane rotation of the text lines in degrees (positive = counter-clockwise) by maximising row-profile variance."""
    f = 900.0 / max(gray.shape[:2]); small = cv2.resize(gray, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    ink = cv2.adaptiveThreshold(small, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 12)
    h, w = ink.shape; c = (w / 2, h / 2)
    def score(a):
        M = cv2.getRotationMatrix2D(c, a, 1.0); r = cv2.warpAffine(ink, M, (w, h), flags=cv2.INTER_NEAREST)
        return float(np.var(r.sum(1).astype(np.float64)))
    coarse = np.arange(-max_angle, max_angle + 0.01, 1.0); a0 = coarse[int(np.argmax([score(a) for a in coarse]))]
    fine = np.arange(a0 - 1.0, a0 + 1.01, 0.2)
    return float(fine[int(np.argmax([score(a) for a in fine]))])

def rotate_expand(img, angle):
    h, w = img.shape[:2]; M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    c, s_ = abs(M[0, 0]), abs(M[0, 1]); nw, nh = int(h * s_ + w * c), int(h * c + w * s_)
    M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
    return cv2.warpAffine(img, M, (nw, nh), flags=cv2.INTER_CUBIC, borderValue=int(np.median(img)))
