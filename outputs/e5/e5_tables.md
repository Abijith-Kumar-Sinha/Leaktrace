# E5 results - attacks (English, delta=eps=0.30 pt, 200 candidate centres)

## (a) Post-capture transformations of a nominal photo

| attack | n | correct & accepted | 95% CI | rejected as unreadable/no-fingerprint |
|---|---|---|---|---|
| rotate 10 | 12 | 12/12 = 100% | 76-100% | 0 |
| rotate 30 | 12 | 0/12 = 0% | 0-24% | 12 |
| rot90 90 | 12 | 12/12 = 100% | 76-100% | 0 |
| rot90 180 | 12 | 12/12 = 100% | 76-100% | 0 |
| rescale 0.35 | 12 | 12/12 = 100% | 76-100% | 0 |
| rescale 0.2 | 12 | 12/12 = 100% | 76-100% | 0 |
| jpeg 15 | 12 | 12/12 = 100% | 76-100% | 0 |
| median 3 | 12 | 12/12 = 100% | 76-100% | 0 |
| unsharp 2.0 | 12 | 12/12 = 100% | 76-100% | 0 |
| contrast 0.5 | 12 | 12/12 = 100% | 76-100% | 0 |

## (b) Collusion (colluders' copies averaged position-wise, or mixed line-by-line)

Candidate set = centres whose score is significant at family-wise alpha=1e-3 (Bonferroni over 200 centres, up to 6 reported).
A looser *lead* set uses z>=3.5 (about 5% family-wise) on the same scores.

| scenario | n | all colluders in strict set | >=1 colluder in strict set | innocents in strict set (mean) | all colluders in lead set (z>=3.5) | innocents in lead set (mean) | top-1 is a colluder |
|---|---|---|---|---|---|---|---|
| 2 colluders, avg | 12 | 12/12 | 12/12 | 0.00 | 12/12 | 0.08 | 12/12 |
| 2 colluders, mix | 12 | 8/12 | 12/12 | 0.00 | 10/12 | 0.08 | 12/12 |
| 3 colluders, avg | 12 | 10/12 | 12/12 | 0.00 | 12/12 | 0.08 | 12/12 |
| 3 colluders, mix | 12 | 1/12 | 11/12 | 0.00 | 4/12 | 0.00 | 12/12 |

## (c) Adversary adds random per-word displacement (noise injection)

| added jitter sigma | n | correct & accepted | 95% CI |
|---|---|---|---|
| 0.1 pt | 12 | 12/12 = 100% | 76-100% |
| 0.2 pt | 12 | 12/12 = 100% | 76-100% |
| 0.4 pt | 12 | 12/12 = 100% | 76-100% |
| 0.8 pt | 12 | 1/12 = 8% | 1-35% |

## (d) Retyping - DOCUMENTED LIMIT: the fingerprint lives in the layout, not in the words

- Retyped text, same template/fonts (no offsets): 0 accepted of 12 -> correctly **rejected** (no fingerprint survives; the lead is lost, not misattributed).
- Retyped with a different font size / line height: 0 accepted of 9; 0 failed to align to the master; the rest were rejected as not significant.