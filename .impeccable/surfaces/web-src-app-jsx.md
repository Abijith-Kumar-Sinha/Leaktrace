---
version: 1
slug: "web-src-app-jsx"
primary_target: "web/src/App.jsx"
related_targets: []
---

# Surface brief: LeakTrace web app (Investigate + Prepare)

Scope: the whole web app in `web/` (Investigate is the lead screen; Prepare, Cases and Audit stubs follow the same system). Visitor mode: **Operate**. Users: exam-board officials (prepare) and investigators (investigate). The public demo is on GitHub Pages, with the backend on a Hugging Face Space (cold starts of 10–30 s).

User decisions (2026-11-13):
- Took the standing exit (the canon, played straight) and asked for "professional and mature for real use and display".
- Then rejected the light canon renders as "bland, AI-generated looking". Asked for **more colours, colour gradients, darker backgrounds**.
- Approved comp-4 "peacock" and asked for it **darker / more colour**, adjusted in code (Figma credits near the cap).

## Direction contract
THESIS: A serious forensic console in which colour carries meaning. Every hue is a role: emerald = agreement, saffron = verdict/action, coral = rejection, lilac = statistics. It refuses the near-black-plus-neon "cyber" console and the bland white SaaS dashboard.
OWN-WORLD: The peacock night. The ground is a deep peacock-blue → midnight-teal diagonal gradient with a faint iridescent sweep, darker than the comp. Panels are solid deep slate-teal with 1px lighter teal hairlines and a 10–12px radius. The verdict tile has a saffron→coral gradient with dark ink. The significant bar has an emerald→saffron gradient. Score bars run teal→emerald. Off-white text in a refined grotesk with tabular numerals. Icons are one stroke family.
STORY: An investigator uploads a leaked photo. In one glance they see the verdict, the centre, the strength of the evidence (p, z, margin), the photo with agreeing words boxed, and the true centre standing far beyond 4000 wrong keys. They trust it because it also says "lead, not proof", and because a rejection looks just as deliberate.
FIRST VIEWPORT: As in comp-4. Left nav (Operations / Governance) with a peacock monogram; top bar with breadcrumb, search and EN|हिन्दी; title row "Investigation · LT-7F3A" with chips and a coral notice at right; 4 KPI tiles (verdict gradient tile first); Evidence panel (photo + overlay) beside Score distribution (histogram + threshold + C0012 bar); Ranked centres table full width.
FORM: Canon (standing exit), the category standard enterprise console, raised by the user's pinned dark peacock palette. Seed key 1b53ba2f, kind canon.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Notes
- Remove anything implying a real government body (no emblems, ministry names).
- Ranked rows below threshold read "Below threshold", never "Not a match".
- The footer tagline "For a fairer tomorrow" is OK; drop the comp's "TRUST EVIDENCE MORE" sub-wordmark (an invented slogan).
