---
name: LeakTrace
description: A forensic console for tracing a leaked exam paper to its printing centre; colour carries meaning.
colors:
  ground-deep: "#021A22"
  ground-mid: "#032A33"
  ground-blue: "#04263A"
  panel: "#08303D"
  panel-raised: "#0A3948"
  panel-high: "#0D4556"
  ink: "#E8F0F2"
  ink-muted: "#A3BCC6"
  ink-faint: "#7795A2"
  dark-ink: "#0F1419"
  saffron: "#FFB547"
  amber: "#FF9446"
  coral: "#F2674F"
  coral-ink: "#FF8E7A"
  emerald: "#14C79A"
  teal: "#1FA9A0"
  peacock: "#1E6FB5"
  lilac: "#B7A8FF"
typography:
  display:
    fontFamily: "Oxygen, Mukta, Noto Sans Devanagari, system-ui, sans-serif"
    fontSize: "29px"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  numeral:
    fontFamily: "Oxygen, Mukta, Noto Sans Devanagari, system-ui, sans-serif"
    fontSize: "35px"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.01em"
    fontFeature: "tnum"
  headline:
    fontFamily: "Oxygen, Mukta, Noto Sans Devanagari, system-ui, sans-serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: 1.15
  body:
    fontFamily: "Oxygen, Mukta, Noto Sans Devanagari, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Oxygen, Mukta, Noto Sans Devanagari, system-ui, sans-serif"
    fontSize: "15.5px"
    fontWeight: 400
    lineHeight: 1.5
  mono:
    fontFamily: "Inconsolata, Mukta, ui-monospace, monospace"
    fontSize: "19px"
    fontWeight: 700
rounded:
  sm: "6px"
  md: "9px"
  button: "10px"
  panel: "12px"
  pill: "99px"
spacing:
  tight: "10px"
  panel: "16px"
  section: "19px"
  gutter: "22px"
components:
  button-primary:
    backgroundColor: "{colors.saffron}"
    textColor: "{colors.dark-ink}"
    rounded: "{rounded.button}"
    padding: "0 22px"
    height: "46px"
  button-ghost:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.button}"
    padding: "0 22px"
    height: "46px"
  button-ghost-hover:
    backgroundColor: "{colors.panel-high}"
  button-small:
    rounded: "{rounded.button}"
    padding: "0 14px"
    height: "34px"
  input:
    backgroundColor: "{colors.ground-deep}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "0 12px"
    height: "44px"
  panel:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "14px 16px"
  verdict-accept:
    backgroundColor: "{colors.saffron}"
    textColor: "{colors.dark-ink}"
    rounded: "{rounded.panel}"
    padding: "14px 20px"
  pill:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink-muted}"
    rounded: "{rounded.pill}"
    padding: "0 12px"
  pill-significant:
    backgroundColor: "{colors.saffron}"
    textColor: "{colors.dark-ink}"
    rounded: "{rounded.pill}"
    padding: "0 12px"
  notice:
    textColor: "{colors.coral-ink}"
    rounded: "{rounded.md}"
    padding: "8px 18px"
---

# Design System: LeakTrace

## Overview

**Creative North Star: "The Peacock Night"**

A serious forensic console in which every hue is a role. The ground is a deep peacock-blue to midnight-teal diagonal with three faint radial washes (teal top right, violet bottom left, ocean blue centre) fixed behind the page. Panels sit on it as solid deep slate-teal slabs with a hairline that shifts from teal to lilac around the corner. The screen reads like an instrument, not a marketing page: dense, numeric, labelled in plain language.

Colour is never decoration. Emerald means agreement, the saffron-to-coral sweep means a verdict or the primary action, coral means rejection and the "not proof" notice, lilac means statistics, and a muted neutral teal means "below threshold". A rejection is drawn with the same care as an accept: a slate verdict tile, a coral cross, a hatched evidence placeholder with a plain sentence.

The system refuses the near-black-plus-neon "cyber" console and the bland white SaaS dashboard. It is dark by commitment (`color-scheme: dark`); there is no light theme.

