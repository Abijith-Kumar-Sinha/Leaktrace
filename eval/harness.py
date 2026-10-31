"""Shared experiment harness: environments, cached copy rendering, degradation, parallel trial runner."""
from __future__ import annotations
import os, json, time, hashlib, itertools
import numpy as np, cv2
from multiprocessing import Pool
from common.config import SEED, RASTER_SCALE
from common.keys import SignBank, word_offsets
from embed.typeset import render, rasterise
from degrade.simulate import Degrade, photograph, crop_for_lines
from decode.pipeline import Decoder, build_master
from decode import score

KEY = "leaktrace-experiment-key-v1"          # experiments use a different key than the dev key used while building
CACHE = "outputs/cache/copies"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Env:
    def __init__(self, lang="en", n_centres=200, key=KEY, delta=0.30, eps=0.30):
        self.lang, self.key, self.delta, self.eps = lang, key, delta, eps
        self.paper = json.load(open(os.path.join(ROOT, f"data/mock_papers/{'english' if lang=='en' else 'hindi'}.json")))
        self.pdf, self.layout, self.master = build_master(self.paper)
        self.ids = [f"C{i:04d}" for i in range(n_centres)]
        self.dec = Decoder(self.layout, self.master, key, self.ids, delta, eps, cache_dir="outputs/cache")
        self.bank = self.dec.bank
        os.makedirs(CACHE, exist_ok=True)

    def decoder(self, delta, eps):
        d = Decoder.__new__(Decoder); d.__dict__.update(self.dec.__dict__); d.delta, d.eps = delta, eps; return d

    def copy_pages(self, ci, delta=None, eps=None, jitter=0.0, jseed=0, mix=None):
        """Rasters of centre ci's copy.  mix: list of (centre_index) for collusion -> ('avg'|'mix', idxs)."""
        delta = self.delta if delta is None else delta; eps = self.eps if eps is None else eps
        tag = hashlib.sha1(json.dumps([self.lang, self.key, ci, delta, eps, jitter, jseed, mix], default=str).encode()).hexdigest()[:14]
        paths = [f"{CACHE}/{tag}_p{p}.png" for p in range(len(self.layout["pages"]))]
        if all(os.path.exists(p) for p in paths):
            return [cv2.imread(p, 0) for p in paths]
        if mix is None:
            off = word_offsets(self.layout, self.bank, ci, delta, eps)
        else:
            kind, idxs = mix
            offs = [word_offsets(self.layout, self.bank, i, delta, eps) for i in idxs]
            rng = np.random.default_rng(jseed + 17)
            off = {}
            if kind == "avg":                    # colluders average their copies (position-wise mean)
                for w in offs[0]:
                    off[w] = tuple(np.mean([o[w] for o in offs], axis=0))
            else:                                # "mix": each LINE is taken from a randomly chosen colluder
                for pg in self.layout["pages"]:
                    for ln in pg["lines"]:
                        o = offs[int(rng.integers(len(offs)))]
                        for w in ln["words"]:
                            off[w] = o[w]
        if jitter > 0:                           # imperfect printing: independent random placement error per word
            rng = np.random.default_rng(jseed + 99)
            off = {w: (dx + rng.normal(0, jitter), dy + rng.normal(0, jitter)) for w, (dx, dy) in off.items()}
        pdf, _ = render(self.paper, off)
        pages = rasterise(pdf)
        for p, im in zip(paths, pages):
            cv2.imwrite(p, im)
        return pages

def true_signs(env, ci, page):
    """(gap-sign, line-sign) rows of centre ci (for measurement-error statistics)."""
    return env.bank.S_gap[ci], env.bank.S_line[ci]

def variants(dbg, env, delta, eps):
    """Score the SAME measurements under decoder variants: both channels / gap only / line only."""
    out = {}
    for name, (ug, ul) in dict(both=(True, True), gap_only=(True, False), line_only=(False, True)).items():
        T, den = score.scores(env.bank, dbg["r_gap"], dbg["q_gap"], dbg["r_line"], dbg["q_line"], env.dec.w_line, ug, ul)
        T0, _ = score.scores(env.dec.null, dbg["r_gap"], dbg["q_gap"], dbg["r_line"], dbg["q_line"], env.dec.w_line, ug, ul)
        d = score.decide(T, T0, env.dec.alpha, min_den=6.0, den=den)
        out[name] = dict(best=d["best"], accept=d["accept"], p_best=d["p_best"], z=d["z_best"], T_best=d["T_best"], sd=d["sigma_null"], den=float(den), T=T)
    return out

