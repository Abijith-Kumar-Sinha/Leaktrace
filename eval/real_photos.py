"""Real printed + photographed evidence: print-pack generator and evaluator.
   python -m eval.real_photos pack --lang en --centres 10        (needs env LEAKTRACE_KEY)
   python -m eval.real_photos run --labels data/photos/labels.csv --lang en --centres 200
"""
import sys, os, csv, argparse, json, numpy as np, cv2
from collections import defaultdict
from eval.harness import wilson, get_env
from common.keys import SignBank, word_offsets
from embed.typeset import render
from decode.pipeline import Decoder, build_master

def pack(a):
    key = os.environ["LEAKTRACE_KEY"]; out = "data/photos/print_pack"; os.makedirs(out, exist_ok=True)
    paper = json.load(open(f"data/mock_papers/{'english' if a.lang == 'en' else 'hindi'}.json"))
    pdf, lay = render(paper); ids = [f"C{i:04d}" for i in range(a.centres)]
    bank = SignBank(key, lay, ids)
    open(f"{out}/plain_master.pdf", "wb").write(pdf)
    for i, c in enumerate(ids):
        p, _ = render(paper, word_offsets(lay, bank, i, a.delta, a.eps)); open(f"{out}/{c}.pdf", "wb").write(p)
    open(f"{out}/PRINT_CHECKLIST.txt", "w").write("Print at 100% / actual size (NOT fit-to-page), A4, single-sided, laser. Record printer + paper in labels.csv.\n")
    print("print pack ->", out, len(ids), "centres + plain master; delta/eps", a.delta, a.eps)

def run(a):
    key = os.environ["LEAKTRACE_KEY"]; paper = json.load(open(f"data/mock_papers/{'english' if a.lang == 'en' else 'hindi'}.json"))
    pdf, lay, mp = build_master(paper); ids = [f"C{i:04d}" for i in range(a.centres)]
    dec = Decoder(lay, mp, key, ids, a.delta, a.eps)
    base = os.path.dirname(a.labels); rows = list(csv.DictReader(open(a.labels))); os.makedirs("outputs/real_photos", exist_ok=True); res = []
    for r in rows:
        img = cv2.imread(os.path.join(base, r["file"]))
        if img is None: print("missing", r["file"]); continue
        o = dec.decode(img); plain = r["is_plain_control"] == "1"
        res.append(dict(r, accept=o["accept"], best=o.get("best_centre"), p_best=o.get("p_best"), correct=(not plain and o["accept"] and o.get("best_centre") == r["centre_id"]),
                        false_accept=(plain and o["accept"]), reason=o.get("reason")))
    with open("outputs/real_photos/results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(res[0])); w.writeheader(); w.writerows(res)
    L = ["# Real-photo results\n"]
    gen = [r for r in res if r["is_plain_control"] != "1"]; pl = [r for r in res if r["is_plain_control"] == "1"]
    L.append(f"Overall: {sum(r['correct'] for r in gen)}/{len(gen)} correct; false accepts on plain controls: {sum(r['false_accept'] for r in pl)}/{len(pl)}\n")
    for fac in ("phone_model", "distance_cm", "angle_deg", "lighting", "whatsapp", "crop_lines", "printer_model"):
        t = defaultdict(lambda: [0, 0])
        for r in gen: t[r[fac]][1] += 1; t[r[fac]][0] += int(r["correct"])
        L.append(f"\n## by {fac}\n| level | correct | 95% CI |\n|---|---|---|")
        for k, (c, n) in sorted(t.items()): lo, hi = wilson(c, n); L.append(f"| {k or '-'} | {c}/{n} | {100*lo:.0f}-{100*hi:.0f}% |")
    open("outputs/real_photos/summary.md", "w").write("\n".join(L)); print("\n".join(L))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--lang", default="en"); ap.add_argument("--centres", type=int, default=10)
    ap.add_argument("--delta", type=float, default=0.30); ap.add_argument("--eps", type=float, default=0.30); ap.add_argument("--labels", default="data/photos/labels.csv")
    a = ap.parse_args(); (pack if a.cmd == "pack" else run)(a)
