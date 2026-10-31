"""E3 - partial leaks: accuracy vs number of visible lines; smallest crop reaching 90%; QR / header baselines; 1/sqrt(M) check."""
import sys, os, json, zlib, numpy as np
from collections import defaultdict
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common.config import SEED
from eval.harness import run_jobs, load, wilson, get_env, Degrade, photograph
from eval.e2_identification import NOM, HARD, POOL, seed_of
from eval import baselines

PHYS = dict(print_dpi=600, jitter=0.05)   # default physical model for E3-E5: 600 dpi laser dots + 0.05 pt per-word placement noise
OUT = "outputs/e3"; RES = f"{OUT}/e3_results.jsonl"; BRES = f"{OUT}/e3_baselines.jsonl"
V2 = "--v2" in sys.argv     # decoder v2: OCR retried at 3.0x / 4.5x when the first pass finds < 12 anchors (fresh trials)
if V2: RES = f"{OUT}/e3_results_v2.jsonl"; BRES = f"{OUT}/e3_baselines_v2.jsonl"
NS_A = [1, 2, 3, 4, 6, 8, 12, 20]
NS_B = [1, 2, 4, 8, 12, 20, 40]
QUAL = {"nominal": dict(NOM, blur=1.0), "hard": HARD}

def windows(n_lines, page_h, rng, pitch=17.5):
    h = n_lines * pitch; y0 = float(rng.uniform(0, page_h - h)); return (0.0, y0, 595.28, y0 + h)

def build_jobs(quick=False):
    rng = np.random.default_rng(SEED + (103 if V2 else 3)); env = get_env("en"); n = 3 if quick else 14
    pre = "v2|" if V2 else ""; extra = dict(ocr_scales=[1.5, 3.0, 4.5]) if V2 else {}
    jobs = []; Bspec = []
    for q, base in QUAL.items():                                    # (A) crop aligned to whole text lines (best case for any mark)
        for nl in NS_A:
            for i in range(n):
                jid = f"{pre}e3A|{q}|{nl}|{i}"; ci = int(rng.integers(POOL)); pg = int(rng.integers(3))
                nlines = len(env.layout["pages"][pg]["lines"]); first = int(rng.integers(0, max(1, nlines - nl)))
                d = dict(base); d["seed"] = seed_of(jid)
                jobs.append(dict(**PHYS, **extra, id=jid, exp="e3A", cond=f"{q}", n_lines=nl, lang="en", ci=ci, page=pg, deg=d, crop_lines=[first, nl], truth_idx=[ci]))
    for nl in NS_B:                                                 # (B) random rectangular window anywhere on the page (fair to header/QR)
        for i in range(n):
            jid = f"{pre}e3B|nominal|{nl}|{i}"; ci = int(rng.integers(POOL)); pg = int(rng.integers(3))
            rect = windows(nl, env.layout["page_size_pt"][1], rng)
            d = dict(QUAL["nominal"]); d["seed"] = seed_of(jid)
            jobs.append(dict(**PHYS, **extra, id=jid, exp="e3B", cond="nominal", n_lines=nl, lang="en", ci=ci, page=pg, deg=d, crop_rect=rect, truth_idx=[ci]))
    return jobs

def baseline_run(jobs):
    env = get_env("en"); rows = []
    for j in jobs:
        if j["exp"] != "e3B": continue
        cid = env.ids[j["ci"]]
        for kind in ("header", "qr"):
            pages = baselines.baseline_pages(env.paper, cid, kind)
            d = Degrade(**j["deg"]); d.crop = tuple(j["crop_rect"])
            img, _ = photograph(pages[j["page"]], d, env.layout["page_size_pt"])
            got = baselines.read_header(img) if kind == "header" else baselines.read_qr(img)
            rows.append(dict(n_lines=j["n_lines"], kind=kind, ok=bool(got == cid)))
    with open(BRES, "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")

def run(quick=False):
    os.makedirs(OUT, exist_ok=True)
    jobs = build_jobs(quick)
    run_jobs(jobs, RES if not quick else RES + ".quick")
    baseline_run(jobs)

