"""E1 human half: forced-choice reader-study KIT (generate) and ANALYSIS (analyse).

  python -m eval.reader_study generate     -> outputs/e1/reader_study/{study.html, trials_key.csv, print_booklet.pdf, README.txt}
  python -m eval.reader_study analyse responses_*.csv

Task per trial: two crops of the same passage, shown at real size; ONE is fingerprinted, one is plain.
Participant picks "which one has been modified".  Chance = 50%.  Anonymous: no names, no identifiers.
"""
import sys, os, csv, json, base64, glob
import numpy as np, cv2
from eval.harness import get_env, wilson
from common.keys import word_offsets
from embed.typeset import render, rasterise
from scipy.stats import binomtest

OUT = "outputs/e1/reader_study"
LEVELS = [0.10, 0.20, 0.30, 0.40, 0.60, 0.80, 1.50]    # 1.50 = deliberately obvious catch level
REPS = 4
PX = 3.0   # px per pt in the images

def crop_pair(env, delta, rng, page=1, n_lines=7):
    lay = env.layout; lines = lay["pages"][page]["lines"]
    start = int(rng.integers(4, len(lines) - n_lines - 1))
    ci = int(rng.integers(len(env.ids)))
    off = word_offsets(lay, env.bank, ci, delta, delta)
    from embed.typeset import render as R
    pdf, _ = R(env.paper, off); pg = rasterise(pdf, PX)[page]
    mp = rasterise(env.pdf, PX)[page]
    y0 = int((lines[start]["y0"] - 4) * PX); y1 = int((lines[start + n_lines]["y1"] + 4) * PX)
    x0 = int(lay["pages"][page]["lines"][start]["x0"] * PX) - 10; x1 = x0 + int(480 * PX)
    return mp[y0:y1, x0:x1], pg[y0:y1, x0:x1]

