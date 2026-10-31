"""E2b - offset size vs printer resolution (the physical floor): bilevel laser dots + 0.05 pt per-word placement noise.
Full-page nominal photo, and a 6-line crop.   python -m eval.e2b_printer [analyse]"""
import sys, os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common.config import SEED
from eval.harness import run_jobs, load, wilson, get_env
from eval.e2_identification import NOM, POOL, seed_of

OUT = "outputs/e2"; RES = f"{OUT}/e2b_results.jsonl"
DPIS = [1200, 600, 300, 150]; DELTAS = [0.05, 0.10, 0.15, 0.20, 0.30, 0.40]

def build_jobs(quick=False):
    rng = np.random.default_rng(SEED + 22); n = 2 if quick else 8; jobs = []; env = get_env("en")
    for mode in ("full page", "6-line crop"):
        dl_list = DELTAS if mode == "full page" else [0.10, 0.20, 0.30, 0.40]
        dpis = DPIS if mode == "full page" else [600, 300]
        for dpi in dpis:
            for dl in dl_list:
                for i in range(n):
                    jid = f"e2b|{mode}|{dpi}|{dl}|{i}"; ci = int(rng.integers(POOL)); pg = int(rng.integers(3))
                    d = dict(NOM, blur=1.0); d["seed"] = seed_of(jid)
                    j = dict(id=jid, exp="e2b", cond=mode, dpi=dpi, delta_val=dl, lang="en", ci=ci, page=pg, deg=d, delta=dl, eps=dl, print_dpi=dpi, jitter=0.05, jseed=ci, truth_idx=[ci])
                    if mode == "6-line crop":
                        nl = len(env.layout["pages"][pg]["lines"]); j["crop_lines"] = [int(rng.integers(0, nl - 6)), 6]
                    jobs.append(j)
    return jobs

def analyse():
    R = [r for r in load(RES) if "error" not in r]; ids = get_env("en").ids
    L = ["# E2b - offset size vs printer resolution (delta = epsilon; 0.05 pt per-word placement noise; nominal photo)\n",
         "Cell = correct centre & accepted / trials. One dot = 72/dpi pt: 1200 dpi 0.06 pt, 600 dpi 0.12 pt, 300 dpi 0.24 pt, 150 dpi 0.48 pt.\n"]
    for mode in ("full page", "6-line crop"):
        rs = [r for r in R if r["job"]["cond"] == mode]
        if not rs: continue
        dpis = sorted({r["job"]["dpi"] for r in rs}, reverse=True); dls = sorted({r["job"]["delta_val"] for r in rs})
        L += [f"\n## {mode}\n", "| delta (pt) | " + " | ".join(f"{d} dpi" for d in dpis) + " |", "|---|" + "---|" * len(dpis)]
        grid = np.zeros((len(dls), len(dpis)))
        for a, dl in enumerate(dls):
            cells = []
            for b, dpi in enumerate(dpis):
                x = [r for r in rs if r["job"]["dpi"] == dpi and r["job"]["delta_val"] == dl]
                k = sum(r["accept"] and r["best"] == ids[r["job"]["ci"]] for r in x); grid[a, b] = k / max(len(x), 1)
                cells.append(f"{k}/{len(x)}")
            L.append(f"| {dl} | " + " | ".join(cells) + " |")
        plt.figure(figsize=(4.6, 3.4)); plt.imshow(100 * grid, vmin=0, vmax=100, cmap="Blues", origin="lower", aspect="auto")
        plt.xticks(range(len(dpis)), dpis); plt.yticks(range(len(dls)), dls); plt.xlabel("printer dpi"); plt.ylabel("delta = epsilon (pt)"); plt.colorbar(label="% correct")
        plt.title(mode); plt.tight_layout(); plt.savefig(f"{OUT}/e2b_{mode.split()[0]}.png", dpi=150); plt.close()
    open(f"{OUT}/e2b_tables.md", "w").write("\n".join(L)); print("\n".join(L))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "analyse": analyse()
    else: os.makedirs(OUT, exist_ok=True); run_jobs(build_jobs("--quick" in sys.argv), RES)