**Key Characteristics:**
- Dark peacock gradient ground, fixed; deep slate-teal panels with iridescent hairlines.
- Colour carries meaning; meaning never relies on colour alone (every verdict has an icon and words).
- One sans (Oxygen) for everything, tabular numerals, Mukta for Devanagari.
- Hindi is first class: the same layout carries both languages.
- One authored motion moment: the result arrives, and the true centre's bar climbs out of the noise.

## Colors

A cool, saturated dark palette (blue-teal ground) with four warm-and-cool signal hues, each bound to one meaning.

### Primary
- **Verdict Saffron** (saffron): the start of the verdict sweep, focus rings, caret, selection, links, active nav icon, list markers, the significant centre's histogram label. Always means "verdict" or "act".
- **Ember Amber** (amber) and **Signal Coral** (coral): the middle and end of the saffron-to-coral sweep on the accept verdict tile (`#FFCB5C → #FFA548 → #F57A50 → #F2674F`) and the primary button (`#FFCB5C → #FFA548 → #F7834E`).

### Secondary
- **Signal Coral** (coral) and **Coral Ink** (coral-ink): rejection and warning. The "Investigative lead, not proof" notice, the threshold line in the histogram and the threshold tick in score bars, the reject verdict icon, error text, the server-down banner, the short-key warning. Coral Ink is the text-legible tint on dark.

### Tertiary
- **Agreement Emerald** (emerald) with **Lagoon Teal** (teal): agreement. Score bars run teal → emerald (`#1FA9A0 → #14C79A → #5BD88F`); the significant row's bar runs on into saffron (`… #9BDC6A → #FFC24D`), as does the histogram hit bar (`#14C79A → #7BD36A → #FFB547`). A filled dropzone turns emerald. Teal is also the dropzone and sample-link colour at rest, and the "waking server" banner.
- **Statistics Lilac** (lilac): statistics only. The z · margin KPI value and the wrong-key null distribution (`#B7A6FF → #6F5FD0`).
- **Peacock Blue** (peacock): atmosphere, not signal. The p-value KPI tint and the cool end of the active-nav wash.

### Neutral
- **Abyss** (ground-deep), **Midnight Teal** (ground-mid), **Peacock Dusk** (ground-blue): the three stops of the 135° page gradient.
- **Slate Teal** (panel), **Raised Slate** (panel-raised), **High Slate** (panel-high): panel body gradient (raised → panel, top to bottom), KPI tiles (high → panel), ghost-button hover.
- **Paper Ink** (ink): primary text. **Mist** (ink-muted): labels, secondary text, axis ticks. **Fog** (ink-faint): hints, separators, footnotes.
- **Dark Ink** (dark-ink): text on saffron (verdict tile, primary button, significant pill) and the verdict icon disc.
- **Below-threshold Teal** (`#1E6E7A → #2A8C93`): the muted bar of every non-significant row.
- **Hairlines**: `rgba(122,196,214,.16)` for panel borders and dividers, `.28` for controls, chips and pills.

### Named Rules
**The One Meaning Rule.** Each signal hue has exactly one job. Saffron means verdict or action, emerald means agreement, coral means rejection or caution, lilac means statistics. If a new element needs a colour, it takes the colour of its meaning or stays neutral.

**The Never Colour Alone Rule.** Accept and reject always show an icon (check or cross) and words alongside the colour. Pills carry "Significant" or "Below threshold" text.

**The Dignified Refusal Rule.** A non-match is "Below threshold" in neutral teal, never "Not a match" in red. A rejected verdict is a slate tile with a coral cross; it is not an error state.

## Typography

**Display Font:** Oxygen (with Mukta, Noto Sans Devanagari, system-ui)
**Body Font:** Oxygen (same stack)
**Label/Mono Font:** Inconsolata (used only for the generated case ID)
**Devanagari:** Mukta, applied by `:lang(hi)`.

**Character:** A plain, slightly rounded grotesk that reads as a tool, not a brand. Numbers are tabular so columns of p-values and z-scores align.

