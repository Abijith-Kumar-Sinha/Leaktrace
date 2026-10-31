import io, json, time, zipfile, numpy as np, cv2, pytest
from fastapi.testclient import TestClient
import os
os.environ["LEAKTRACE_DATA"] = "outputs/test_cases"
from api.main import app
from embed.typeset import rasterise
from degrade.simulate import Degrade, photograph

def test_prepare_then_investigate():
    c = TestClient(app)
    paper = json.load(open("data/mock_papers/english.json")); paper["questions"] = paper["questions"][:10]
    centres = "\n".join(["centre_id"] + [f"K{i:03d}" for i in range(6)])
    r = c.post("/api/prepare", files={"paper": ("p.json", json.dumps(paper)), "centres": ("c.csv", centres)}, data={"key": "api-test-secret-key", "lang": "en"})
    assert r.status_code == 200, r.text
    cid = r.json()["case_id"]
    for _ in range(120):
        s = c.get(f"/api/prepare/{cid}").json()
        if s["state"] != "running": break
        time.sleep(1)
    assert s["state"] == "done", s
    z = zipfile.ZipFile(io.BytesIO(c.get(f"/api/prepare/{cid}/zip").content))
    names = z.namelist(); assert sum(n.startswith("copies/") for n in names) == 6
    page = rasterise(z.read("copies/K004.pdf"))[0]
    img, _ = photograph(page, Degrade(out_width=1600, persp=0.3, blur=1.0, noise=3, jpeg=85, whatsapp=True, seed=5), [595.28, 841.89])
    ok, buf = cv2.imencode(".jpg", img)
    r = c.post("/api/decode", files={"photo": ("leak.jpg", buf.tobytes(), "image/jpeg")}, data={"case_id": cid, "key": "api-test-secret-key"})
    assert r.status_code == 200, r.text
    out = r.json(); res = out["result"]
    assert res["accept"] and res["best_centre"] == "K004" and out["overlay"].startswith("data:image/jpeg")
    assert "NOT PROOF" in out["notice"]
    # wrong key must not identify anybody
    r2 = c.post("/api/decode", files={"photo": ("leak.jpg", buf.tobytes(), "image/jpeg")}, data={"case_id": cid, "key": "another-wrong-secret-key"})
    assert not r2.json()["result"]["accept"]
