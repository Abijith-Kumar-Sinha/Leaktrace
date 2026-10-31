"""E2 - centre identification on full-page photos: quality sweeps, false-accept rate on plain pages,
channel ablation (gap-only / line-only), header-only baseline, offset-size sweep.
   python -m eval.e2_identification [--quick]        # run
   python -m eval.e2_identification analyse          # tables + plots"""
import sys, os, json, zlib, numpy as np
from collections import defaultdict
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common.config import SEED
from eval.harness import run_jobs, load, wilson, get_env, Degrade, photograph, crop_for_lines
from eval import baselines

OUT = "outputs/e2"; RES = f"{OUT}/e2_results.jsonl"; BRES = f"{OUT}/e2_header_baseline.jsonl"
NOM = dict(out_width=1600, persp=0.3, noise=3, jpeg=90, blur=0.8)
HARD = dict(out_width=1000, persp=0.6, rot_deg=4, blur=1.5, noise=8, light=0.5, jpeg=60, whatsapp=True)

CONDS = {   # name -> degrade overrides (applied on top of NOM unless 'base' given)
    "ideal (no degradation)": dict(base=dict(out_width=2400, background=False)),
    "nominal phone photo": {},
    "blur 1.5": dict(blur=1.5), "blur 2.5": dict(blur=2.5), "blur 3.0": dict(blur=3.0),
    "jpeg q40": dict(jpeg=40), "jpeg q20": dict(jpeg=20),
    "width 900": dict(out_width=900), "width 600": dict(out_width=600),
    "perspective 1.0 + rot 8deg": dict(persp=1.0, rot_deg=8),
    "lighting 1.0": dict(light=1.0), "noise 15": dict(noise=15),
    "WhatsApp": dict(whatsapp=True),
    "hard combined (WhatsApp)": dict(base=HARD),
    "print jitter 0.10pt": dict(_jitter=0.10), "print jitter 0.20pt": dict(_jitter=0.20),
    "paper warp 0.5pt": dict(nonrigid_pt=0.5), "paper warp 1.0pt": dict(nonrigid_pt=1.0),
    "feed error 0.5pt": dict(feed_jitter_pt=0.5),
    "physical combined": dict(whatsapp=True, nonrigid_pt=0.5, feed_jitter_pt=0.3, _jitter=0.10),
}
POOL = 30        # distinct centres rendered per language (copies cached; all 200 are candidates)

def deg_for(cond, seed):
    o = dict(CONDS[cond]); base = dict(o.pop("base", NOM)); jit = o.pop("_jitter", 0.0)
    base.update(o); base["seed"] = seed
    return base, jit

def seed_of(job_id): return (SEED + zlib.crc32(job_id.encode())) % (2**31)

def build_jobs(quick=False):
    rng = np.random.default_rng(SEED)
    n = 3 if quick else 16
    jobs = []
    for cond in CONDS:
        for i in range(n):
            jid = f"e2|{cond}|{i}"; ci = int(rng.integers(POOL)); pg = int(rng.integers(3))
            d, jit = deg_for(cond, seed_of(jid))
            jobs.append(dict(id=jid, exp="e2", cond=cond, lang="en", ci=ci, page=pg, deg=d, jitter=jit, jseed=ci, truth_idx=[ci]))
    # false-accept: PLAIN pages and copies of centres NOT in the list, under mixed conditions
    mix = ["nominal phone photo", "WhatsApp", "hard combined (WhatsApp)", "blur 1.5", "jpeg q40", "width 900"]
    for i in range(10 if quick else 120):
        cond = mix[i % len(mix)]; jid = f"e2|plain|{i}"
        d, _ = deg_for(cond, seed_of(jid))
        jobs.append(dict(id=jid, exp="e2", cond="PLAIN page", sub=cond, lang="en", ci=0, page=int(rng.integers(3)), deg=d, plain=True))
    for i in range(6 if quick else 40):
        cond = mix[i % len(mix)]; jid = f"e2|unlisted|{i}"
        d, _ = deg_for(cond, seed_of(jid))
        jobs.append(dict(id=jid, exp="e2", cond="valid fingerprint, centre NOT in list", sub=cond, lang="en", ci=200 + i, page=int(rng.integers(3)), deg=d, jseed=i, unlisted=True))
    # offset-size sweep (full-page hard, and mild)
    for dl in (0.05, 0.10, 0.15, 0.20, 0.30, 0.40):
        for q, base in (("hard", HARD), ("nominal", dict(NOM, blur=1.5))):
            for i in range(3 if quick else 12):
                jid = f"e2|delta{dl}|{q}|{i}"; ci = int(rng.integers(POOL))
                d = dict(base); d["seed"] = seed_of(jid)
                jobs.append(dict(id=jid, exp="e2", cond=f"delta sweep {q}", delta_val=dl, lang="en", ci=ci, page=int(rng.integers(3)),
                                 deg=d, delta=dl, eps=dl, truth_idx=[ci]))
    return jobs

