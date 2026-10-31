# E4 results - English vs Hindi (delta=eps=0.30 pt, 200 candidate centres)

| condition | English correct & accepted | Hindi correct & accepted | EN top-1 before significance test | HI top-1 before significance test | EN gap-error RMSE | HI gap-error RMSE | EN line-error RMSE | HI line-error RMSE |
|---|---|---|---|---|---|---|---|---|
| nominal phone photo | 12/12 = 100% | 12/12 = 100% | 12/12 | 12/12 | 0.28 | 0.34 | 0.29 | 0.34 |
| blur 2.5 | 12/12 = 100% | 12/12 = 100% | 12/12 | 12/12 | 0.29 | 0.34 | 0.24 | 0.33 |
| jpeg q20 | 12/12 = 100% | 12/12 = 100% | 12/12 | 12/12 | 0.29 | 0.35 | 0.29 | 0.32 |
| width 600 | 12/12 = 100% | 12/12 = 100% | 12/12 | 12/12 | 0.32 | 0.36 | 0.25 | 0.33 |
| hard combined (WhatsApp) | 12/12 = 100% | 12/12 = 100% | 12/12 | 12/12 | 0.32 | 0.35 | 0.28 | 0.33 |
| paper warp 1.0pt | 12/12 = 100% | 12/12 = 100% | 12/12 | 12/12 | 0.69 | 0.70 | 0.75 | 0.62 |
| crop 6 lines | 12/12 = 100% | 12/12 = 100% | 12/12 | 12/12 | 0.28 | 0.39 | 0.59 | 0.60 |
| crop 3 lines | 7/12 = 58% | 0/12 = 0% | 12/12 | 12/12 | 0.32 | 0.55 | 0.83 | 0.84 |

## False accepts on plain pages

- en: 0 accepted of 24
- hi: 0 accepted of 24

## Alignment (OCR anchors) - median RANSAC inliers on page / words on page

- en: median inliers 304 of ~352 words per page
- hi: median inliers 170 of ~363 words per page

## Per-gap measurement error vs width of the narrower neighbouring word (blur sigma 2.0 px photos; error = |r - s_true|)

| narrower word width (pt) | EN mean error | EN n | HI mean error | HI n |
|---|---|---|---|---|
| 0-15 | 0.12 | 1160 | 0.19 | 1022 |
| 15-25 | 0.11 | 510 | 0.16 | 698 |
| 25-40 | 0.09 | 172 | 0.10 | 182 |
| 40-60 | 0.09 | 18 | 0.08 | 10 |
| 60-inf | - | 0 | - | 0 |