def analyse():
    allr = load(RES); R = [r for r in allr if "error" not in r]; ids = get_env("en").ids
    ok = lambda r: r["accept"] and r["best"] == ids[r["job"]["ci"]]
    L = [f"# E3 results - partial leaks (English, delta=eps=0.30 pt, 600 dpi print model, 200 candidate centres) - decoder {'v2 (multi-scale OCR, fresh trials)' if V2 else 'v1.1 (rotation-loop bug fixed)'}\n",
         "## (A) Crop aligned to whole text lines (fingerprint only; header/QR cannot survive such a crop by construction)\n",
         "| visible lines | quality | n | correct & accepted | 95% CI | top-1 before significance test | median positions used (gaps+lines) | median z |", "|---|---|---|---|---|---|---|---|"]
    curves = {}
    for q in QUAL:
        for nl in NS_A:
            rs = [r for r in R if r["job"]["exp"] == "e3A" and r["job"]["cond"] == q and r["job"]["n_lines"] == nl]
            if not rs: continue
            k = sum(ok(r) for r in rs); lo, hi = wilson(k, len(rs)); M = np.median([(r["n_gaps"] or 0) + (r["n_lines"] or 0) for r in rs])
            curves.setdefault(q, []).append((nl, k / len(rs), lo, hi, M))
            L.append(f"| {nl} | {q} | {len(rs)} | {k}/{len(rs)} = {100*k/len(rs):.0f}% | {100*lo:.0f}-{100*hi:.0f}% | {sum(1 for r in rs if r.get('variants') and r['variants']['both']['best'] == r['job']['ci'])}/{len(rs)} | {M:.0f} | {np.median([r.get('z') or 0 for r in rs]):.1f} |")
    L.append("\n**Smallest crop reaching >= 90% point accuracy:** " + "; ".join(
        f"{q}: " + next((f"{c[0]} line(s)" for c in curves[q] if c[1] >= 0.9), "none of the tested sizes") for q in curves))
    # (B)
    L += ["\n## (B) Random rectangular window anywhere on the page, nominal quality (same window, same photo conditions for every method)\n",
          "| window height (lines) | LeakTrace fingerprint | header serial (OCR) | QR code (single location) |", "|---|---|---|---|"]
    B = load(BRES) if os.path.exists(BRES) else []
    bcurve = defaultdict(list)
    for nl in NS_B:
        rs = [r for r in R if r["job"]["exp"] == "e3B" and r["job"]["n_lines"] == nl]
        if not rs: continue
        a = sum(ok(r) for r in rs)
        h = [b["ok"] for b in B if b["n_lines"] == nl and b["kind"] == "header"]; qq = [b["ok"] for b in B if b["n_lines"] == nl and b["kind"] == "qr"]
        L.append(f"| {nl} | {a}/{len(rs)} = {100*a/len(rs):.0f}% | {sum(h)}/{len(h)} = {100*sum(h)/max(len(h),1):.0f}% | {sum(qq)}/{len(qq)} = {100*sum(qq)/max(len(qq),1):.0f}% |")
        bcurve["fp"].append((nl, a / len(rs))); bcurve["header"].append((nl, sum(h) / max(len(h), 1))); bcurve["qr"].append((nl, sum(qq) / max(len(qq), 1)))
    # 1/sqrt(M) check: null sigma of the score vs number of positions used
    pts = [((r["n_gaps"] or 0) + (r["n_lines"] or 0), r["sd"]) for r in R if r.get("sd") and (r["n_gaps"] or 0) > 0 and r["job"]["exp"] == "e3A"]
    if len(pts) > 5:
        x = np.log([p[0] for p in pts]); y = np.log([p[1] for p in pts]); slope, icpt = np.polyfit(x, y, 1)
        res = y - (slope * x + icpt); r2 = 1 - res.var() / y.var()
        L.append(f"\n## Noise scaling\nEmpirical log-log fit of the wrong-key score spread sigma(T) against the number of visible positions M over {len(pts)} photos: slope = {slope:.2f} (theory: -0.50), R^2 = {r2:.2f}.")
    open(f"{OUT}/e3_tables{'_v2' if V2 else ''}.md", "w").write("\n".join(L)); print("\n".join(L))
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    for q, c in (("nominal", "#2b6cb0"), ("hard", "#c05621")):
        if q in curves:
            xs = [c_[0] for c_ in curves[q]]; ax[0].errorbar(xs, [100 * c_[1] for c_ in curves[q]], yerr=[[100 * (c_[1] - c_[2]) for c_ in curves[q]], [100 * (c_[3] - c_[1]) for c_ in curves[q]]], marker="o", color=c, label=q, capsize=2)
    ax[0].axhline(90, ls="--", color="gray", lw=.8); ax[0].set_xscale("log"); ax[0].set_xlabel("visible text lines"); ax[0].set_ylabel("correct centre, accepted (%)"); ax[0].set_title("(A) line-aligned crops"); ax[0].legend(); ax[0].grid(alpha=.3)
    for k, c, lab in (("fp", "#2b6cb0", "LeakTrace"), ("header", "#718096", "header serial"), ("qr", "#975a16", "QR code")):
        if bcurve.get(k): ax[1].plot([a for a, _ in bcurve[k]], [100 * b for _, b in bcurve[k]], "o-", color=c, label=lab)
    ax[1].set_xscale("log"); ax[1].set_xlabel("window height (text lines)"); ax[1].set_title("(B) random window, nominal quality"); ax[1].legend(); ax[1].grid(alpha=.3)
    plt.tight_layout(); plt.savefig(f"{OUT}/e3_partial{'_v2' if V2 else ''}.png", dpi=160)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "analyse": analyse()
    else: run(quick="--quick" in sys.argv)
