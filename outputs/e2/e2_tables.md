# E2 results (English, delta=eps=0.30 pt unless stated, 200 candidate centres)

| condition | n | top-1 correct & accepted | 95% CI | accepted but wrong | rejected | median z | mean positions (gaps/lines) |
|---|---|---|---|---|---|---|---|
| ideal (no degradation) | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 11.7 | 276/26 |
| nominal phone photo | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 14.1 | 302/28 |
| blur 1.5 | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 14.2 | 344/32 |
| blur 2.5 | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 14.0 | 323/30 |
| blur 3.0 | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 14.0 | 302/28 |
| jpeg q40 | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 14.0 | 302/28 |
| jpeg q20 | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 14.0 | 303/28 |
| width 900 | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 11.8 | 276/26 |
| width 600 | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 13.9 | 310/28 |
| perspective 1.0 + rot 8deg | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 14.3 | 368/34 |
| lighting 1.0 | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 14.3 | 341/32 |
| noise 15 | 16 | 15/16 = 94% | 72-99% | 0 | 1 | 9.5 | 252/23 |
| WhatsApp | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 14.3 | 352/32 |
| hard combined (WhatsApp) | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 13.7 | 286/27 |
| print jitter 0.10pt | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 13.1 | 301/28 |
| print jitter 0.20pt | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 11.3 | 326/30 |
| paper warp 0.5pt | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 13.8 | 301/28 |
| paper warp 1.0pt | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 12.9 | 299/28 |
| feed error 0.5pt | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 13.9 | 326/30 |
| physical combined | 16 | 16/16 = 100% | 81-100% | 0 | 0 | 13.1 | 314/29 |

## False-accept rate (alpha = 1e-3 family-wise over 200 centres)

- **PLAIN page**: 0 accepted of 120 (rate 0.0%, 95% CI 0.0-3.1%); median best z = 2.67; failed-to-align = 0
- **valid fingerprint, centre NOT in list**: 0 accepted of 40 (rate 0.0%, 95% CI 0.0-8.8%); median best z = 2.61; failed-to-align = 0

## Channel ablation (same measurements, re-scored) - genuine trials of the 20 quality/physical conditions

| decoder | top-1 correct & accepted | 95% CI | top-1 correct before the significance test | n |
|---|---|---|---|---|
| both | 319/319 = 100% | 99-100% | 319/319 = 100% | 319 |
| gap only | 319/319 = 100% | 99-100% | 319/319 = 100% | 319 |
| line only | 0/319 = 0% | 0-1% | 314/319 = 98% | 319 |

## Offset-size sweep (delta = epsilon)

| delta (pt) | hard full-page: correct | nominal+blur1.5: correct |
|---|---|---|
| 0.05 | 12/12 | 12/12 |
| 0.1 | 12/12 | 12/12 |
| 0.15 | 12/12 | 12/12 |
| 0.2 | 12/12 | 12/12 |
| 0.3 | 12/12 | 12/12 |
| 0.4 | 12/12 | 12/12 |

## Baselines on full-page photos (mark visible; no cropping)

| condition | header-serial read correctly (OCR) | QR code read correctly |
|---|---|---|
| ideal (no degradation) | 12/12 | 12/12 |
| nominal phone photo | 12/12 | 12/12 |
| blur 2.5 | 1/12 | 5/12 |
| jpeg q20 | 12/12 | 12/12 |
| width 600 | 3/12 | 0/12 |
| hard combined (WhatsApp) | 1/12 | 2/12 |
| WhatsApp | 12/12 | 12/12 |