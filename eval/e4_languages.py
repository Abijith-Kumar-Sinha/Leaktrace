"""E4 - English vs Hindi (Devanagari): same conditions, accuracy + script-specific error analysis."""
import sys, os, json, numpy as np
from collections import defaultdict
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common.config import SEED
from eval.harness import run_jobs, load, wilson, get_env, Degrade, photograph, crop_for_lines
from eval.e2_identification import NOM, HARD, POOL, seed_of, CONDS, deg_for

PHYS = dict(print_dpi=600, jitter=0.05)   # default physical model for E3-E5: 600 dpi laser dots + 0.05 pt per-word placement noise
OUT = "outputs/e4"; RES = f"{OUT}/e4_results.jsonl"
COND4 = ["nominal phone photo", "blur 2.5", "jpeg q20", "width 600", "hard combined (WhatsApp)", "paper warp 1.0pt"]
CROPS = [6, 3]

def build_jobs(quick=False):
    rng = np.random.default_rng(SEED + 4); n = 3 if quick else 12; jobs = []
    for lang in ("en", "hi"):
        env = get_env(lang)
        for cond in COND4:
            for i in range(n):
                jid = f"e4|{lang}|{cond}|{i}"; ci = int(rng.integers(POOL)); pg = int(rng.integers(3))
                d, jit = deg_for(cond, seed_of(jid))
                jobs.append(dict(**PHYS, id=jid, exp="e4", cond=cond, lang=lang, ci=ci, page=pg, deg=d, jseed=ci, truth_idx=[ci]))
        for nl in CROPS:
            for i in range(n):
                jid = f"e4|{lang}|crop{nl}|{i}"; ci = int(rng.integers(POOL)); pg = int(rng.integers(3))
                nlines = len(env.layout["pages"][pg]["lines"]); first = int(rng.integers(0, nlines - nl))
                d = dict(NOM, blur=1.0); d["seed"] = seed_of(jid)
                jobs.append(dict(**PHYS, id=jid, exp="e4", cond=f"crop {nl} lines", lang=lang, ci=ci, page=pg, deg=d, crop_lines=[first, nl], truth_idx=[ci]))
        for i in range(n * 2):                                     # plain pages in this language
            jid = f"e4|{lang}|plain|{i}"; d, _ = deg_for(["nominal phone photo", "hard combined (WhatsApp)"][i % 2], seed_of(jid))
            jobs.append(dict(**PHYS, id=jid, exp="e4", cond="PLAIN page", lang=lang, ci=0, page=int(rng.integers(3)), deg=d, plain=True))
    return jobs

def run(quick=False):
    os.makedirs(OUT, exist_ok=True)
    run_jobs(build_jobs(quick), RES if not quick else RES + ".quick")

def diagnostics():
    """Per-gap error vs word width, per language, on a handful of blurred photos (uses ground truth)."""
    out = {}
    for lang in ("en", "hi"):
        env = get_env(lang); dec = env.dec; rows = []
        rng = np.random.default_rng(SEED + 44)
        for i in range(6):
            ci = int(rng.integers(POOL)); pg = i % 3
            pages = env.copy_pages(ci)
            img, _ = photograph(pages[pg], Degrade(**dict(NOM, blur=2.0, seed=i)), env.layout["page_size_pt"])
            r = dec.decode(img, debug=True)
            if "_debug" not in r: continue
            dbg = r["_debug"]; words = dbg["words"]; wid = {w["id"]: k for k, w in enumerate(words)}
            sg = env.bank.S_gap[ci]
            for ln in env.layout["pages"][pg]["lines"]:
                ids = ln["words"]
                for k in range(len(ids) - 1):
                    j = env.bank.gap_index[(pg, ln["id"], k)]
                    if dbg["q_gap"][j] <= 0 or sg[j] == 0: continue
                    a, b = env.layout["words"][ids[k]], env.layout["words"][ids[k + 1]]
                    wmin = min(a["x1"] - a["x0"], b["x1"] - b["x0"])
                    rows.append((wmin, abs(dbg["r_gap"][j] - sg[j]), float(dbg["q_gap"][j])))
        out[lang] = np.array(rows)
    return out