### Hierarchy
- **Display** (700, 29px, 1.15; 24px under 560px): the page title, e.g. "Investigation · LT-7F3A".
- **Numeral** (700, 35px, 1.1, tabular): KPI values. Scientific notation keeps a real superscript exponent and a lighter `×`.
- **Headline** (700, 20px, 1.15): panel titles.
- **Verdict** (700, 24px accept / 21px reject): the verdict tile's heading.
- **Body** (400, 16px, 1.5): tables and running text; intros cap at 72ch.
- **Label** (400, 15–15.5px): chips, pills, sub-headings, field labels; hints at 13.5–14px in Fog.
- **Mono** (Inconsolata 700, 19px): the case ID shown after a prepare job, the one string the official must copy exactly.

### Named Rules
**The Tabular Rule.** Every number that can be compared (scores, p-values, counts) uses `font-variant-numeric: tabular-nums`.

**The One Family Rule.** One sans for display, body and numerals. Do not introduce a display face.

## Layout

An app shell: a 260px sticky left rail (brand, two nav groups "Operations" and "Governance", a footer line), a 62px sticky top bar (breadcrumb, search, EN | हिन्दी, avatar) with a translucent blurred background, and a content column capped at 1640px with a 19px vertical rhythm between blocks and 21–22px side gutters.

The Investigate result is a fixed reading order: a title row (title, chips, and the coral notice pushed right), four KPI tiles (`1.13fr 1fr 1fr 1fr`, 18px gap, verdict first), an evidence panel beside the score distribution (`595fr 619fr`), then the ranked table full width. Forms sit in a single panel capped at 1080px, with a two-column field grid (four columns for key / language / δ / ε).

Breakpoints: at 1280px the notice wraps to its own line; at 1100px evidence and distribution stack and the four-field row goes to two; at 900px the rail becomes an off-canvas drawer (300px, slides with `cubic-bezier(.16,1,.3,1)`), search and avatar hide, and KPIs go two-up; at 560px everything is one column, the score-bar column and rank column hide, pills switch to short labels, and chart text is scaled up so it stays legible inside the scaled SVG.

## Elevation & Depth

A hybrid system: tonal layering does most of the work (ground → panel → high slate), with one soft ambient shadow under every panel and tile and a coloured glow only under saffron elements.

### Shadow Vocabulary
- **Panel ambient** (`box-shadow: 0 1px 0 rgba(255,255,255,.04) inset, 0 18px 40px -22px rgba(0,0,0,.65)`): every panel and KPI tile.
- **Verdict glow** (`box-shadow: 0 22px 48px -24px rgba(255,140,60,.7)`): the accept verdict tile only.
- **Primary glow** (`box-shadow: 0 14px 30px -16px rgba(255,150,60,.8)`): the primary button.
- **Drawer** (`box-shadow: 30px 0 60px -20px rgba(0,0,0,.7)`): the mobile nav drawer.

### Named Rules
**The Warm Light Rule.** Only saffron elements glow. Everything else is lit by tone and a soft dark shadow.

**The Iridescent Hairline Rule.** Panels and non-verdict KPI tiles carry a 1px masked gradient border (`rgba(64,224,196,.55)` → peacock → `rgba(170,140,255,.45)` at 135°): teal at the top left fading to lilac at the bottom right. This is the world's signature; the verdict tile does not get it.

## Shapes

Gently rounded and consistent. Panels and tiles 12px; buttons 10px; inputs, nav items, the notice and the evidence frame 9px; focus outlines and the language toggle 6px; chips, pills and bars fully round (99px). Borders are 1px hairlines; the dropzone is a 1.5px dashed hairline that turns solid emerald once filled. Empty states use a 135° hatched stripe (`rgba(122,196,214,.05)` 10px bands). The verdict icon is a 54px disc.

## Components

### Buttons
Confident and warm for the one action that matters; quiet otherwise.
- **Shape:** gently rounded (10px), 46px tall, 700 weight, 9px icon gap.
- **Primary:** the saffron sweep (`linear-gradient(100deg, #FFCB5C, #FFA548 60%, #F7834E)`) with dark ink and the primary glow. One per form.
- **Hover / Focus:** primary brightens (`brightness(1.06)`) and lifts 1px; ghost fills with High Slate. Focus is a 2px saffron outline offset 2px.
- **Disabled primary:** loses the sweep entirely, becoming a dim slate (`rgba(4,30,38,.6)`) with Fog text, so an unready action never looks ready.
- **Ghost / Small:** translucent slate with a control hairline; small is 34px.

