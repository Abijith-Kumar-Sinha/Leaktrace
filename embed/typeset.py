"""HTML -> PDF typesetting with exact per-word / per-line control (WeasyPrint, HarfBuzz shaping).

Master  : flow layout, every word is its own <span class="w" id="wN">.
Copy    : IDENTICAL html, but selected spans get `position:relative; left:dx; top:dy`.
          Relative positioning does not change flow, so line breaks / justification are untouched.
"""
from __future__ import annotations
import html as _html, json
import numpy as np
import pymupdf
from weasyprint import HTML
from common.config import PX_TO_PT, RASTER_SCALE

FONTS = {"en": ('"Liberation Serif"', 11.0, 1.50), "hi": ('"FreeSerif"', 12.0, 1.55)}

def _css(lang):
    fam, size, lh = FONTS[lang]
    return f"""
@page {{ size: A4; margin: 22mm 20mm 20mm 20mm; }}
html {{ font-family: {fam}; font-size: {size}pt; line-height: {lh}; color: #000; }}
body {{ margin: 0; text-align: justify; hyphens: none; }}
h1 {{ font-size: {size+4}pt; text-align: center; margin: 0 0 4pt 0; font-weight: bold; }}
.sub {{ font-size: {size-1.5}pt; text-align: center; margin: 0 0 6pt 0; }}
.rule {{ border-top: 0.8pt solid #000; margin: 4pt 0 8pt 0; }}
.ins {{ font-size: {size-1}pt; margin: 0 0 3pt 0; }}
.hd {{ font-weight: bold; margin: 6pt 0 3pt 0; text-align: left; }}
p.q {{ margin: 0 0 7pt 0; break-inside: avoid; }}
"""

def paper_units(paper: dict, max_questions: int | None = None):
    """-> list of (kind, text) units in reading order."""
    u = [("h1", paper["title"]), ("sub", paper["subtitle"]),
         ("rule", ""), ("hd", "Instructions" if paper["lang"] == "en" else "निर्देश")]
    for i, t in enumerate(paper["instructions"], 1):
        u.append(("ins", f"{i}. {t}"))
    u.append(("rule", ""))
    qs = paper["questions"][: max_questions] if max_questions else paper["questions"]
    for i, q in enumerate(qs, 1):
        u.append(("q", f"{i}. {q}"))
    return u

def build_html(paper: dict, offsets: dict | None = None, max_questions: int | None = None, decor_html: str = "", decor_css: str = ""):
    units = paper_units(paper, max_questions)
    parts, words, g = [], [], 0
    for kind, text in units:
        if kind == "rule":
            parts.append('<div class="rule"></div>'); continue
        spans = []
        for tok in text.split():
            style = ""
            if offsets is not None and g in offsets:
                dx, dy = offsets[g]
                if dx != 0 or dy != 0:
                    style = f' style="position:relative;left:{dx:.4f}pt;top:{dy:.4f}pt"'
            spans.append(f'<span class="w" id="w{g}"{style}>{_html.escape(tok)}</span>')
            words.append(tok); g += 1
        inner = " ".join(spans)
        tag = {"h1": "h1", "sub": "div class=\"sub\"", "hd": "div class=\"hd\"",
               "ins": "div class=\"ins\"", "q": "p class=\"q\""}[kind]
        close = tag.split()[0]
        parts.append(f"<{tag}>{inner}</{close}>")
    doc = f'<!doctype html><html lang="{paper["lang"]}"><head><meta charset="utf-8"><style>{_css(paper["lang"])}{decor_css}</style></head><body>{decor_html}{"".join(parts)}</body></html>'
    return doc, words

def render(paper, offsets=None, max_questions=None, decor_html="", decor_css=""):
    """-> (pdf_bytes, layout dict).  Layout is read from WeasyPrint's laid-out box tree."""
    html_s, words = build_html(paper, offsets, max_questions, decor_html, decor_css)
    document = HTML(string=html_s).render()
    layout = extract_layout(document, words)
    layout["lang"] = paper["lang"]
    return document.write_pdf(), layout

def extract_layout(document, words):
    pages = []
    wmeta = {}
    for pi, page in enumerate(document.pages):
        lines = []
        def walk(b):
            name = type(b).__name__
            if name == "LineBox":
                ws = []
                def inl(x):
                    for c in getattr(x, "children", []):
                        el = getattr(c, "element", None)
                        if type(c).__name__ == "InlineBox" and el is not None and el.get("class") == "w":
                            gid = int(el.get("id")[1:])
                            ws.append((gid, c))
                        else:
                            inl(c)
                inl(b)
                if ws:
                    lid = len(lines)
                    ids = []
                    for gid, c in ws:
                        x0, y0 = c.position_x * PX_TO_PT, c.position_y * PX_TO_PT
                        wmeta[gid] = dict(id=gid, text=words[gid], page=pi, line=lid, idx=len(ids),
                                          x0=x0, x1=x0 + c.width * PX_TO_PT,
                                          y0=y0, y1=y0 + c.height * PX_TO_PT)
                        ids.append(gid)
                    lines.append(dict(id=lid, words=ids,
                                      y0=min(wmeta[i]["y0"] for i in ids), y1=max(wmeta[i]["y1"] for i in ids),
                                      x0=wmeta[ids[0]]["x0"], x1=wmeta[ids[-1]]["x1"]))
                return
            for c in getattr(b, "children", []):
                walk(c)
        walk(page._page_box)
        pages.append(dict(index=pi, lines=lines))
    pw = document.pages[0]._page_box.margin_width() * PX_TO_PT
    ph = document.pages[0]._page_box.margin_height() * PX_TO_PT
    return dict(page_size_pt=[pw, ph], pages=pages, words=[wmeta[i] for i in sorted(wmeta)])

def rasterise(pdf_bytes: bytes, scale: float = RASTER_SCALE, page: int | None = None):
    """-> list of uint8 grayscale arrays (one per page) at `scale` px per point."""
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    out = []
    for i, p in enumerate(doc):
        if page is not None and i != page:
            continue
        pm = p.get_pixmap(matrix=pymupdf.Matrix(scale, scale), colorspace=pymupdf.csGRAY, alpha=False)
        out.append(np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width).copy())
    return out
