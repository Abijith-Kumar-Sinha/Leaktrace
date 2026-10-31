# E3 results - partial leaks (English, delta=eps=0.30 pt, 600 dpi print model, 200 candidate centres) - decoder v1.1 (rotation-loop bug fixed)

## (A) Crop aligned to whole text lines (fingerprint only; header/QR cannot survive such a crop by construction)

| visible lines | quality | n | correct & accepted | 95% CI | top-1 before significance test | median positions used (gaps+lines) | median z |
|---|---|---|---|---|---|---|---|
| 1 | nominal | 14 | 0/14 = 0% | 0-22% | 0/14 | 0 | 0.0 |
| 2 | nominal | 14 | 0/14 = 0% | 0-22% | 10/14 | 22 | 3.1 |
| 3 | nominal | 14 | 4/14 = 29% | 12-55% | 14/14 | 34 | 4.0 |
| 4 | nominal | 14 | 12/14 = 86% | 60-96% | 14/14 | 46 | 4.7 |
| 6 | nominal | 14 | 14/14 = 100% | 78-100% | 14/14 | 71 | 5.8 |
| 8 | nominal | 14 | 14/14 = 100% | 78-100% | 14/14 | 93 | 6.7 |
| 12 | nominal | 14 | 14/14 = 100% | 78-100% | 14/14 | 142 | 8.2 |
| 20 | nominal | 14 | 14/14 = 100% | 78-100% | 14/14 | 232 | 10.4 |
| 1 | hard | 14 | 0/14 = 0% | 0-22% | 0/14 | 0 | 0.0 |
| 2 | hard | 14 | 0/14 = 0% | 0-22% | 1/14 | 0 | 0.0 |
| 3 | hard | 14 | 0/14 = 0% | 0-22% | 1/14 | 6 | 1.4 |
| 4 | hard | 14 | 5/14 = 36% | 16-61% | 6/14 | 8 | 2.2 |
| 6 | hard | 14 | 8/14 = 57% | 33-79% | 8/14 | 73 | 4.8 |
| 8 | hard | 14 | 10/14 = 71% | 45-88% | 10/14 | 94 | 6.5 |
| 12 | hard | 14 | 12/14 = 86% | 60-96% | 14/14 | 138 | 7.4 |
| 20 | hard | 14 | 14/14 = 100% | 78-100% | 14/14 | 204 | 9.4 |

**Smallest crop reaching >= 90% point accuracy:** nominal: 6 line(s); hard: 20 line(s)

## (B) Random rectangular window anywhere on the page, nominal quality (same window, same photo conditions for every method)

| window height (lines) | LeakTrace fingerprint | header serial (OCR) | QR code (single location) |
|---|---|---|---|
| 1 | 0/14 = 0% | 0/14 = 0% | 0/14 = 0% |
| 2 | 0/14 = 0% | 1/14 = 7% | 1/14 = 7% |
| 4 | 0/14 = 0% | 1/14 = 7% | 1/14 = 7% |
| 8 | 13/14 = 93% | 0/14 = 0% | 0/14 = 0% |
| 12 | 11/14 = 79% | 1/14 = 7% | 0/14 = 0% |
| 20 | 13/14 = 93% | 1/14 = 7% | 2/14 = 14% |
| 40 | 14/14 = 100% | 4/14 = 29% | 1/14 = 7% |

## Noise scaling
Empirical log-log fit of the wrong-key score spread sigma(T) against the number of visible positions M over 173 photos: slope = -0.48 (theory: -0.50), R^2 = 0.94.