def header_jobs(quick=False):
    env = get_env("en"); rng = np.random.default_rng(SEED + 1)
    rows = []
    for cond in ["ideal (no degradation)", "nominal phone photo", "blur 2.5", "jpeg q20", "width 600", "hard combined (WhatsApp)", "WhatsApp"]:
        for i in range(3 if quick else 12):
            ci = int(rng.integers(POOL)); cid = env.ids[ci]; pg = int(rng.integers(3))
            d, _ = deg_for(cond, seed_of(f"hdr|{cond}|{i}"))
            for kind in ("header", "qr"):
                pages = baselines.baseline_pages(env.paper, cid, kind)
                img, _ = photograph(pages[pg], Degrade(**d), env.layout["page_size_pt"])
                got = baselines.read_header(img) if kind == "header" else baselines.read_qr(img)
                rows.append(dict(cond=cond, kind=kind, ok=bool(got == cid), got=got, truth=cid))
    with open(BRES, "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")

def run(quick=False):
    os.makedirs(OUT, exist_ok=True)
    jobs = build_jobs(quick)
    for j in jobs:                       # unlisted centres: render copies of centre ids beyond the 200 candidates
        if j.get("unlisted"):
            j["ci"] = j["ci"]
    run_jobs(jobs, RES if not quick else RES + ".quick")
    header_jobs(quick)

