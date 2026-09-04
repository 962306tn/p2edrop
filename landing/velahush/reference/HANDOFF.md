# Handoff: VelaHush pet-odor-gun product landing (dropship, US, women 35+)

## Overview
A single-product direct-response landing page for a cordless "odor gun" (nano dry-mist fogger) sold
dropship in the United States. Audience: US women 35+ with dogs/cats. The page's job is one thing:
get the visitor to add a unit to cart, ideally on the recurring-refill plan.

Commercial model baked into the page:
- Odor gun, one-time: **$49**
- Odor gun + 3 refill pods: **$59.90** (marked MOST POPULAR)
- Odor gun + refill plan: **$59.90** today, then **$17.85** every 2 months (3 pods, 15% off, skip/cancel anytime) — marked NEVER RUN OUT
- Refill pods standalone: **$21 / 3 pods**
- 30-day money back, 90-day warranty (motor + battery), free US shipping over $50, ships from California

## About the Design Files
The files in this bundle are **design references authored in HTML** — a working prototype of the
intended look, copy and behavior. They are **not production code to copy**. The task is to
**recreate this design in the target codebase's own environment** (Shopify/Liquid + theme sections,
Next.js/React, Vue, whatever the store runs on) using its established components, routing, cart and
analytics. If no environment exists yet, pick the appropriate stack for a Shopify-backed or
headless-commerce store and implement there.

`VelaHush Landing v2.dc.html` is a "Design Component": one HTML file whose `<x-dc>` body is the
markup (all styling inline, tokens via `var(--*)`) and whose `<script data-dc-script>` class holds
the logic (state, derived values, handlers) — read it as *markup + a view model*, not as a
framework to port.

## Fidelity
**High-fidelity.** Final colors, type, spacing, copy and interaction states. Recreate closely.
The only intentionally unfinished parts are the **image placeholders** (striped boxes with a
monospace caption saying what photo belongs there) — those need real photography before launch.