### Chips
- **Style:** 37px, fully round, control hairline, translucent slate, 15.5px. Facts about the case (centre count, language), not filters.

### Pills (status)
- **Below threshold:** translucent slate, hairline, Mist text.
- **Significant:** saffron→amber gradient fill, dark ink, 700. Only ever on the accepted centre.

### Cards / Containers
- **Corner Style:** 12px.
- **Background:** Raised Slate → Slate Teal top-to-bottom; KPI tiles High Slate → Slate Teal at 160°, each tinted by its meaning (emerald source, peacock p-value, violet statistics).
- **Shadow Strategy:** panel ambient plus the iridescent hairline.
- **Internal Padding:** 14px 16px (panels), 14px 20px (tiles), 24px 26px (forms).

### Inputs / Fields
- **Style:** 44px, 9px radius, control hairline, deep translucent fill (`rgba(4,18,27,.6)`), label above in Paper Ink at 15px, hint below in Fog.
- **Focus:** border turns saffron; the caret is saffron.
- **Error:** hint turns Coral Ink; form errors are a Coral Ink line with an alert icon.
- **Dropzone:** a dashed tile with a teal icon, bold label, hint and a small ghost button; teal on hover or drag; solid emerald with the filename once filled.

### Navigation
- **Rail:** group headings in Mist at 15.5px; items 49px tall, 9px radius, 16.5px, 21px stroke icons. Hover is a faint teal wash. Active is a saffron-to-peacock horizontal wash, white text and a saffron icon.
- **Top bar:** breadcrumb with `/` separators (last crumb in Paper Ink), a 38px search field, and an EN | हिन्दी toggle where the active language is Paper Ink.
- **Mobile:** the rail becomes a drawer opened from a menu button.

### Verdict Tile (signature)
The first KPI. Accept: the saffron→coral sweep, dark ink, a dark disc with a saffron check, "Fingerprint found", warm glow. Reject: slate gradient (`#3A4C58 → #2C3A45`), Paper Ink text, a coral-tinted disc with a coral cross, "No valid fingerprint" and the reason.

### Score Distribution (signature)
A histogram of the wrong-key null distribution in lilac, a dashed coral threshold line labelled `z = 4.4`, and the best centre's bar: emerald → saffron when above threshold, flat grey (`#58707C`) when below. On arrival the bar climbs from 4% height (1.1s, `cubic-bezier(.16,1,.3,1)`, 0.55s delay) and its label rises in after it.

### Score Bar
A 14px fully round track in a faint teal; teal → emerald fill for significant rows, muted teal for the rest; a 3px Coral Ink tick marks the threshold.

### Investigative-lead Notice
A coral hairline banner (9px radius, coral 16% → 7% wash, Coral Ink text, alert icon). Required next to every result and on every page head; it is right-aligned in the title row.

### Server Banner
Waking: teal wash, mint text, spinning loader. Down: coral wash, Coral Ink text, retry button outlined in `currentColor`.

## Do's and Don'ts

### Do:
- **Do** give every new element the colour of its meaning (saffron verdict/action, emerald agreement, coral rejection/caution, lilac statistics) or leave it neutral.
- **Do** pair every accept/reject colour with an icon and words.
- **Do** keep the "Investigative lead, not proof" notice in coral beside any result.
- **Do** set comparable numbers tabular and render p-values with a real superscript exponent.
- **Do** use one stroke icon family (Lucide, 1.5–2 stroke) at 15–26px.
- **Do** keep motion to the result-arrival moment and honour `prefers-reduced-motion` (all animation and transitions off).
- **Do** test both EN and हिन्दी at every breakpoint; Mukta carries Devanagari.

### Don't:
- **Don't** use red or "Not a match" wording for below-threshold rows; they are neutral teal "Below threshold".
- **Don't** give a glow to anything that is not saffron.
- **Don't** add a light theme, a near-black neon "cyber" palette, or a white SaaS dashboard look.
- **Don't** introduce a second display face.
- **Don't** imply a real government body (no emblems, ministry names).
- **Don't** use saffron for a non-significant result.