def analyse():
    allr = load(RES); R = [r for r in allr if "error" not in r]
    ok = lambda r: r["accept"] and r["best"] == get_env(r["job"]["lang"]).ids[r["job"]["ci"]]
    L = ["# E4 results - English vs Hindi (delta=eps=0.30 pt, 200 candidate centres)\n",
         "| condition | English correct & accepted | Hindi correct & accepted | EN top-1 before significance test | HI top-1 before significance test | EN gap-error RMSE | HI gap-error RMSE | EN line-error RMSE | HI line-error RMSE |", "|---|---|---|---|---|---|---|---|---|"]
    conds = COND4 + [f"crop {n} lines" for n in CROPS]
    plot = {"en": [], "hi": []}
    for c in conds:
        row = [c]; ge = {}; le = {}; t1 = {}
        for lang in ("en", "hi"):
            rs = [r for r in R if r["job"]["cond"] == c and r["job"]["lang"] == lang]
            k = sum(ok(r) for r in rs); row.append(f"{k}/{len(rs)} = {100*k/max(len(rs),1):.0f}%"); plot[lang].append(100 * k / max(len(rs), 1))
            t1[lang] = sum(1 for r in rs if r.get("variants") and r["variants"]["both"]["best"] == r["job"]["ci"])
            g = [r["err_gap_rmse"] for r in rs if r.get("err_gap_rmse") is not None]; l_ = [r["err_line_rmse"] for r in rs if r.get("err_line_rmse") is not None]
            ge[lang] = np.mean(g) if g else float("nan"); le[lang] = np.mean(l_) if l_ else float("nan")
        ntot = {lg: len([r for r in R if r["job"]["cond"] == c and r["job"]["lang"] == lg]) for lg in ("en", "hi")}
        row += [f"{t1['en']}/{ntot['en']}", f"{t1['hi']}/{ntot['hi']}"]
        L.append("| " + " | ".join(row) + f" | {ge['en']:.2f} | {ge['hi']:.2f} | {le['en']:.2f} | {le['hi']:.2f} |")
    L.append("\n## False accepts on plain pages\n")
    for lang in ("en", "hi"):
        rs = [r for r in R if r["job"]["cond"] == "PLAIN page" and r["job"]["lang"] == lang]; fa = sum(r["accept"] for r in rs)
        L.append(f"- {lang}: {fa} accepted of {len(rs)}")
    L.append("\n## Alignment (OCR anchors) - median RANSAC inliers on page / words on page\n")
    for lang in ("en", "hi"):
        env = get_env(lang)
        inl = [r["inl"] for r in R if r["job"]["lang"] == lang and r["job"]["cond"] in ("nominal phone photo",) and r.get("inl")]
        wp = np.mean([sum(1 for w in env.layout["words"] if w["page"] == p) for p in range(3)])
        L.append(f"- {lang}: median inliers {np.median(inl) if inl else float('nan'):.0f} of ~{wp:.0f} words per page")
    D = diagnostics()
    L.append("\n## Per-gap measurement error vs width of the narrower neighbouring word (blur sigma 2.0 px photos; error = |r - s_true|)\n")
    L.append("| narrower word width (pt) | EN mean error | EN n | HI mean error | HI n |"); L.append("|---|---|---|---|---|")
    edges = [0, 15, 25, 40, 60, 1e9]
    for a, b in zip(edges[:-1], edges[1:]):
        cells = []
        for lang in ("en", "hi"):
            m = (D[lang][:, 0] >= a) & (D[lang][:, 0] < b)
            cells += [f"{D[lang][m, 1].mean():.2f}" if m.any() else "-", str(int(m.sum()))]
        L.append(f"| {a:.0f}-{b if b < 1e8 else 'inf'} | " + " | ".join(cells) + " |")
    open(f"{OUT}/e4_tables.md", "w").write("\n".join(L)); print("\n".join(L))
    fig, ax = plt.subplots(figsize=(8, 3.8)); x = np.arange(len(conds)); w = .38
    ax.bar(x - w / 2, plot["en"], w, label="English", color="#2b6cb0"); ax.bar(x + w / 2, plot["hi"], w, label="Hindi", color="#c05621")
    ax.set_xticks(x); ax.set_xticklabels(conds, rotation=25, ha="right", fontsize=8); ax.set_ylabel("correct centre, accepted (%)"); ax.legend(); ax.set_ylim(0, 105); ax.grid(axis="y", alpha=.3)
    plt.tight_layout(); plt.savefig(f"{OUT}/e4_languages.png", dpi=160)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "analyse": analyse()
    else: run(quick="--quick" in sys.argv)
