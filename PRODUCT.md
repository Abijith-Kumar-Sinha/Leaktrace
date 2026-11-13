# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
- **Exam-board official (primary):** before an exam, prepares the question paper and produces one invisibly fingerprinted PDF per exam centre. Works at a desk under time pressure and confidentiality; the secret key and the unmarked master must never leave their hands.
- **Investigator (primary):** after a paper leaks, has a phone photo of it, often cropped, tilted and WhatsApp-compressed. Needs to learn which centre's printed copy it came from, how strong the evidence is, and when the tool refuses to say.
- **Secondary:** SDG 4 project evaluators (RVCE teachers) see the public demo, but the interface is designed as the real tool, not a showcase.

## Product Purpose
LeakTrace traces a leaked exam paper back to the centre that printed it. It does this through keyed, sub-millimetre word-gap and line shifts that are repeated on every line, plus a deterministic decoder. Success means the right centre is named with a calibrated p-value, and nothing is named when the evidence is insufficient: zero wrong accusations matters more than coverage. SDG 4 framing: fair, merit-based access to education (targets 4.3, 4.5, 4.1).

## Positioning
Visible QR codes and serial numbers are what Indian boards use today, and both can be cropped out. LeakTrace's mark is invisible, survives a crop down to about 4 lines, and every accusation is backed by a wrong-key significance test that can **reject**. It is classical, keyed and interpretable, not a black-box model.

## Operating Context
- Prepare: upload the paper (JSON, or .txt with blank-line-separated questions), a centre list (≤5000) and a secret key (≥12 characters), with δ/ε offsets → background job → ZIP of per-centre PDFs plus the unmarked master.
- Investigate: choose a case, enter the same key, upload a photo → ranked centres, confidence, p-value, z, margin, accept/reject with the reason, an overlay of the decoded shifts on the photo, and the candidate set when collusion is possible.
- The backend is a Python FastAPI service (Tesseract, WeasyPrint, OpenCV). The public demo runs its frontend on GitHub Pages and its backend on a Hugging Face Space, which may be asleep or slow (10–30 s per decode).
- The demo starts **empty**: no preloaded case or public key. Visitors prepare a case first, as in the real workflow.

## Capabilities and Constraints
- Papers in English and Hindi (Devanagari). **The UI has an English/Hindi language toggle.**
- The output is an **investigative lead, not proof**. This notice must always be visible next to any result.
- A retyped paper carries no fingerprint; such photos are rejected.
- The key is used in memory only and is never stored by the server.
- All accuracy figures to date come from simulation. The real print-and-photo study and the human reader study have not been run, so no UI copy may claim real-world accuracy.

## Brand Commitments
- Name: **LeakTrace**. No logo exists yet.
- The fixed notice wording "Investigative lead — not proof" (and its full disclaimer) must be kept.

## Evidence on Hand
- Simulated results in `outputs/*/…_tables.md`, a report at `docs/LeakTrace_report.pdf`, and figures in `docs/figs/` (a simulated leaked photo, an overlay).
- No real deployments, users, testimonials or field results exist. Do not fabricate any.

## Product Principles
1. Refusing beats guessing: a rejection is a first-class, dignified result, not an error.
2. Show the evidence, not just the verdict: always show the p-value, the margin, the positions used and the overlay.
3. Secrets stay with the official: the key and the master are visibly handled as confidential.
4. Bilingual by default: Hindi is a first-class citizen in both papers and interface.

## Accessibility & Inclusion
- An English/Hindi interface with a Devanagari-capable font stack.
- Results must not rely on colour alone (accept/reject also needs text and an icon).
