# LeakTrace

Invisible per-centre fingerprints for printed exam papers (tiny word-gap and line-position shifts), and a
deterministic decoder that takes a **photo** of a leaked paper — cropped, blurred, resized, JPEG/WhatsApp-compressed —
and reports which centre's copy it most probably came from, **with a significance level, or rejects the photo**.

> **LeakTrace is an investigative-lead tool. It does not prove who leaked a paper.** A retyped paper carries no
> fingerprint (tested in E5). Every result below that comes from the simulator is labelled as simulation.

SDG 4 (Quality Education). English and Hindi (Devanagari). Mock papers only (`data/mock_papers/`, written by us).

## Live demo
- **Web app:** https://abijith-kumar-sinha.github.io/Leaktrace/ (add `?lang=hi` after the route for the Hindi UI, e.g. `#/investigate?lang=hi`).
- **Decoder API:** a Hugging Face Docker Space built from `deploy/hf-space/`. The Space clones this repo, so it only needs the
  `Dockerfile` and `README.md` from that folder. The free Space sleeps when idle, so the first request after a pause can take up to a minute.
- **Try it:** Prepare paper → download the sample paper and the 200-centre list from the links on that page → enter a key of
  12 or more characters → download the ZIP → print or screenshot one centre's PDF → photograph it → Investigate.
- The GitHub Pages build reads the API URL from the repository variable `LEAKTRACE_API`.

## How it works (one paragraph)
`embed/` typesets the master with WeasyPrint/HarfBuzz, one CSS span per word. A centre's copy is the *same* HTML with
`position:relative` offsets: gaps are grouped in pairs `(+s,-s)` (one word moves by ±δ, line width and justified margins
are unchanged), lines are grouped in pairs `(+s,-s)` moved vertically by ±ε. Signs come from
`HMAC-SHA256(secret key, centre id)`. `decode/` flattens illumination, finds words with Tesseract (OCR is used **only** to
locate words), matches them to the master by sequence alignment, fits a homography with RANSAC, then measures every word's
sub-pixel displacement against the master raster with ECC. Score `T(c) = Σ q_j s_j(c) r_j / Σ q_j`; the p-value comes from the
empirical distribution of the same statistic under 4000 **wrong keys**, Bonferroni-corrected over the candidate centres. If
that is not significant the photo is **rejected**.

## Run it (one command per stage, from this folder)
```
make setup          # pinned dependencies (Python 3.11+; needs tesseract with eng + hin, and WeasyPrint's pango)
make test           # unit tests (determinism, exact embedding, round trip 100 %, monotonicity, rejection, Hindi shaping, API)
make e1             # E1 objective half: SSIM / pixel-change vs offset size           -> outputs/e1/
make study          # E1 human half: build the forced-choice reader-study kit          -> outputs/e1/reader_study/
make e2             # E2 full-page identification, false-accept rate, ablation, baselines  -> outputs/e2/
python -m eval.e2b_printer && python -m eval.e2b_printer analyse    # offset size x printer dpi
make e3             # E3 partial leaks (add --v2 for the multi-scale-OCR decoder)      -> outputs/e3/
make e4             # E4 English vs Hindi                                              -> outputs/e4/
make e5             # E5 attacks (rescale, rotation, collusion, noise injection, retyping) -> outputs/e5/
make api            # FastAPI on :8000        make web   # React UI on :5173 (proxies /api)
python docs/build_report.py     # final report PDF -> docs/LeakTrace_report.pdf
```
All experiments use fixed seeds (`common/config.py: SEED`), a key different from the one used while developing, and write
raw per-trial results as `*.jsonl` next to the tables/plots, so every number in the report can be re-derived.

## Layout
```
embed/      typesetting + fingerprint embedding        decode/   OCR anchors, alignment, measurement, scoring, overlay
degrade/    photo simulator + post-capture attacks     eval/     experiments E1–E5, baselines, real-photo evaluator
common/     keys (HMAC signs) + constants              api/      FastAPI (prepare / decode)      web/   React UI
data/mock_papers/  English + Hindi mock papers         data/photos/  real-photo protocol + labels template
tests/      pytest                                     docs/     report + notes
```

## Using the app
* **Paper preparation:** upload the paper (our JSON, or a .txt with blank-line-separated paragraphs), a centre list (one id per
  line, ≤ 5000), a secret key (≥ 12 chars) → ZIP with one PDF per centre. The key is used in memory only.
* **Investigation:** pick the case, enter the same key, upload the photo → ranked centres, confidence, accept/reject, an overlay of
  the decoded spacing changes on the photo, and the “investigative lead, not proof” notice.

## Honest limits (see the report for numbers)
Paper source must be typeset by LeakTrace (arbitrary PDFs cannot be re-flowed); a photo with fewer than ~4 text lines is
below the significance floor at α = 10⁻³ over 200 centres; retyping removes the mark; the physical channel (printer placement
error, paper curl, lens distortion, motion blur) is only *modelled* until the real-photo protocol in `data/photos/README.md`
has been carried out; and the offset size must be fixed by the human reader study (E1), which this repository supports but
cannot perform.
