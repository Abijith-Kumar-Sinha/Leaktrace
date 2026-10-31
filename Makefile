PY = PYTHONPATH=. python3
.PHONY: setup test e1 study e2 e3 e4 e5 report api web
setup:        ; pip install --break-system-packages -r requirements.txt
test:         ; $(PY) -m pytest -q tests
e1:           ; $(PY) -m eval.e1_visibility
study:        ; $(PY) -m eval.reader_study generate
e2:           ; $(PY) -m eval.e2_identification && $(PY) -m eval.e2_identification analyse
e3:           ; $(PY) -m eval.e3_partial && $(PY) -m eval.e3_partial analyse
e4:           ; $(PY) -m eval.e4_languages && $(PY) -m eval.e4_languages analyse
e5:           ; $(PY) -m eval.e5_attacks && $(PY) -m eval.e5_attacks analyse
api:          ; $(PY) -m uvicorn api.main:app --port 8000
web:          ; cd web && npm install && npm run dev
