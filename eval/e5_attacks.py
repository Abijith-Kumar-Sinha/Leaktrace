"""E5 - attacks: rescaling / rotation / enhancement, collusion of 2-3 copies, noise injection, retyping (documented limit)."""
import sys, os, json, numpy as np, itertools
from collections import defaultdict
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common.config import SEED
from eval.harness import run_jobs, load, wilson, get_env
from eval.e2_identification import NOM, HARD, POOL, seed_of
import embed.typeset as TS

PHYS = dict(print_dpi=600, jitter=0.05)   # default physical model for E3-E5: 600 dpi laser dots + 0.05 pt per-word placement noise
OUT = "outputs/e5"; RES = f"{OUT}/e5_results.jsonl"
POST = [("rotate", 10), ("rotate", 30), ("rot90", 90), ("rot90", 180), ("rescale", 0.35), ("rescale", 0.2), ("jpeg", 15), ("median", 3), ("unsharp", 2.0), ("contrast", 0.5)]

def build_jobs(quick=False):
    rng = np.random.default_rng(SEED + 5); n = 3 if quick else 12; jobs = []
    for kind, p in POST:                                           # (a) post-capture transformations of a nominal photo
        for i in range(n):
            jid = f"e5|post|{kind}{p}|{i}"; ci = int(rng.integers(POOL)); d = dict(NOM, blur=1.0, out_width=2000); d["seed"] = seed_of(jid)
            jobs.append(dict(**PHYS, id=jid, exp="e5post", cond=f"{kind} {p}", lang="en", ci=ci, page=int(rng.integers(3)), deg=d, post=[(kind, p)], truth_idx=[ci]))
    for k in (2, 3):                                               # (b) collusion
        for kind in ("avg", "mix"):
            for i in range(n):
                jid = f"e5|coll|{k}|{kind}|{i}"; idx = [int(x) for x in rng.choice(POOL, k, replace=False)]; d = dict(NOM, blur=1.0); d["seed"] = seed_of(jid)
                jobs.append(dict(**PHYS, id=jid, exp="e5coll", cond=f"{k} colluders, {kind}", k=k, kind=kind, lang="en", ci=idx[0], page=int(rng.integers(3)), deg=d,
                                 mix=[kind, idx], jseed=i, truth_idx=idx))
    for s in (0.1, 0.2, 0.4, 0.8):                                 # (c) noise injection: random per-word displacement added by the adversary
        for i in range(n):
            jid = f"e5|jit|{s}|{i}"; ci = int(rng.integers(POOL)); d = dict(NOM, blur=1.0); d["seed"] = seed_of(jid)
            jobs.append(dict(print_dpi=600, id=jid, exp="e5jit", cond=f"adversary jitter {s}pt", lang="en", ci=ci, page=int(rng.integers(3)), deg=d, jitter=s, jseed=100 + i, truth_idx=[ci]))
    for i in range(n):                                             # (d) retyped with the same template (plain text, no fingerprint)
        jid = f"e5|retype_same|{i}"; d = dict(NOM, blur=1.0); d["seed"] = seed_of(jid)
        jobs.append(dict(**PHYS, id=jid, exp="e5retype", cond="retyped, same template", lang="en", ci=0, page=int(rng.integers(3)), deg=d, plain=True))
    return jobs

def retype_different_layout(quick=False):
    """Retyped in another font size / column width: the master geometry no longer applies."""
    from eval.harness import Degrade, photograph, get_env
    env = get_env("en"); dec = env.dec; res = []
    old = dict(TS.FONTS)
    try:
        for i, (fs, lh) in enumerate([(10.5, 1.5), (11.5, 1.5), (11.0, 1.7)][: (1 if quick else 3)]):
            TS.FONTS["en"] = ('"Liberation Serif"', fs, lh)
            pdf, lay = TS.render(env.paper); pg = TS.rasterise(pdf)
            for p in range(3):
                img, _ = photograph(pg[p], Degrade(**dict(NOM, blur=1.0, seed=7 * i + p)), lay["page_size_pt"])
                r = dec.decode(img)
                res.append(dict(variant=f"font {fs}pt / line-height {lh}", page=p, accept=bool(r["accept"]), reason=r.get("reason"), best=r.get("best_centre"), p_best=r.get("p_best")))
    finally:
        TS.FONTS.clear(); TS.FONTS.update(old)
    return res

