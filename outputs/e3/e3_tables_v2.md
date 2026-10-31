# E3 results - partial leaks (English, delta=eps=0.30 pt, 600 dpi print model, 200 candidate centres) - decoder v2 (multi-scale OCR, fresh trials)

## (A) Crop aligned to whole text lines (fingerprint only; header/QR cannot survive such a crop by construction)

| visible lines | quality | n | correct & accepted | 95% CI | top-1 before significance test | median positions used (gaps+lines) | median z |
|---|---|---|---|---|---|---|---|
| 1 | nominal | 14 | 0/14 = 0% | 0-22% | 0/14 | 0 | 0.0 |
| 2 | nominal | 14 | 0/14 = 0% | 0-22% | 12/14 | 23 | 3.2 |
| 3 | nominal | 14 | 2/14 = 14% | 4-40% | 14/14 | 30 | 3.7 |
| 4 | nominal | 14 | 13/14 = 93% | 69-99% | 14/14 | 46 | 4.7 |
| 6 | nominal | 14 | 14/14 = 100% | 78-100% | 14/14 | 70 | 5.7 |
| 8 | nominal | 14 | 14/14 = 100% | 78-100% | 14/14 | 94 | 6.6 |
| 12 | nominal | 14 | 14/14 = 100% | 78-100% | 14/14 | 138 | 8.1 |
| 20 | nominal | 14 | 14/14 = 100% | 78-100% | 14/14 | 233 | 10.5 |
| 1 | hard | 14 | 0/14 = 0% | 0-22% | 1/14 | 0 | 0.0 |
| 2 | hard | 14 | 0/14 = 0% | 0-22% | 4/14 | 6 | 1.9 |
| 3 | hard | 14 | 1/14 = 7% | 1-31% | 3/14 | 6 | 1.8 |
| 4 | hard | 14 | 4/14 = 29% | 12-55% | 6/14 | 18 | 2.8 |
| 6 | hard | 14 | 7/14 = 50% | 27-73% | 9/14 | 57 | 4.8 |
| 8 | hard | 14 | 11/14 = 79% | 52-92% | 12/14 | 100 | 6.6 |
| 12 | hard | 14 | 12/14 = 86% | 60-96% | 12/14 | 147 | 8.2 |
| 20 | hard | 14 | 14/14 = 100% | 78-100% | 14/14 | 214 | 9.9 |

**Smallest crop reaching >= 90% point accuracy:** nominal: 4 line(s); hard: 20 line(s)

## (B) Random rectangular window anywhere on the page, nominal quality (same window, same photo conditions for every method)

| window height (lines) | LeakTrace fingerprint | header serial (OCR) | QR code (single location) |
|---|---|---|---|
| 1 | 0/14 = 0% | 0/0 = 0% | 0/0 = 0% |
| 2 | 0/14 = 0% | 0/0 = 0% | 0/0 = 0% |
| 4 | 5/14 = 36% | 0/0 = 0% | 0/0 = 0% |
| 8 | 8/14 = 57% | 0/0 = 0% | 0/0 = 0% |
| 12 | 11/14 = 79% | 0/0 = 0% | 0/0 = 0% |
| 20 | 12/14 = 86% | 0/0 = 0% | 0/0 = 0% |
| 40 | 14/14 = 100% | 0/0 = 0% | 0/0 = 0% |

## Noise scaling
Empirical log-log fit of the wrong-key score spread sigma(T) against the number of visible positions M over 184 photos: slope = -0.50 (theory: -0.50), R^2 = 0.97.