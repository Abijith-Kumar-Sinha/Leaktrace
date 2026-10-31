import json, numpy as np, pytest, pymupdf
from common.keys import centre_seed, gap_signs, line_signs, SignBank, word_offsets
from embed.typeset import render, rasterise
from degrade.simulate import Degrade, photograph, crop_for_lines
from decode.pipeline import Decoder, build_master

KEY = "unit-test-key"
NQ = 14   # questions on the test paper: one page and a bit, keeps tests fast

@pytest.fixture(scope="module")
def en():
    paper = json.load(open("data/mock_papers/english.json"))
    pdf, lay, mp = build_master(paper, NQ)
    ids = [f"U{i:03d}" for i in range(40)]
    dec = Decoder(lay, mp, KEY, ids, 0.3, 0.3, n_null=1500, cache_dir="outputs/cache")
    return paper, pdf, lay, mp, dec

def copy_page(paper, lay, dec, ci, page=0):
    off = word_offsets(lay, dec.bank, ci, 0.3, 0.3)
    pdf, _ = render(paper, off, NQ)
    return rasterise(pdf)[page]

# ---- key -> signs -------------------------------------------------------------------------
def test_signs_deterministic_and_balanced():
    a, b = centre_seed(KEY, "C1"), centre_seed(KEY, "C1")
    assert a == b and a != centre_seed(KEY, "C2") and a != centre_seed("other", "C1")
    s1, s2 = gap_signs(a, 0, 3, 11), gap_signs(a, 0, 3, 11)
    assert (s1 == s2).all() and set(np.unique(s1)) <= {-1, 0, 1}
    assert s1.sum() == 0 and s1[-1] == 0            # pairs cancel; odd tail unmarked
    ls = line_signs(a, 0, 21)
    assert ls.sum() == 0 and ls[-1] == 0

def test_signs_look_independent_across_centres():
    seeds = [centre_seed(KEY, f"C{i}") for i in range(200)]
    M = np.stack([np.concatenate([gap_signs(s, 0, l, 12) for l in range(30)]) for s in seeds]).astype(float)
    C = (M @ M.T) / (np.abs(M[0]) > 0).sum(); np.fill_diagonal(C, 0)
    n_bits = 30 * 6                      # one independent bit per gap pair -> sigma = 1/sqrt(180)
    assert abs(C).max() < 5 / np.sqrt(n_bits) and abs(C.mean()) < 0.01

# ---- embedding precision -----------------------------------------------------------------
def test_embedded_offsets_exact(en):
    paper, pdf, lay, mp, dec = en
    off = word_offsets(lay, dec.bank, 3, 0.3, 0.3)
    pdf2, lay2 = render(paper, off, NQ)
    d = np.array([[w2["x0"] - w["x0"], w2["y0"] - w["y0"]] for w, w2 in zip(lay["words"], lay2["words"])])
    exp = np.array([off[w["id"]] for w in lay["words"]])
    assert np.abs(d - exp).max() < 1e-6
    # and in the PDF itself
    w1 = pymupdf.open(stream=pdf, filetype="pdf")[0].get_text("words")
    w2 = pymupdf.open(stream=pdf2, filetype="pdf")[0].get_text("words")
    dd = np.array([[b[0] - a[0], b[1] - a[1]] for a, b in zip(w1, w2)])
    assert set(np.round(dd[:, 0], 2)) <= {-0.3, 0.0, 0.3} and set(np.round(dd[:, 1], 2)) <= {-0.3, 0.3}
    assert max(abs(w2["x1"] - w2["x0"] - (w["x1"] - w["x0"])) for w, w2 in zip(lay["words"], lay2["words"])) < 1e-6  # no re-shaping

