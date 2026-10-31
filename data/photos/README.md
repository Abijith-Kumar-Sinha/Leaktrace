# Real-photo protocol (laser print -> phone photo -> WhatsApp)

This is the part of the study that needs **hardware and people**: it cannot be simulated, and the printer's placement
accuracy and the paper's flatness are the two things most likely to limit the real-world result.
Until these photos exist, every accuracy number in the report is a *simulation* and is labelled as such.

## 1. Print pack
```
export LEAKTRACE_KEY='<your secret key>'
PYTHONPATH=. python3 -m eval.real_photos pack --lang en --centres 10 --delta 0.30 --eps 0.30
```
creates `data/photos/print_pack/` with one PDF per centre (`C0000.pdf` ... `C0009.pdf`), `plain_master.pdf` (negative control)
and `labels_template.csv`.  Centre ids are fixed so the ground truth is known.

## 2. Printing (record everything in labels.csv)
* Laser printer, one printer for the whole batch first, then repeat on a second model if available.
* Print at **100 % / "actual size"** - NEVER "fit to page" (it rescales the layout and the offsets with it). A4, plain 70-80 gsm.
* Print each centre's copy **single-sided**; keep the sheets flat (no folding) until photographed.

## 3. Photographing
For each printed page photograph with **2-3 different phones**, varying:
| factor | levels |
|---|---|
| distance | 25 cm, 40 cm, 60 cm |
| angle | straight on, ~15 deg, ~30 deg |
| lighting | daylight by a window, room tube light, dim + phone flash |
| framing | whole page; and a crop to roughly 3 / 6 / 12 lines (crop in the gallery) |
Take at least **3 photos per (page, phone, condition)**; shoot the plain master pages the same way (negative control).

## 4. WhatsApp
Send a random 50 % of the photos to yourself on WhatsApp ("standard quality", not "HD"), save them back, and put the
received file in `whatsapp/` keeping the same `photo_id` plus suffix `_wa`.

## 5. Folder layout
```
data/photos/
  originals/    P0001.jpg ...            (phone output, unedited)
  whatsapp/     P0001_wa.jpg ...         (after WhatsApp)
  labels.csv    one row per photo (below)
```
`labels.csv` columns:
`photo_id,file,subset,paper_lang,page,centre_id,is_plain_control,printer_model,paper_stock,phone_model,distance_cm,angle_deg,lighting,framing,crop_lines,whatsapp,notes`
(`centre_id` empty for the plain control; `subset` = original|whatsapp; `framing` = full|crop).

## 6. Run the evaluation
```
export LEAKTRACE_KEY='<same key>'
PYTHONPATH=. python3 -m eval.real_photos run --labels data/photos/labels.csv --lang en --centres 200
```
writes `outputs/real_photos/results.csv` and `summary.md`: accuracy and false-accept by phone, distance, angle, lighting,
WhatsApp, crop size, with Wilson 95 % intervals - the real counterpart of E2/E3.

Ethics: photograph only your own mock papers; no personal data is involved.
