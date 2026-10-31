"""LeakTrace API.  Run:  uvicorn api.main:app --port 8000   (from the repo root, with PYTHONPATH=.)

Paper Preparation Module  POST /api/prepare   (paper + centres + secret key) -> background job -> ZIP of per-centre PDFs
Investigation Dashboard   POST /api/decode    (photo + case id + key)         -> ranked centres, confidence, accept/reject, overlay
The secret key is used in memory only; it is never written to disk or logged.
"""
from __future__ import annotations
import os, io, json, uuid, zipfile, threading, hashlib, base64, time, re
import numpy as np, cv2
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from common.keys import SignBank, word_offsets
from embed.typeset import render, rasterise
from decode.pipeline import Decoder
from decode.overlay import draw_overlay, NOTICE

app = FastAPI(title="LeakTrace", description="Exam-paper leak attribution. " + NOTICE)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
DATA = os.environ.get("LEAKTRACE_DATA", "outputs/cases")
os.makedirs(DATA, exist_ok=True)
JOBS: dict[str, dict] = {}
_DEC: dict[str, Decoder] = {}
_LOCK = threading.Lock()
DISCLAIMER = ("LeakTrace is an INVESTIGATIVE-LEAD tool. A match shows which centre's printed copy the photographed paper most "
              "probably came from; it does not prove who leaked it, and a retyped paper carries no fingerprint.")

def paper_from_upload(name: str, raw: bytes, lang: str) -> dict:
    if name.lower().endswith(".json"):
        p = json.loads(raw.decode("utf-8")); assert {"title", "questions"} <= set(p); p.setdefault("lang", lang)
        p.setdefault("subtitle", ""); p.setdefault("instructions", []); return p
    txt = raw.decode("utf-8").strip().replace("\r", "")
    blocks = [b.strip().replace("\n", " ") for b in re.split(r"\n\s*\n", txt) if b.strip()]
    return dict(lang=lang, title=blocks[0], subtitle="", instructions=[], questions=blocks[1:])

def parse_centres(raw: bytes) -> list[str]:
    ids = [l.split(",")[0].strip() for l in raw.decode("utf-8").splitlines()]
    ids = [i for i in ids if i and i.lower() not in ("centre", "centre_id", "id")]
    if len(set(ids)) != len(ids) or not ids: raise HTTPException(400, "centre ids must be unique and non-empty")
    if len(ids) > 5000: raise HTTPException(400, "at most 5000 centres")
    return ids

def _prepare_worker(job_id, paper, ids, key, delta, eps, case_dir):
    J = JOBS[job_id]
    try:
        pdf, layout = render(paper)
        J["total"] = len(ids)
        open(f"{case_dir}/master.pdf", "wb").write(pdf)
        json.dump(layout, open(f"{case_dir}/layout.json", "w"))
        json.dump(dict(centres=ids, delta=delta, eps=eps, lang=paper["lang"], title=paper["title"], created=time.time()), open(f"{case_dir}/meta.json", "w"))
        bank = SignBank(key, layout, ids)
        zpath = f"{case_dir}/copies.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("master_layout.json", json.dumps(layout))
            z.writestr("master_UNMARKED_keep_secret.pdf", pdf)
            for i, cid in enumerate(ids):
                off = word_offsets(layout, bank, i, delta, eps)
                cpdf, _ = render(paper, off)
                z.writestr(f"copies/{cid}.pdf", cpdf)
                J["done"] = i + 1
            z.writestr("README.txt", f"LeakTrace case {job_id}\nOne PDF per centre. Keep master_UNMARKED_keep_secret.pdf and the secret key private.\n{DISCLAIMER}\n")
        J["state"] = "done"
    except Exception as e:
        J["state"] = "error"; J["error"] = str(e)