_ENVS = {}
def get_env(lang, delta=0.30, eps=0.30):
    k = (lang, delta, eps)
    if k not in _ENVS:
        _ENVS[k] = Env(lang, delta=delta, eps=eps)
    return _ENVS[k]

def run_one(job):
    """job: dict(lang, ci, page, deg(dict), delta, eps, jitter, jseed, mix, plain(bool), truth_idx(list|None), tag fields...)"""
    try:
        env = get_env(job["lang"], job.get("env_delta", 0.30), job.get("env_eps", 0.30))
        delta, eps = job.get("delta", 0.30), job.get("eps", 0.30)
        if job.get("plain"):
            pages = env.master
        else:
            pages = env.copy_pages(job["ci"], delta, eps, job.get("jitter", 0.0), job.get("jseed", 0), job.get("mix"))
        d = Degrade(**job["deg"])
        crop = job.get("crop_lines")
        if crop:
            d.crop = crop_for_lines(env.layout, job["page"], crop[0], crop[1], full_width=job.get("crop_full_width", True))
        img, info = photograph(pages[job["page"]], d, env.layout["page_size_pt"])
        dec = env.decoder(delta, eps)
        r = dec.decode(img, debug=True)
        rec = dict(job={k: v for k, v in job.items() if k not in ("deg",)}, deg=job["deg"], accept=r["accept"], reason=r.get("reason"),
                   best=r.get("best_centre"), p_best=r.get("p_best"), z=r.get("z_best"), T_best=r.get("T_best"), T_second=r.get("T_second"),
                   sd=r.get("sigma_null"), n_gaps=r.get("n_gaps"), n_lines=r.get("n_lines"), inl=r.get("n_inliers"),
                   cands=r.get("candidate_centres"), t=r["timing"].get("total"))
        dbg = r.get("_debug")
        if dbg is not None:
            v = variants(dbg, env, delta, eps)
            rec["variants"] = {k: {kk: vv for kk, vv in x.items() if kk != "T"} for k, x in v.items()}
            tgt = job.get("truth_idx")
            if tgt:
                rec["T_true"] = [float(v["both"]["T"][i]) for i in tgt]
                rec["rank_true"] = [int((v["both"]["T"] > v["both"]["T"][i]).sum()) for i in tgt]
                sg = env.bank.S_gap[tgt[0]]; sl = env.bank.S_line[tgt[0]]
                mg = dbg["q_gap"] > 0; ml = dbg["q_line"] > 0
                if len(tgt) == 1:
                    rec["err_gap_rmse"] = float(np.sqrt(np.mean((dbg["r_gap"][mg] - sg[mg]) ** 2))) if mg.any() else None
                    rec["err_line_rmse"] = float(np.sqrt(np.mean((dbg["r_line"][ml] - sl[ml]) ** 2))) if ml.any() else None
                    rec["gap_q_mean"] = float(dbg["q_gap"][mg].mean()) if mg.any() else None
        return rec
    except Exception as e:                       # never lose a whole sweep to one bad trial
        import traceback
        return dict(job={k: v for k, v in job.items() if k != "deg"}, deg=job.get("deg"), error=traceback.format_exc()[-600:], accept=False, best=None)

def run_jobs(jobs, out_path, workers=2, resume=True):
    done = set()
    if resume and os.path.exists(out_path):
        for line in open(out_path):
            try: done.add(json.loads(line)["job"]["id"])
            except Exception: pass
    todo = [j for j in jobs if j["id"] not in done]
    t0 = time.time()
    with open(out_path, "a") as f, Pool(workers) as pool:
        for i, rec in enumerate(pool.imap_unordered(run_one, todo, chunksize=1), 1):
            f.write(json.dumps(rec, default=float) + "\n"); f.flush()
            if i % 20 == 0:
                print(f"  {i}/{len(todo)}  {time.time()-t0:.0f}s", flush=True)
    return out_path

def load(path):
    return [json.loads(l) for l in open(path)]

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0, c - h), min(1, c + h))
