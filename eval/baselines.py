"""Baselines: a visible header serial, and a QR code in one fixed location (what real-world marks usually are)."""
import re, base64, os, hashlib, cv2, numpy as np
from embed.typeset import render, rasterise
from decode import locate
from common.config import RASTER_SCALE

def _qr_png(text):
    q = cv2.QRCodeEncoder.create().encode(text)
    q = cv2.resize(q, None, fx=8, fy=8, interpolation=cv2.INTER_NEAREST)
    q = cv2.copyMakeBorder(q, 24, 24, 24, 24, cv2.BORDER_CONSTANT, value=255)
    return base64.b64encode(cv2.imencode(".png", q)[1]).decode()

def decor(kind, centre_id):
    if kind == "header":   # serial printed in the page header, every page (best case for the header baseline)
        return (f'<div class="hdrmark">Centre {centre_id} &middot; Confidential</div>',
                '.hdrmark{position:fixed;top:-14mm;left:0;width:100%;text-align:center;font-size:9pt;font-family:"Liberation Serif"}')
    if kind == "qr":       # 56 pt (2 cm) square QR code in the bottom-right footer, every page
        return (f'<img class="qrmark" src="data:image/png;base64,{_qr_png(centre_id)}">',
                '.qrmark{position:fixed;right:0;bottom:-16mm;width:56pt;height:56pt}')
    raise ValueError(kind)

CACHE = "outputs/cache/baselines"
def baseline_pages(paper, centre_id, kind):
    os.makedirs(CACHE, exist_ok=True)
    tag = hashlib.sha1(f"{paper['lang']}|{centre_id}|{kind}|qr56pt-v2".encode()).hexdigest()[:12]
    ps = [f"{CACHE}/{tag}_{i}.png" for i in range(3)]
    if all(os.path.exists(p) for p in ps):
        return [cv2.imread(p, 0) for p in ps]
    h, c = decor(kind, centre_id)
    pdf, lay = render(paper, None, None, h, c)
    pages = rasterise(pdf)
    for p, im in zip(ps, pages): cv2.imwrite(p, im)
    return pages

def read_header(img, lang="eng"):
    norm = locate.flatten_illumination(locate.to_gray(img))
    txt = " ".join(o["text"] for o in locate.ocr_words(norm, lang))
    m = re.search(r"C\d{4}", txt)
    return m.group(0) if m else None

def read_qr(img):
    """Generous to the baseline: a QR counts as read if EITHER OpenCV's detector or zxing-cpp reads it (at 1x/2x/3x)."""
    g = locate.to_gray(img)
    try:
        import zxingcpp
        for up in (1.0, 2.0):
            im = cv2.resize(g, None, fx=up, fy=up, interpolation=cv2.INTER_CUBIC) if up != 1 else g
            r = zxingcpp.read_barcodes(im)
            if r: return r[0].text
    except Exception:
        pass
    det = cv2.QRCodeDetector()
    for up in (1.0, 2.0, 3.0):
        im = cv2.resize(g, None, fx=up, fy=up, interpolation=cv2.INTER_CUBIC) if up != 1 else g
        try:
            t, _, _ = det.detectAndDecode(im)
        except cv2.error:
            t = ""
        if t: return t
    return None