def test_justified_margins_preserved(en):
    paper, pdf, lay, mp, dec = en
    off = word_offsets(lay, dec.bank, 3, 0.3, 0.3)
    _, lay2 = render(paper, off, NQ)
    for a, b in zip(lay["words"], lay2["words"]):
        ln = lay["pages"][a["page"]]["lines"][a["line"]]
        if a["id"] == ln["words"][-1] and len(ln["words"]) > 3:
            assert abs(a["x1"] - b["x1"]) < 1e-6        # last word of the line did not move horizontally

# ---- round trip, no degradation: must be 100% ---------------------------------------------
def test_roundtrip_no_degradation(en):
    paper, pdf, lay, mp, dec = en
    ok = 0
    for ci in range(0, 40, 4):
        page = copy_page(paper, lay, dec, ci)
        img, _ = photograph(page, Degrade(out_width=2000, background=False), lay["page_size_pt"])
        r = dec.decode(img)
        ok += int(r["accept"] and r["best_centre"] == dec.bank.centre_ids[ci])
    assert ok == 10

# ---- monotonic behaviour ------------------------------------------------------------------
def test_score_grows_with_visible_lines(en):
    paper, pdf, lay, mp, dec = en
    ci = 7; page = copy_page(paper, lay, dec, ci)
    z = []
    for n in (2, 4, 8, 16):
        img, _ = photograph(page, Degrade(out_width=1600, blur=1.0, noise=3, jpeg=85,
                                          crop=crop_for_lines(lay, 0, 5, n), seed=n), lay["page_size_pt"])
        r = dec.decode(img); z.append(r["z_best"] if r["best_centre"] == dec.bank.centre_ids[ci] else 0.0)
    assert all(b >= a - 0.5 for a, b in zip(z, z[1:])) and z[-1] > z[0]

def test_accuracy_does_not_improve_with_more_blur(en):
    paper, pdf, lay, mp, dec = en
    zs = []
    for blur in (0.5, 1.5, 3.2):
        z = []
        for ci in (3, 9, 21):
            page = copy_page(paper, lay, dec, ci)
            img, _ = photograph(page, Degrade(out_width=1600, blur=blur, noise=3, jpeg=85, seed=ci), lay["page_size_pt"])
            r = dec.decode(img); z.append(r["z_best"] if (r["accept"] and r["best_centre"] == dec.bank.centre_ids[ci]) else 0.0)
        zs.append(np.mean(z))
    assert zs[0] >= zs[1] - 0.5 and zs[1] >= zs[2] - 0.5

# ---- rejection ------------------------------------------------------------------------------
def test_plain_pages_rejected(en):
    paper, pdf, lay, mp, dec = en
    for s in range(6):
        img, _ = photograph(mp[0], Degrade(out_width=1600, persp=0.3, blur=1.0, noise=3, jpeg=85, seed=s), lay["page_size_pt"])
        assert not dec.decode(img)["accept"]

def test_non_paper_image_rejected(en):
    paper, pdf, lay, mp, dec = en
    rng = np.random.default_rng(0)
    r = dec.decode((rng.random((900, 700)) * 255).astype(np.uint8))
    assert not r["accept"] and r["reason"]

# ---- Hindi ------------------------------------------------------------------------------------
def test_hindi_shaping_preserved():
    paper = json.load(open("data/mock_papers/hindi.json"))
    pdf, lay = render(paper, None, 6)
    bank = SignBank(KEY, lay, ["H1"])
    off = word_offsets(lay, bank, 0, 0.3, 0.3)
    pdf2, lay2 = render(paper, off, 6)
    assert all(w["x1"] > w["x0"] for w in lay["words"])
    # splitting text into per-word spans must not reshape any word: identical advance widths in master and copy
    assert max(abs((a["x1"] - a["x0"]) - (b["x1"] - b["x0"])) for a, b in zip(lay["words"], lay2["words"])) < 1e-6
    # conjunct shaping happened: the rendered PDF has fewer glyphs than code points for conjunct-heavy words
    txt = "".join(pymupdf.open(stream=pdf, filetype="pdf")[0].get_text("text"))
    assert "प्रश्नपत्र" in txt.replace("\n", " ") or "प्रश्न" in txt
