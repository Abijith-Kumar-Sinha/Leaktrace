# E3 results - partial leaks (English, delta=eps=0.30 pt, 200 candidate centres)

## (A) Crop aligned to whole text lines (fingerprint only; header/QR cannot survive such a crop by construction)

| visible lines | quality | n | correct & accepted | 95% CI | median positions used (gaps+lines) | median z |
|---|---|---|---|---|---|---|
| 1 | nominal | 14 | 0/14 = 0% | 0-22% | 0 | 0.0 |
| 2 | nominal | 14 | 0/14 = 0% | 0-22% | 22 | 3.1 |
| 3 | nominal | 14 | 4/14 = 29% | 12-55% | 34 | 4.0 |
| 4 | nominal | 14 | 12/14 = 86% | 60-96% | 46 | 4.7 |
| 6 | nominal | 14 | 14/14 = 100% | 78-100% | 71 | 5.8 |
| 8 | nominal | 14 | 14/14 = 100% | 78-100% | 93 | 6.7 |
| 12 | nominal | 14 | 14/14 = 100% | 78-100% | 142 | 8.2 |
| 20 | nominal | 14 | 14/14 = 100% | 78-100% | 232 | 10.4 |
| 1 | hard | 14 | 0/14 = 0% | 0-22% | 0 | 0.0 |
| 2 | hard | 14 | 0/14 = 0% | 0-22% | 0 | 0.0 |
| 3 | hard | 14 | 0/14 = 0% | 0-22% | 0 | 0.0 |
| 4 | hard | 14 | 1/14 = 7% | 1-31% | 0 | 0.0 |
| 6 | hard | 14 | 2/14 = 14% | 4-40% | 0 | 0.0 |
| 8 | hard | 14 | 8/14 = 57% | 33-79% | 92 | 6.0 |
| 12 | hard | 14 | 10/14 = 71% | 45-88% | 138 | 7.2 |
| 20 | hard | 14 | 12/14 = 86% | 60-96% | 196 | 9.3 |

**Smallest crop reaching >= 90% point accuracy:** nominal: 6 line(s); hard: none of the tested sizes

## (B) Random rectangular window anywhere on the page, hard quality (same window, same photo conditions for every method)

| window height (lines) | LeakTrace fingerprint | header serial (OCR) | QR code (single location) |
|---|---|---|---|
| 1 | 0/14 = 0% | 0/14 = 0% | 0/14 = 0% |
| 2 | 0/14 = 0% | 0/14 = 0% | 0/14 = 0% |
| 4 | 0/14 = 0% | 0/14 = 0% | 0/14 = 0% |
| 8 | 8/14 = 57% | 0/14 = 0% | 0/14 = 0% |
| 12 | 10/14 = 71% | 0/14 = 0% | 0/14 = 0% |
| 20 | 13/14 = 93% | 0/14 = 0% | 0/14 = 0% |
| 40 | 14/14 = 100% | 0/14 = 0% | 0/14 = 0% |

## Noise scaling
Empirical log-log fit of the wrong-key score spread sigma(T) against the number of visible positions M over 139 photos: slope = -0.47 (theory: -0.50), R^2 = 0.95.