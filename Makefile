PY = PYTHONPATH=. python3
.PHONY: setup test e1 study e2 e2b e3 e3v2 e4 e5 report api web
setup:        ; pip install --break-system-packages -r requirements.txt
test:         ; $(PY) -m pytest -q tests
e1:           ; $(PY) -m eval.e1_visibility
study:        ; $(PY) -m eval.reader_study generate
e2:           ; $(PY) -m eval.e2_identification && $(PY) -m eval.e2_identification analyse
e3:           ; $(PY) -m eval.e3_partial && $(PY) -m eval.e3_partial analyse
e4:           ; $(PY) -m eval.e4_languages && $(PY) -m eval.e4_languages analyse
e2b:          ; $(PY) -m eval.e2b_printer && $(PY) -m eval.e2b_printer analyse
e5:           ; $(PY) -m eval.e5_attacks && $(PY) -m eval.e5_attacks analyse && $(PY) -m eval.e5_rotation_v2 && $(PY) -m eval.e5_rotation_v2 analyse
e3v2:         ; $(PY) -m eval.e3_partial --v2 && $(PY) -m eval.e3_partial analyse --v2
api:          ; $(PY) -m uvicorn api.main:app --port 8000
web:          ; cd web && npm install && npm run dev
report:       ; $(PY) docs/build_report.py