## Design system
The page is built on the bound **Modernist** design system (see `ds-modernist.css` in this bundle,
copied from the project's `_ds/modernist-*/styles.css`). Non-negotiables from that system:
- Flat and architectural: **zero border radius everywhere** (`--radius-*: 0`).
- **2px rules** (`var(--color-divider)`, or `var(--color-text)` for the strongest edges) separate
  every major section; grid structure stays visible. Do not replace rules with whitespace.
- Everything **flush left**, including labels inside wide buttons (the CTA has label left, price right).
- Type is **Archivo** only (`--font-heading` 800 for headings, `--font-body` for copy). Headings are
  uppercase, tight (`letter-spacing: -0.03em`, `line-height: ~1`).
- Photography prints **pure black and white** (`filter: grayscale(1)`); never tint imagery.
- Accent red is used sparingly: CTA fill, badges, the one full-red poster band. For body-size text in
  red, use `--color-accent-700` (#ae1800) — the base accent only clears ~3:1 on this ground.
- Focus is a 2px accent `:focus-visible` ring; hover on the primary CTA is `--color-accent-600`.

## Screens / Views
One continuous page, max content width **1240px**, page gutter `var(--space-6)` (24px),
section vertical padding **72px**, bottom padding 104px to clear the sticky bar.
All multi-column blocks are `grid-template-columns: repeat(auto-fit, minmax(<N>px, 1fr))`, so the
page reflows to one column on mobile with no media queries. Verify at 390px and 1440px.

### 1. Announcement bar
Ink ground (#201e1d) with bg-colored text, 12px/600, uppercase, letter-spacing .1em, flex gap 32px,
padding 12px 24px. Items: "Free US shipping over $50" · "30-day money back" · "90-day warranty" ·
"Ships from California".

### 2. Header (sticky, top: 0, z-index 40)
Bg `--color-bg`, `border-bottom: 2px solid var(--color-text)`. Left: wordmark **VELAHUSH**
(Archivo 800, 24px, uppercase, -0.02em) + kicker "PET ODOR LAB" (11px/600, .14em, neutral-700).
Right: nav links (13px/600 uppercase, .06em, neutral-800) How it works · Reviews · Refills, then a
red CTA chip "SHOP $49" (accent fill, white text, padding 12px 16px, no radius).

### 3. Hero — buy block (id `#buy`)
Two columns, `minmax(380px, 1fr)`, gap 32px, closed by a 2px divider.
- **Left (sticky, top 92px)**: main image frame, 2px ink border, aspect-ratio 1/1, striped
  background `repeating-linear-gradient(45deg, neutral-200 0 10px, #fff 10px 20px)`; product photo
  fills it `object-fit: cover; filter: grayscale(1)`. Top-left red flag "2026 BEST ODOR TOOL"
  (11px/700, .12em, white on accent, padding 8px 12px). Below: 5 thumbnails in a 5-col grid, gap 8px,
  1/1, 2px border — ink when selected, neutral-300 otherwise; placeholder thumbs show a 9px caption.
- **Right column**, gap 24px:
  - Rating row: red-700 stars + "4.8/5 from 25,089 reviews" (13px/600, neutral-700).
  - H1, Archivo 800, `clamp(36px, 4.6vw, 58px)`, line-height .98, -0.03em, uppercase:
    "Nobody should be able to tell you have dogs."
  - Sub (17px/1.55, neutral-800, max 48ch): "A cordless dry-mist gun that neutralizes pet odor inside
    your couch cushions, rugs and car seats — so the room smells like nothing at all, not like a
    candle trying to hide something."
  - Benefit list, 4 rows, each `01–04` in accent-700 700/13px + text 15.5px, rows separated by 1px
    neutral-300, list topped by a 2px divider:
    01 Neutralizes odor inside the fabric — not perfume sprayed over it
    02 Dry mist: no soaked cushions, no wiping, safe to sit on in a minute
    03 Cordless and rechargeable — one charge covers about 40 rooms
    04 Fragrance-light and dye-free around pets, kids and asthma
  - **Plan picker** header row: "PICK YOUR SETUP" (11px/700, .14em) left, urgency "POD BATCH SHIPS
    FRIDAY" (12px/700 accent-700) right.
  - Three plan rows (see Commercial model). Each row: 18px square radio (2px ink border, accent fill
    when chosen), title Archivo 800/16px uppercase, optional badge (9.5px/700, .12em, white on accent
    for MOST POPULAR, on ink for NEVER RUN OUT), note 13.5px neutral-700, right-aligned price
    Archivo 800/19px with struck-through compare price 12.5px neutral-600. Selected row: white fill,
    2px ink border, `--shadow-sm`; unselected: transparent, 2px neutral-300.
  - Plan note under the picker, 12.5px neutral-700 with a 2px accent left rule and 12px padding:
    plan selected → "Plan billed $17.85 every 2 months after today. Skip or cancel in one click.";
    otherwise → "One-time purchase. Add pods later at $21 for three."
  - Scent chips: label "SCENT" + Lemon / Lavender / Peppermint / Fresh Linen. Chip 13px/600,
    padding 8px 12px, 2px border; selected = ink fill, bg-colored text.
  - **Primary CTA**: full-width, accent fill, white, Archivo 800/17px uppercase, padding 16px 24px,
    `display: flex; justify-content: space-between` → label flush left ("ADD TO CART"), price right
    ("$59.90"). Hover accent-600. On click the label becomes "ADDED TO CART" and the price a ✓.
  - Scarcity line: 8px accent square blinking (1.8s ease-in-out infinite, opacity 1 → .25) +
    "312 shipped this week · 5 orders in the last 30 min" (13px/600 neutral-700).
  - Trust grid, 2px divider box, 4 cells split by 1px rules: "30-DAY REFUND / Keep the pods either
    way", "90-DAY WARRANTY / Motor and battery covered", "ARRIVES <date range> / Tracking on every
    order", "US SUPPORT / Real replies within a day".
  - Payment chips: Visa, Mastercard, Amex, PayPal, Apple Pay, Shop Pay, Klarna — 10.5px/600 uppercase,
    1px neutral-400 border, padding 4px 8px.

### 4. Trust marquee
Full-width band, `--color-surface` ground, 2px bottom divider. Items 12px/700, .14em, uppercase,
neutral-800, padding 12px 24px, duplicated once and translated `-50%` over 32s linear infinite:
Neutralizes at the source · Dry mist, no residue · Cordless & rechargeable · 30,000+ US homes ·
90-day warranty · Refills from $17.85.

### 5. "You stopped smelling it. Your guests didn't."
Two columns. Left: kicker "THE MOMENT NOBODY TALKS ABOUT" (accent-700), H2
`clamp(28px, 3.6vw, 44px)` uppercase, two 16.5px/1.6 paragraphs (nose-blindness; candles add perfume
and wear off by dinner), then a 3-cell spec box (2px border, 1px inner rules): **18s** to treat a full
sofa · **5µm** dry-mist particle size · **40+** rooms per charge (numbers Archivo 800/30px).
Right: 4/3 photo frame placeholder — "photo: woman misting the sofa before guests arrive (B&W)".

### 6. How it works (id `#how`) — 3 steps
H2 "Three steps. About a minute." + line "No wiping, no drying time, no damp patches on the cushions."
Three equal cells (`minmax(280px, 1fr)`), 1px rules between, each: 3/2 photo placeholder,
"STEP 01/02/03" (11px/700, .16em, accent-700), title Archivo 800/21px uppercase, body 15px/1.55:
01 Click in a pod · 02 Sweep the fabric · 03 Walk away.

### 7. Refills (id `#refills`)
Two columns. Left: 1/1 grayscale photo of the refill oil bottle. Right: kicker "NEVER RUN OUT",
H2 "Refills: 3 pods for $21, or $17.85 on the plan", paragraph on cadence (each pod ≈25 living-room
treatments; three pods per two months; 15% off on plan; skip/pause/cancel from any email), a 4-cell
scent box (Lemon "bright, citrus-clean" style notes), and a secondary CTA — ink fill, bg text,
Archivo 800/14px uppercase, padding 16px 24px, hover accent — "ADD THE REFILL PLAN" linking to #buy.

### 8. Red poster band
Full-bleed `--color-accent` field, white type — the one place red runs as a ground.
H2 `clamp(30px, 4.4vw, 56px)` uppercase: "Sofa. Car. Pet bed. That's where the smell lives."
Right: 16.5px paragraph + six 2px-white-outlined chips: Sofa & cushions, Car seats, Pet beds,
Rugs & carpet, Litter area, Blankets.

### 9. Reviews (id `#reviews`)
Header: H2 "What dog and cat people say" + "4.8/5 from 25,089 reviews — all verified purchases";
right, a 3-cell stat box: 90% said odor was clearly reduced after one use · 30k+ US homes since 2024 ·
4.8 average rating. Then three UGC cards (`minmax(300px, 1fr)`, 1px rules, no radius, no shadow):
4/3 customer-photo placeholder, accent-700 stars, title Archivo 800/18px uppercase, body 15px,
attribution 12.5px/600 (Jenna G. — Ohio; Maika P. — Texas; Diane R. — Florida, all "verified buyer").

### 10. Recent orders / shipping map
`--color-surface` ground. Left: kicker "SHIPPING ACROSS THE STATES", H2 "1,284 orders shipped in the
last 7 days", then a 2px-bordered list of 5 rows (city+state, item, time-ago), rows split by 1px
rules. One row is "live": accent-100 background, accent dot, time-ago replaced by "just now"; it
advances every 5.2s. Right: 8/5 placeholder — "graphic: US map with order pins (B&W, red pins)".

### 11. Comparison table
Max width 1000px. 2px ink border. Header row: ink ground, bg text, 11px/700 .12em uppercase,
columns `1.7fr 0.65fr 0.65fr` — "COMPARE / VELAHUSH / SPRAYS & CANDLES". Six rows split by 1px rules,
label 15.5px, then "YES" (accent-700, 800/15px) and "NO" (neutral-600, 700/15px):
Neutralizes odor at the source · No heavy masking perfume · Reaches inside cushions and fibers ·
Safe around pets and kids · Still working by dinner time · Cost per use after month one.

### 12. Guarantee + warranty pair
Two cells, each 2px ink border (the right one shares the edge: `border-left-width: 0`), padding 32px.
Left (bg ground): kicker "30-DAY MONEY BACK", H3 `clamp(24px, 2.6vw, 34px)` uppercase "Use it for 30
days. If guests still notice, we refund you." + "Keep the refill pods. One email, no return-shipping
runaround, no restocking fee." Right (`--color-surface`): kicker "90-DAY WARRANTY", H3 "Motor or
battery quits inside 90 days? New unit, free." + "Send a photo of the serial plate and we ship a
replacement from California. Nothing to mail back."

### 13. FAQ (id `#faq`)
Max width 900px. 2px top rule; six rows, 1px bottom rules. Question row: 16.5px/700, padding 16px 0,
cursor pointer, right-side +/– sign (Archivo 20px, accent). Answer 15.5px/1.6, neutral-800, max 62ch,
padding-bottom 24px. Single-open accordion, first item open on load. Topics: does it really remove
odor vs cover it · safety around pets/kids · which smells · charge and pod life (with prices) ·
how the refill plan works · shipping/returns/warranty (with the computed arrival window).

### 14. Footer
2px top rule, `--color-surface`. Wordmark, uppercase 12px/600 links (Shipping, Refunds, Warranty,
Contact), and "© 2026 VelaHush. Results vary by surface and odor level."

### 15. Sticky add-to-cart bar
`position: fixed; left/right 0; bottom 0; z-index 50`, bg ground, `border-top: 2px solid ink`,
`transform: translateY(110% → 0)` with `transition: transform .2s ease`. Shows once scrollY > 640.
Left: 44px grayscale product thumb in a 2px border + selected summary (14px/700 uppercase:
"<plan> · <scent> · <price>") + "30-day money back · 90-day warranty · Free US shipping" (12px).
Right: accent CTA "ADD — $59.90" (Archivo 800/15px uppercase, padding 16px 24px), hover accent-600.

## Interactions & Behavior
- **Plan select** → updates the radio fill, card border/shadow, plan note, hero CTA price, sticky-bar
  summary and price; resets the "added" state.
- **Scent select** → updates chip fill and the summary string in the sticky bar. Scent must travel
  into the cart line item (and into the subscription for the plan option).
- **Gallery thumb select** → swaps the main image; selected thumb takes the 2px ink border.
- **Add to cart** (both CTAs) → in production: add the selected variant (and, for the plan, create the
  subscription/selling-plan line) then open the cart drawer. In the prototype it only flips the label
  to "ADDED ✓".
- **FAQ** → single-open accordion; clicking the open row closes it.
- **Sticky bar** → scroll listener on both `window` and `document` (capture phase) plus a 250ms
  interval poll, because the prototype runs inside a scrolling host container. In a real page a
  single scroll listener or an IntersectionObserver sentinel after `#buy` is enough.
- **Live order row** → `setInterval` 5200ms cycling the highlighted row. If you keep this, feed it
  from real recent-order data or clearly generic city names; do not fabricate order counts in markets
  with strict advertising rules.
- **Arrival window** → computed at render as today+5 to today+9 days, formatted `MMM d–MMM d`
  (`en-US`). Replace with the real fulfillment SLA.
- **Marquee / blink** → CSS keyframes only; respect `prefers-reduced-motion` in production (the
  prototype does not).
- Reflow is container-query-free: every grid uses `auto-fit + minmax`, so one column below ~380–780px.

## State Management
```
plan:    0 | 1 | 2      // 1 (gun + 3 pods) default
scent:   0..3           // 0 = Lemon
faq:     index | -1     // 0 open on load
img:     0..4           // gallery index, 0 default
sticky:  boolean        // scrollY > 640
added:   boolean        // CTA feedback, reset on plan change
tick:    number         // 5.2s counter driving the live order row
```
Derived per render: money formatting (`$59.90`, trailing `.00` stripped), `refillSub = refill * 0.85`,
arrival window, plan note, CTA labels, sticky summary, marquee items.
Production data needs: product + variant/selling-plan IDs, review aggregate (rating, count),
real recent-order feed (optional), cart state.

## Design Tokens
From `ds-modernist.css` — use the variables, not the hexes:
- `--color-bg` #f3f2f2 · `--color-surface` #eae9e9 · `--color-text` #201e1d
- `--color-accent` #ec3013 · `--color-divider` `color-mix(in srgb, #201e1d 40%, transparent)`
- Neutral ramp: 100 #f8f4f4 · 200 #eae7e7 · 300 #d7d3d3 · 400 #bab6b6 · 500 #9b9797 · 600 #7d7979 ·
  700 #605d5d · 800 #444141 · 900 #2d2b2b
- Accent ramp: 100 #fff2ef · 200 #ffe0d9 · 300 #ffc4b8 · 400 #ff9783 · 500 #ff563c · 600 #dd2b0f ·
  700 #ae1800 · 800 #7c1405 · 900 #4d170e
- Type: `--font-heading` / `--font-body` = "Archivo", system-ui, sans-serif; heading weight 800
- Spacing: `--space-1` 4 · `--space-2` 8 · `--space-3` 12 · `--space-4` 16 · `--space-6` 24 ·
  `--space-8` 32 (px)
- Radius: `--radius-sm/md/lg` = **0px**
- Shadow: `--shadow-sm` `0 1px 2px` ink 14% · `--shadow-md` `0 3px 10px` ink 16% ·
  `--shadow-lg` `0 12px 32px` ink 22%
- Page-level literals not in the token set: max-width 1240px (900/1000px for FAQ and table),
  section padding 72px, sticky offsets 92px (gallery) and 640px (sticky-bar threshold),
  heading clamps as quoted per section.

## Assets
- `uploads/assets-1788516208703-ks2u.jpg` — supplier photo of the unit on its retail box. Used as the
  hero image, first thumbnail and sticky-bar thumb, always `filter: grayscale(1)`.
  **Caveat: the unit and box carry the supplier's "K12 Blue Ray Sprayer" branding — reshoot or retouch
  to VelaHush before launch.**
- `uploads/assets-1788516208697-3bn1.jpg` — fragrance-oil bottle (Lemon). Used in the refill section
  and the second thumbnail, grayscale.
- Everything else is an intentional placeholder: a striped box with a monospace caption naming the shot
  needed (misting the sofa, in-hand scale, dog on treated rug, three how-it-works shots, three UGC
  customer photos, US order-pin map). Commission or license these before launch.
- Icons: the design system specifies **Lucide**; this page currently uses no icons — if you add any,
  take them from Lucide.
- Fonts: Archivo via Google Fonts (weights 400–800).

## Legal / compliance notes for whoever ships this
- "90% said odor was clearly reduced", "30,000+ US homes", "4.8/5 from 25,089 reviews", "1,284 orders
  shipped", "312 shipped this week" and the named testimonials are **placeholder marketing claims**
  from the prototype. Replace with substantiated numbers and real, consented reviews before running
  US traffic (FTC endorsement + substantiation rules).
- Odor-neutralizing claims should stay non-medical (no disinfection/kills-germs/virus claims) unless
  the product is EPA-registered for it.

## Files
- `VelaHush Landing v2.dc.html` — the hi-fi design (current). Markup in `<x-dc>`, view model in the
  `data-dc-script` class.
- `ds-modernist.css` — the Modernist design-system stylesheet (tokens + component layer).
- `support.js` — runtime that renders the prototype file locally. Not part of the design; do not port.
- `uploads/` — the two real product photos.
- `Freshden Pet Odor Landing.dc.html` — earlier v1 exploration in a different (warm serif) direction.
  Reference only; the Modernist version above supersedes it.
