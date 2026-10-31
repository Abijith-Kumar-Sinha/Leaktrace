"""E1 (objective half): SSIM / displacement statistics of fingerprinted vs plain pages, English and Hindi.
The human forced-choice half is in eval/reader_study.py (kit + analysis); no human result is invented here."""
import os, json, numpy as np, cv2, csv
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim
from eval.harness import get_env
from common.keys import word_offsets
from embed.typeset import render, rasterise

OUT = "outputs/e1"; os.makedirs(OUT, exist_ok=True)
DELTAS = [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.60, 0.80, 1.00]

def run():
    rows = []
    for lang in ("en", "hi"):
        env = get_env(lang)
        lay = env.layout
        gaps = [lay["words"][b]["x0"] - lay["words"][a]["x1"] for p in lay["pages"] for ln in p["lines"] for a, b in zip(ln["words"][:-1], ln["words"][1:])]
        mean_gap = float(np.mean(gaps))
        master = env.master[1]                       # page 2: dense body text
        textmask = np.zeros(master.shape, bool)
        for ln in lay["pages"][1]["lines"]:
            textmask[int(ln["y0"] * 4):int(ln["y1"] * 4), :] = True
        for d in DELTAS:
            off = word_offsets(lay, env.bank, 0, d, d)
            pdf, _ = render(env.paper, off); pg = rasterise(pdf)[1]
            s_full, smap = ssim(master, pg, data_range=255, full=True)
            s_text = float(smap[textmask].mean())
            changed = float((np.abs(master.astype(int) - pg.astype(int)) > 16).mean() / max(textmask.mean(), 1e-9))
            rows.append(dict(lang=lang, delta_pt=d, delta_pct_of_mean_word_gap=100 * d / mean_gap, mean_word_gap_pt=mean_gap,
                             max_word_shift_pt=d, ssim_page=s_full, ssim_text_lines=s_text, pct_text_pixels_changed=100 * changed))
            print(lang, d, round(s_full, 4), round(s_text, 4), flush=True)
        # magnified difference figure for the report (delta = 0.3)
        off = word_offsets(lay, env.bank, 0, 0.3, 0.3); pdf, _ = render(env.paper, off); pg = rasterise(pdf)[1]
        y0 = int(lay["pages"][1]["lines"][6]["y0"] * 4) - 20; y1 = y0 + 330
        crop_m, crop_c = master[y0:y1, 150:1500], pg[y0:y1, 150:1500]
        diff = np.clip(128 + (crop_c.astype(int) - crop_m.astype(int)) * 1.0, 0, 255).astype(np.uint8)
        cv2.imwrite(f"{OUT}/fig_{lang}_plain_fingerprinted_diff.png", np.vstack([crop_m, crop_c, diff]))
    with open(f"{OUT}/e1_objective.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    for lang, c in (("en", "#2b6cb0"), ("hi", "#c05621")):
        r = [x for x in rows if x["lang"] == lang]
        ax[0].plot([x["delta_pt"] for x in r], [x["ssim_text_lines"] for x in r], "o-", color=c, label={"en": "English", "hi": "Hindi"}[lang])
        ax[1].plot([x["delta_pt"] for x in r], [x["pct_text_pixels_changed"] for x in r], "o-", color=c)
    ax[0].set_xlabel("offset delta = epsilon (pt)"); ax[0].set_ylabel("SSIM, text-line regions"); ax[0].legend(); ax[0].set_title("Structural similarity to plain page")
    ax[1].set_xlabel("offset delta = epsilon (pt)"); ax[1].set_ylabel("% of text-line pixels changed (>16 levels)"); ax[1].set_title("Pixels changed")
    for a in ax: a.grid(alpha=.3)
    plt.tight_layout(); plt.savefig(f"{OUT}/e1_ssim.png", dpi=160)
    return rows

if __name__ == "__main__":
    run()
