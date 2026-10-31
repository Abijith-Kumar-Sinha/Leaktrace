"""E5 follow-up: arbitrary in-plane rotation with decoder v2 (skew estimate + multi-scale OCR), fresh trials.
v1.1 failed at 30 degrees (0/12) because Tesseract cannot read steeply skewed lines."""
import sys, os, numpy as np
from common.config import SEED
from eval.harness import run_jobs, load, wilson, get_env
from eval.e2_identification import NOM, POOL, seed_of
OUT = "outputs/e5"; RES = f"{OUT}/e5_rotation_v2.jsonl"
ANGLES = [15, 30, 45, -30, -45]

def build_jobs():
    rng = np.random.default_rng(SEED + 55); jobs = []
    for a in ANGLES:
        for i in range(12):
            jid = f"e5rot2|{a}|{i}"; ci = int(rng.integers(POOL)); d = dict(NOM, blur=1.0, out_width=2000); d["seed"] = seed_of(jid)
            jobs.append(dict(id=jid, exp="e5rot2", cond=f"rotate {a}", lang="en", ci=ci, page=int(rng.integers(3)), deg=d, post=[("rotate", a)],
                             truth_idx=[ci], print_dpi=600, jitter=0.05, jseed=ci, ocr_scales=[1.5, 3.0, 4.5], deskew=True))
    return jobs

def analyse():
    R = [r for r in load(RES) if "error" not in r]; ids = get_env("en").ids
    L = ["# E5 follow-up - in-plane rotation, decoder v2 (skew estimate + multi-scale OCR), fresh trials\n", "| rotation | n | correct & accepted | 95% CI |", "|---|---|---|---|"]
    for a in ANGLES:
        rs = [r for r in R if r["job"]["cond"] == f"rotate {a}"]
        k = sum(r["accept"] and r["best"] == ids[r["job"]["ci"]] for r in rs); lo, hi = wilson(k, len(rs))
        L.append(f"| {a} deg | {len(rs)} | {k}/{len(rs)} = {100*k/max(len(rs),1):.0f}% | {100*lo:.0f}-{100*hi:.0f}% |")
    open(f"{OUT}/e5_rotation_v2.md", "w").write("\n".join(L)); print("\n".join(L))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "analyse": analyse()
    else: run_jobs(build_jobs(), RES)