@app.post("/api/prepare")
async def prepare(paper: UploadFile = File(...), centres: UploadFile = File(...), key: str = Form(...), lang: str = Form("en"),
                  delta: float = Form(0.30), eps: float = Form(0.30)):
    if len(key) < 12: raise HTTPException(400, "secret key must be at least 12 characters")
    if not (0.02 <= delta <= 1.5 and 0.02 <= eps <= 1.5): raise HTTPException(400, "delta/epsilon must be between 0.02 and 1.5 pt")
    pap = paper_from_upload(paper.filename, await paper.read(), lang); ids = parse_centres(await centres.read())
    job_id = uuid.uuid4().hex[:10]; case_dir = f"{DATA}/{job_id}"; os.makedirs(case_dir)
    JOBS[job_id] = dict(state="running", done=0, total=len(ids))
    threading.Thread(target=_prepare_worker, args=(job_id, pap, ids, key, delta, eps, case_dir), daemon=True).start()
    return dict(case_id=job_id, centres=len(ids))

@app.get("/api/prepare/{job_id}")
def prepare_status(job_id: str):
    if job_id not in JOBS: raise HTTPException(404, "unknown job")
    return JOBS[job_id]

@app.get("/api/prepare/{job_id}/zip")
def prepare_zip(job_id: str):
    p = f"{DATA}/{job_id}/copies.zip"
    if not os.path.exists(p) or JOBS.get(job_id, {}).get("state") != "done": raise HTTPException(404, "not ready")
    return FileResponse(p, media_type="application/zip", filename=f"leaktrace_{job_id}.zip")

@app.get("/api/cases")
def cases():
    out = []
    for c in sorted(os.listdir(DATA)):
        m = f"{DATA}/{c}/meta.json"
        if os.path.exists(m): out.append(dict(case_id=c, **{k: v for k, v in json.load(open(m)).items() if k != "centres"}, n_centres=len(json.load(open(m))["centres"])))
    return out

def _decoder(case_id, key):
    kh = hashlib.sha256((case_id + "|" + key).encode()).hexdigest()
    with _LOCK:
        if kh in _DEC: return _DEC[kh], json.load(open(f"{DATA}/{case_id}/meta.json"))
        cd = f"{DATA}/{case_id}"
        if not os.path.exists(f"{cd}/meta.json"): raise HTTPException(404, "unknown case")
        meta = json.load(open(f"{cd}/meta.json")); layout = json.load(open(f"{cd}/layout.json"))
        master = rasterise(open(f"{cd}/master.pdf", "rb").read())
        d = Decoder(layout, master, key, meta["centres"], meta["delta"], meta["eps"], cache_dir=f"{DATA}/_nullcache")
        _DEC[kh] = d
        return d, meta

@app.post("/api/decode")
async def decode(photo: UploadFile = File(...), case_id: str = Form(...), key: str = Form(...), alpha: float = Form(1e-3)):
    raw = await photo.read(); img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    if img is None: raise HTTPException(400, "could not read the image")
    dec, meta = _decoder(case_id, key); dec.alpha = alpha
    r = dec.decode(img, debug=True, ocr_scales=(1.5, 3.0, 4.5), deskew=True)
    dbg = r.pop("_debug", None)
    overlay = None
    if dbg is not None:
        ov = draw_overlay(cv2.cvtColor(dbg['norm'], cv2.COLOR_GRAY2BGR), dbg, dec.bank, r["best"], meta["delta"], meta["eps"])
        overlay = "data:image/jpeg;base64," + base64.b64encode(cv2.imencode(".jpg", ov, [cv2.IMWRITE_JPEG_QUALITY, 85])[1]).decode()
    clean = {k: (v if not isinstance(v, (np.floating, np.integer)) else v.item()) for k, v in r.items() if k not in ("H",)}
    clean.pop("best", None); clean.pop("second", None); clean.pop("candidates", None)
    return JSONResponse(dict(result=clean, overlay=overlay, notice=NOTICE, disclaimer=DISCLAIMER))

@app.get("/api/health")
def health(): return dict(ok=True, notice=NOTICE)