def analyse():
    R = [r for r in load(RES) if "error" not in r]
    errs = [r for r in load(RES) if "error" in r]
    by = defaultdict(list)
    for r in R: by[r["job"]["cond"]].append(r)
    lines = ["# E2 results (English, delta=eps=0.30 pt unless stated, 200 candidate centres)\n",
             "| condition | n | top-1 correct & accepted | 95% CI | accepted but wrong | rejected | median z | mean positions (gaps/lines) |", "|---|---|---|---|---|---|---|---|"]
    table = []
    for cond in CONDS:
        rs = by.get(cond, [])
        if not rs: continue
        ok = sum(1 for r in rs if r["accept"] and r["best"] == get_env("en").ids[r["job"]["ci"]])
        wrong = sum(1 for r in rs if r["accept"] and r["best"] != get_env("en").ids[r["job"]["ci"]])
        rej = sum(1 for r in rs if not r["accept"])
        lo, hi = wilson(ok, len(rs))
        z = np.median([r.get("z") or 0 for r in rs])
        ng = np.mean([r.get("n_gaps") or 0 for r in rs]); nl = np.mean([r.get("n_lines") or 0 for r in rs])
        table.append((cond, len(rs), ok, lo, hi, wrong, rej, z))
        lines.append(f"| {cond} | {len(rs)} | {ok}/{len(rs)} = {100*ok/len(rs):.0f}% | {100*lo:.0f}-{100*hi:.0f}% | {wrong} | {rej} | {z:.1f} | {ng:.0f}/{nl:.0f} |")
    # false accept
    lines.append("\n## False-accept rate (alpha = 1e-3 family-wise over 200 centres)\n")
    for key in ("PLAIN page", "valid fingerprint, centre NOT in list"):
        rs = by.get(key, [])
        if rs:
            fa = sum(1 for r in rs if r["accept"]); lo, hi = wilson(fa, len(rs))
            lines.append(f"- **{key}**: {fa} accepted of {len(rs)} (rate {100*fa/len(rs):.1f}%, 95% CI {100*lo:.1f}-{100*hi:.1f}%); "
                         f"median best z = {np.median([r.get('z') or 0 for r in rs]):.2f}; failed-to-align = {sum(1 for r in rs if (r.get('reason') or '').startswith('alignment'))}")
    # channel ablation, on the SAME measurements, over all genuine non-delta-sweep trials
    lines.append("\n## Channel ablation (same measurements, re-scored) - genuine trials of the 20 quality/physical conditions\n")
    lines.append("| decoder | top-1 correct & accepted | 95% CI | top-1 correct before the significance test | n |"); lines.append("|---|---|---|---|---|")
    ids = get_env("en").ids
    gen = [r for c in CONDS for r in by.get(c, []) if "variants" in r]
    for name in ("both", "gap_only", "line_only"):
        ok = sum(1 for r in gen if r["variants"][name]["accept"] and ids[r["variants"][name]["best"]] == ids[r["job"]["ci"]])
        lo, hi = wilson(ok, len(gen)); t1 = sum(1 for r in gen if r["variants"][name]["best"] == r["job"]["ci"]); lines.append(f"| {name.replace('_', ' ')} | {ok}/{len(gen)} = {100*ok/len(gen):.0f}% | {100*lo:.0f}-{100*hi:.0f}% | {t1}/{len(gen)} = {100*t1/len(gen):.0f}% | {len(gen)} |")
    # offset-size sweep
    lines.append("\n## Offset-size sweep (delta = epsilon)\n")
    lines.append("| delta (pt) | hard full-page: correct | nominal+blur1.5: correct |"); lines.append("|---|---|---|")
    sw = {}
    for q in ("hard", "nominal"):
        for r in by.get(f"delta sweep {q}", []):
            dl = r["job"]["delta_val"]; sw.setdefault((q, dl), []).append(r["accept"] and r["best"] == ids[r["job"]["ci"]])
    for dl in sorted({k[1] for k in sw}):
        a = sw.get(("hard", dl), []); b = sw.get(("nominal", dl), [])
        lines.append(f"| {dl} | {sum(a)}/{len(a)} | {sum(b)}/{len(b)} |")
    # header / QR baselines
    if os.path.exists(BRES):
        B = load(BRES); lines.append("\n## Baselines on full-page photos (mark visible; no cropping)\n")
        lines.append("| condition | header-serial read correctly (OCR) | QR code read correctly |"); lines.append("|---|---|---|")
        for cond in dict.fromkeys(b["cond"] for b in B):
            h = [b["ok"] for b in B if b["cond"] == cond and b["kind"] == "header"]; q = [b["ok"] for b in B if b["cond"] == cond and b["kind"] == "qr"]
            lines.append(f"| {cond} | {sum(h)}/{len(h)} | {sum(q)}/{len(q)} |")
    if errs: lines.append(f"\n({len(errs)} trials errored and are excluded; see jsonl)")
    open(f"{OUT}/e2_tables.md", "w").write("\n".join(lines)); print("\n".join(lines))
    # plot
    fig, ax = plt.subplots(figsize=(8, 5.2))
    names = [t[0] for t in table]; acc = [100 * t[2] / t[1] for t in table]
    err = [[100 * t[2] / t[1] - 100 * t[3] for t in table], [100 * t[4] - 100 * t[2] / t[1] for t in table]]
    ax.barh(range(len(names)), acc, xerr=err, color="#2b6cb0", capsize=2); ax.set_yticks(range(len(names))); ax.set_yticklabels(names, fontsize=7)
    ax.invert_yaxis(); ax.set_xlabel("correct centre, accepted (%)  [Wilson 95% CI]"); ax.set_xlim(0, 105); ax.grid(axis="x", alpha=.3)
    ax.set_title("E2: full-page identification (200 centres)"); plt.tight_layout(); plt.savefig(f"{OUT}/e2_accuracy.png", dpi=160)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "analyse": analyse()
    else: run(quick="--quick" in sys.argv)