def generate(seed=20261031):
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(seed)
    trials = []
    for lang in ("en", "hi"):
        env = get_env(lang)
        for d in LEVELS:
            for r in range(REPS):
                plain, fp = crop_pair(env, d, rng)
                fp_left = bool(rng.integers(2))
                trials.append(dict(lang=lang, delta=d, fp_left=fp_left, left=fp if fp_left else plain, right=plain if fp_left else fp))
    order = rng.permutation(len(trials)); trials = [trials[i] for i in order]
    key = []
    items = []
    for i, t in enumerate(trials):
        enc = lambda im: base64.b64encode(cv2.imencode(".png", im, [cv2.IMWRITE_PNG_COMPRESSION, 9])[1]).decode()
        items.append(dict(id=i, L=enc(t["left"]), R=enc(t["right"])))
        key.append(dict(trial=i, lang=t["lang"], delta_pt=t["delta"], fingerprinted_side="L" if t["fp_left"] else "R"))
        cv2.imwrite(f"{OUT}/trial_{i:03d}_L.png", t["left"]); cv2.imwrite(f"{OUT}/trial_{i:03d}_R.png", t["right"])
    with open(f"{OUT}/trials_key.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(key[0])); w.writeheader(); w.writerows(key)
    css_scale = 96 / 72 / PX
    html = f"""<!doctype html><meta charset=utf-8><title>LeakTrace reader study</title>
<style>body{{font-family:system-ui;max-width:900px;margin:20px auto;padding:0 12px}} .pair{{display:flex;gap:18px;align-items:flex-start;margin:10px 0}}
.pair div{{border:2px solid #ccc;padding:4px;cursor:pointer;background:#fff}} .pair div:hover{{border-color:#2b6cb0}} img{{width:calc(var(--w)*{css_scale}px);image-rendering:auto}}
.note{{background:#fffbea;border:1px solid #ecc94b;padding:8px;margin:10px 0;font-size:14px}}</style>
<h2>Reader study (anonymous, about 10 minutes)</h2>
<div class=note>Two copies of the same passage are shown. One has had its word spacing and line positions slightly altered; the other is untouched. Click the copy you think was <b>altered</b>. If you genuinely cannot tell, still pick one (guessing is fine and expected). Please view this page at 100% browser zoom, at a normal reading distance. Nothing is sent anywhere: answers stay in this page until you press Download. No name or personal detail is collected.</div>
<div id=app></div><script>
const items={json.dumps(items)}; let i=0; const ans=[];
function show(){{ if(i>=items.length){{done();return;}}
 const it=items[i]; document.getElementById('app').innerHTML=`<p>Trial ${{i+1}} of ${{items.length}}</p><div class=pair>
 <div onclick="pick('L')"><img onload="this.style.setProperty('--w',this.naturalWidth)" src="data:image/png;base64,${{it.L}}"></div>
 <div onclick="pick('R')"><img onload="this.style.setProperty('--w',this.naturalWidth)" src="data:image/png;base64,${{it.R}}"></div></div>
 <p>Click the one that was altered. <span style="color:#777">(Left / Right)</span></p>`;}}
function pick(s){{ans.push({{trial:items[i].id,choice:s}});i++;show();}}
function done(){{ const csv='trial,choice\\n'+ans.map(a=>a.trial+','+a.choice).join('\\n');
 document.getElementById('app').innerHTML='<h3>Finished - thank you.</h3><p>Press the button and send the downloaded file to the study organiser.</p><button id=dl>Download my answers</button>';
 document.getElementById('dl').onclick=()=>{{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{{type:'text/csv'}}));a.download='responses_'+Math.random().toString(36).slice(2,8)+'.csv';a.click();}};}}
show();</script>"""
    open(f"{OUT}/study.html", "w").write(html)
    open(f"{OUT}/README.txt", "w").write(
"""LeakTrace E1 reader-study kit
1. Give study.html to >= 20 volunteers (any laptop/desktop browser, 100% zoom). Each completes {n} trials (2 languages x {l} offset levels x {r} repetitions, randomised).
2. Each volunteer returns the downloaded responses_*.csv (anonymous random file name).
3. Put all returned CSVs in one folder and run:  python -m eval.reader_study analyse "<folder>/responses_*.csv"
   (trials_key.csv holds the answer key: keep it away from volunteers.)
4. For the PRINTED variant (recommended, closer to the real use): print trial_XXX_L.png / _R.png pairs at 100% scale (3 px/pt = 216 dpi) on a laser printer.
Ethics: anonymous, voluntary, no personal data; get the course instructor's approval before running.
""".format(n=len(trials), l=len(LEVELS), r=REPS))
    print("trials:", len(trials), "->", OUT)

def analyse(pattern):
    key = {int(r["trial"]): r for r in csv.DictReader(open(f"{OUT}/trials_key.csv"))}
    files = glob.glob(pattern); n_vol = len(files)
    from collections import defaultdict
    tab = defaultdict(lambda: [0, 0])
    for f in files:
        for r in csv.DictReader(open(f)):
            k = key[int(r["trial"])]; tab[(k["lang"], float(k["delta_pt"]))][1] += 1
            tab[(k["lang"], float(k["delta_pt"]))][0] += int(r["choice"] == k["fingerprinted_side"])
    rows = []
    for (lang, d), (c, n) in sorted(tab.items()):
        lo, hi = wilson(c, n); p = binomtest(c, n, 0.5, alternative="greater").pvalue
        rows.append(dict(lang=lang, delta_pt=d, n=n, correct=c, acc=c / n, ci_lo=lo, ci_hi=hi, p_above_chance=p))
    with open(f"{OUT}/reader_study_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"{n_vol} volunteers")
    for lang in ("en", "hi"):
        r = [x for x in rows if x["lang"] == lang]; ok = 0.0
        for x in r:                      # largest delta such that this and all smaller levels are NOT detectably above chance
            if x["p_above_chance"] > 0.05: ok = x["delta_pt"]
            else: break
        print(lang, "largest unnoticed delta (Bonferroni-free, p>0.05 for it and all smaller):", ok)
    for x in rows: print(x)

if __name__ == "__main__":
    if sys.argv[1] == "generate": generate()
    else: analyse(sys.argv[2])