def run(quick=False):
    os.makedirs(OUT, exist_ok=True)
    run_jobs(build_jobs(quick), RES if not quick else RES + ".quick")
    json.dump(retype_different_layout(quick), open(f"{OUT}/e5_retype_layout.json", "w"), indent=1)

def analyse():
    R = [r for r in load(RES) if "error" not in r]; env = get_env("en"); ids = env.ids
    L = ["# E5 results - attacks (English, delta=eps=0.30 pt, 200 candidate centres)\n", "## (a) Post-capture transformations of a nominal photo\n",
         "| attack | n | correct & accepted | 95% CI | rejected as unreadable/no-fingerprint |", "|---|---|---|---|---|"]
    for kind, p in POST:
        rs = [r for r in R if r["job"]["cond"] == f"{kind} {p}"]
        if not rs: continue
        k = sum(r["accept"] and r["best"] == ids[r["job"]["ci"]] for r in rs); lo, hi = wilson(k, len(rs))
        L.append(f"| {kind} {p} | {len(rs)} | {k}/{len(rs)} = {100*k/len(rs):.0f}% | {100*lo:.0f}-{100*hi:.0f}% | {sum(not r['accept'] for r in rs)} |")
    L += ["\n## (b) Collusion (colluders' copies averaged position-wise, or mixed line-by-line)\n",
          "Candidate set = centres whose score is significant at family-wise alpha=1e-3 (Bonferroni over 200 centres, up to 6 reported).\n"
          "A looser *lead* set uses z>=3.5 (about 5% family-wise) on the same scores.\n",
          "| scenario | n | all colluders in strict set | >=1 colluder in strict set | innocents in strict set (mean) | all colluders in lead set (z>=3.5) | innocents in lead set (mean) | top-1 is a colluder |", "|---|---|---|---|---|---|---|---|"]
    for k in (2, 3):
        for kind in ("avg", "mix"):
            rs = [r for r in R if r["job"]["cond"] == f"{k} colluders, {kind}"]
            if not rs: continue
            allin = anyin = inn = lall = linn = top1 = 0
            for r in rs:
                tr = {ids[i] for i in r["job"]["truth_idx"]}; cs = set(r.get("cands") or []) if r["accept"] else set()
                allin += tr <= cs; anyin += bool(tr & cs); inn += len(cs - tr)
                lead = {ids[i] for i, z in r.get("top_z", []) if z >= 3.5}; lall += tr <= lead; linn += len(lead - tr)
                top1 += (r.get("best") in tr)
            n = len(rs)
            L.append(f"| {k} colluders, {kind} | {n} | {allin}/{n} | {anyin}/{n} | {inn/n:.2f} | {lall}/{n} | {linn/n:.2f} | {top1}/{n} |")
    L.append("\n## (c) Adversary adds random per-word displacement (noise injection)\n"); L.append("| added jitter sigma | n | correct & accepted | 95% CI |"); L.append("|---|---|---|---|")
    for s in (0.1, 0.2, 0.4, 0.8):
        rs = [r for r in R if r["job"]["cond"] == f"adversary jitter {s}pt"]
        if rs:
            k = sum(r["accept"] and r["best"] == ids[r["job"]["ci"]] for r in rs); lo, hi = wilson(k, len(rs))
            L.append(f"| {s} pt | {len(rs)} | {k}/{len(rs)} = {100*k/len(rs):.0f}% | {100*lo:.0f}-{100*hi:.0f}% |")
    L.append("\n## (d) Retyping - DOCUMENTED LIMIT: the fingerprint lives in the layout, not in the words\n")
    rs = [r for r in R if r["job"]["cond"] == "retyped, same template"]
    L.append(f"- Retyped text, same template/fonts (no offsets): {sum(r['accept'] for r in rs)} accepted of {len(rs)} -> correctly **rejected** (no fingerprint survives; the lead is lost, not misattributed).")
    rl = json.load(open(f"{OUT}/e5_retype_layout.json")) if os.path.exists(f"{OUT}/e5_retype_layout.json") else []
    if rl:
        L.append(f"- Retyped with a different font size / line height: {sum(x['accept'] for x in rl)} accepted of {len(rl)}; "
                 f"{sum(1 for x in rl if (x['reason'] or '').startswith('alignment'))} failed to align to the master; the rest were rejected as not significant.")
    open(f"{OUT}/e5_tables.md", "w").write("\n".join(L)); print("\n".join(L))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "analyse": analyse()
    else: run(quick="--quick" in sys.argv)
