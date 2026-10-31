"""Scripted photo degradations: perspective, rotation, blur, resize, lighting, noise, crop, JPEG, WhatsApp.

Everything is seeded (np.random.Generator) so a given (page, params, seed) always gives the same photo.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict, field
import numpy as np, cv2
from common.config import RASTER_SCALE

@dataclass
class Degrade:
    out_width: int = 1600          # width in px of the whole page in the photo (resize)
    persp: float = 0.0             # perspective severity 0..1 (corner jitter, fraction of 5% of width)
    rot_deg: float = 0.0           # in-plane rotation
    blur: float = 0.0              # defocus blur sigma in photo px
    motion: float = 0.0            # motion blur length in photo px
    noise: float = 0.0             # gaussian sensor noise sigma (8-bit levels)
    light: float = 0.0             # lighting change strength 0..1 (gradient, vignette, gamma)
    jpeg: int | None = None        # JPEG quality applied to the photo (None = lossless)
    crop: tuple | None = None      # (x0,y0,x1,y1) in PAGE POINTS kept after capture
    whatsapp: bool = False         # post-crop: resize long side<=1600 and JPEG q=whatsapp_q
    whatsapp_q: int = 72
    background: bool = True        # dark table around the page
    feed_jitter_pt: float = 0.0    # smooth vertical paper-feed error amplitude (printer), pt
    nonrigid_pt: float = 0.0       # smooth non-homographic warp amplitude (paper curl / lens), pt
    seed: int = 0
    def tag(self):
        return {k: v for k, v in asdict(self).items()}

def _feed_warp(page, amp_pt, rng, scale=RASTER_SCALE):
    """Smooth vertical displacement field dy(y) (printer feed roller error)."""
    h, w = page.shape
    ys = np.arange(h, dtype=np.float32)
    dy = np.zeros(h, np.float32)
    for period_pt in (40.0, 97.0, 230.0):
        dy += rng.uniform(0.3, 1.0) * np.sin(2 * np.pi * ys / (period_pt * scale) + rng.uniform(0, 6.28))
    dy *= amp_pt * scale / 2.0
    mapy = (ys + dy)[:, None].repeat(w, 1).astype(np.float32)
    mapx = np.arange(w, dtype=np.float32)[None, :].repeat(h, 0)
    return cv2.remap(page, mapx, mapy, cv2.INTER_CUBIC, borderValue=255)

def _nonrigid_warp(page, amp_pt, rng, scale=RASTER_SCALE):
    """Low-frequency 2-D displacement field that a homography cannot absorb."""
    h, w = page.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = np.zeros((h, w), np.float32); dy = np.zeros((h, w), np.float32)
    for period_pt in (140.0, 260.0, 480.0):
        for (f, g) in ((dx, 0), (dy, 1)):
            ax, ay = rng.uniform(-1, 1, 2)
            f += rng.uniform(0.4, 1.0) * np.sin(2 * np.pi * (ax * xx + ay * yy) / (period_pt * scale) + rng.uniform(0, 6.28))
    k = amp_pt * scale / 1.8
    return cv2.remap(page, xx + dx * k, yy + dy * k, cv2.INTER_CUBIC, borderValue=255)

def photograph(page: np.ndarray, d: Degrade, page_size_pt, scale: float = RASTER_SCALE):
    """page: uint8 gray raster at `scale` px/pt.  Returns (img uint8 gray, info dict with H page_px->img_px)."""
    rng = np.random.default_rng(d.seed)
    src = page.astype(np.float32)
    if d.feed_jitter_pt > 0:
        src = _feed_warp(src, d.feed_jitter_pt, rng, scale)
    if d.nonrigid_pt > 0:
        src = _nonrigid_warp(src, d.nonrigid_pt, rng, scale)
    src = src * (225.0 / 255.0) + 12.0 * 0  # paper is slightly grey, ink stays dark
    h0, w0 = src.shape
    margin = 0.06 if d.background else 0.0
    Wc = int(round(d.out_width * (1 + 2 * margin)))
    s = d.out_width / w0
    Hc = int(round(h0 * s + 2 * margin * d.out_width))
    ox = margin * d.out_width
    base = np.float32([[0, 0], [w0, 0], [w0, h0], [0, h0]])
    dst = base * s + np.float32([ox, ox])
    c = dst.mean(0)
    th = np.deg2rad(d.rot_deg)
    R = np.float32([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    dst = (dst - c) @ R.T + c
    dst += rng.uniform(-1, 1, (4, 2)).astype(np.float32) * d.persp * 0.05 * d.out_width
    H = cv2.getPerspectiveTransform(base, dst.astype(np.float32))
    # anti-alias before shrinking
    sig = max(0.0, 0.5 * (1.0 / s) - 0.5)
    if sig > 0.05:
        src = cv2.GaussianBlur(src, (0, 0), sig)
    bg = 55.0 if d.background else 225.0
    img = cv2.warpPerspective(src, H, (Wc, Hc), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=bg)
    if d.light > 0:
        yy, xx = np.mgrid[0:Hc, 0:Wc].astype(np.float32)
        a = rng.uniform(0, 2 * np.pi)
        grad = (np.cos(a) * (xx / Wc - 0.5) + np.sin(a) * (yy / Hc - 0.5))
        vig = 1 - 0.5 * (((xx / Wc - 0.5) ** 2 + (yy / Hc - 0.5) ** 2))
        gain = (1 + 0.55 * d.light * grad) * (1 - 0.35 * d.light * (1 - vig))
        img = img * gain
        img = 255.0 * np.clip(img / 255.0, 0, 1) ** (1 + 0.35 * d.light * rng.uniform(-1, 1))
    if d.blur > 0:
        img = cv2.GaussianBlur(img, (0, 0), d.blur)
    if d.motion > 1:
        k = int(d.motion) | 1
        ker = np.zeros((k, k), np.float32); ker[k // 2, :] = 1.0 / k
        M = cv2.getRotationMatrix2D((k / 2 - 0.5, k / 2 - 0.5), rng.uniform(0, 180), 1)
        ker = cv2.warpAffine(ker, M, (k, k)); ker /= max(ker.sum(), 1e-6)
        img = cv2.filter2D(img, -1, ker)
    if d.noise > 0:
        img = img + rng.normal(0, d.noise, img.shape).astype(np.float32)
    img = np.clip(img, 0, 255).astype(np.uint8)
    if d.jpeg is not None:
        img = cv2.imdecode(cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, int(d.jpeg)])[1], 0)
    info = dict(H=H.tolist(), crop_px=None)
    if d.crop is not None:
        x0, y0, x1, y1 = d.crop
        pts = np.float32([[x0, y0], [x1, y0], [x1, y1], [x0, y1]]) * scale
        q = cv2.perspectiveTransform(pts[None], H)[0]
        cx0, cy0 = np.maximum(np.floor(q.min(0)), 0).astype(int)
        cx1, cy1 = np.minimum(np.ceil(q.max(0)), [Wc, Hc]).astype(int)
        img = img[cy0:cy1, cx0:cx1]
        info["crop_px"] = [int(cx0), int(cy0), int(cx1), int(cy1)]
        T = np.array([[1, 0, -cx0], [0, 1, -cy0], [0, 0, 1]], float)
        info["H"] = (T @ H).tolist()
    if d.whatsapp:
        long = max(img.shape)
        if long > 1600:
            f = 1600.0 / long
            img = cv2.resize(img, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
            S = np.diag([f, f, 1.0]); info["H"] = (S @ np.array(info["H"])).tolist()
        img = cv2.imdecode(cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, d.whatsapp_q])[1], 0)
    return img, info

def crop_for_lines(layout, page_index, first_line, n_lines, pad_pt=2.0, full_width=True):
    """Crop rectangle (page points) that contains n_lines consecutive text lines of one page."""
    ls = layout["pages"][page_index]["lines"][first_line:first_line + n_lines]
    y0 = ls[0]["y0"] - pad_pt; y1 = ls[-1]["y1"] + pad_pt
    pw = layout["page_size_pt"][0]
    return (0.0, y0, pw, y1) if full_width else (min(l["x0"] for l in ls) - 6, y0, max(l["x1"] for l in ls) + 6, y1)
