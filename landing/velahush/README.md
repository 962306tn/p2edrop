# VelaHush — pet odor gun landing page

A static recreation of the hi-fi design handed off from Claude Design, built on
the **Modernist** design system. Single-product direct-response page; audience is
US women 35+ with dogs or cats; the page has one job, which is add-to-cart on the
refill plan.

It ships in two skins. Open either in a browser — no build step, no server, no
dependencies.

| | |
|---|---|
| **`index.html`** | **Modernist** — the approved design from Claude Design |
| **`index-cupertino.html`** | **Cupertino** — the same page in the repo's own design system, with a dark-mode toggle in the nav |

```
index.html                the page, Modernist skin
index-cupertino.html      the page, Cupertino skin — head and one nav button apart
velahush.js               behaviour, shared by both — and the only place prices live
velahush.css              Modernist skin
ds-modernist.css          Modernist tokens, verbatim from Claude Design — do not edit
velahush-cupertino.css    Cupertino skin
assets/                   photos; see assets/README.md for what goes where
reference/                the handoff sources this was built from
```

The Cupertino skin reads its tokens from `../../design-system/dist/cupertino.css`,
so a fix to that design system reaches this page without a copy step.

## Two skins, one markup

The two HTML files differ by twelve lines: the two stylesheet links, and the
theme-toggle button. Everything else — every section, every string, every class —
is identical, and both load the same `velahush.js`.

That works because no styling decision lives in the markup. There are no inline
styles and no design-system class names in the HTML; even the uppercasing is a
CSS rule, which is why the same `<h1>` reads `NOBODY SHOULD BE ABLE TO TELL YOU
HAVE DOGS.` in one skin and `Nobody should be able to tell you have dogs.` in the
other. **If you edit the page, edit both HTML files**, or the two drift.

The skins are opposites, and that is the point of keeping both:

| | Modernist | Cupertino |
|---|---|---|
| Corners | square, everywhere | pill controls, 18px cards |
| Separation | 2px rules | air and alternating grounds |
| Type | Archivo 800, uppercase, tight | system stack, sentence case |
| Accent | red `#ec3013` | blue `#0071e3` |
| Photography | forced black and white | full colour |
| Contrast band | red field | black field, flipping in dark mode |
| Dark mode | none | follows the OS, with a nav toggle |

Two conveniences fall out of the Cupertino skin not loading `ds-modernist.css`:
its `.grayscale` class stops existing, so photos print in colour on their own,
and Archivo is never requested, so that page loads no web font at all.

Dark mode is stored per browser under `vh-theme` and applied by a small inline
script in the head, before first paint — otherwise a stored dark choice flashes
light on every load. With nothing stored the design system follows the OS, so
the button's label says what the click will do, not what the theme currently is.

## Editing the offer

Prices and terms live in one object at the top of `velahush.js`:

```js
var OFFER = { gunPrice: 49, bundlePrice: 59.90, refillPrice: 21, ... };
```

Change a number there and it updates the plan rows, the plan note, both CTAs, the
sticky summary, the marquee and the FAQ answers together. These mirror the
editable props on the Claude Design component, so the two stay comparable.

## Why ds-modernist.css is untouched

It ships exactly as exported. Keeping it pristine is what lets the next export
from Claude Design be diffed against it to see what actually changed in the
system. Page-specific styling goes in `velahush.css`, which reads its tokens.

The system's non-negotiables, upheld throughout: zero border radius; 2px rules
separating every major section; everything flush left, including the label inside
the wide CTA; Archivo only, headings uppercase and tight; photography pure black
and white; red reserved for the CTA, the badges and the one poster band.

## Where this departs from the prototype

Each of these is deliberate. The handoff `README.md` (in `reference/`) is the
spec; where it and the `.dc.html` disagreed, the spec won.

1. **Bullet numbers `01–04` use `--color-accent-700`, not `--color-accent`.** The
   spec asks for accent-700 and explains why: at body size the base red clears
   only ~3:1 on this ground. The prototype code used the base accent. If you want
   the brighter red back it is one line in `.vh-bullet__n`.
2. **The announcement bar runs edge to edge**, with only its content held to the
   1240px grid. The prototype capped the bar itself at 1240px, which leaves it
   visibly inset on wide screens while the header rule below it does not.
3. **Header CTA reads "SHOP $49".** The prototype's template produced
   `Shop $ 49`, with a stray space.
4. **Grid rules are drawn as 1px gaps** showing the container through, rather
   than a border on each cell. Identical look, but correct when a grid wraps — the
   border version left a rule hanging at the right edge with nothing matching it.
5. **The scent box is a fixed 2×2.** Auto-fit put the fourth cell alone in its own
   row with the container showing through beside it.
6. **Scent descriptions are new copy.** The prototype's markup loops over
   `scentCards`, but its view model never defines that value, so the box rendered
   empty. The spec asked for "Lemon — bright, citrus-clean" style notes; these are
   written to that brief and are the one piece of copy on the page not from the
   handoff.
7. **Archivo 500 and 700 are requested.** The design system only imports 400/600/
   800, but the page sets 500 and 700 in several places, which browsers were
   synthesising.
8. **`prefers-reduced-motion` is honoured** — the marquee, the blinking scarcity
   dot and the sticky-bar slide all stop. The spec asks for this in production.
9. **One passive scroll listener** drives the sticky bar. The prototype needed a
   window listener, a capture-phase document listener and a 250ms poll because it
   ran inside a scrolling host container; a real page does not.
10. **The FAQ is buttons with `aria-expanded` and a hidden panel**, so it works by
    keyboard and reads correctly to a screen reader.

## Before this takes traffic

Two blockers, both flagged in the handoff spec:

- **The product photo carries the supplier's branding.** The unit and box read
  "K12 Blue Ray Sprayer" and it is legible at hero size. Reshoot or retouch.
- **Every social-proof number on the page is a placeholder.** "4.8/5 from 25,089
  reviews", "90% said odor was clearly reduced", "30,000+ US homes", "1,284 orders
  shipped in the last 7 days", "312 shipped this week", and all three named
  testimonials came from the prototype as invented marketing copy. Replace with
  substantiated figures and real, consented reviews before running US traffic —
  the FTC's endorsement and substantiation rules apply to all of it.

Two more to watch:

- The **live order row** cycles demo cities every 5.2s. Feed it from real recent
  orders or drop the section; do not fabricate order counts.
- The **arrival window** is computed as today+5 to today+9. Replace with the real
  fulfilment SLA.
- Keep odor claims **non-medical** — no disinfects, kills germs, or virus claims —
  unless the product is EPA-registered for it.

## Porting to a store

The markup is deliberately plain: semantic sections, flat `vh-` classes, no
framework. To move it to Shopify sections, GemPages, or a headless front end,
carry over `ds-modernist.css` and `velahush.css` as-is and re-express `index.html`
in the target's templating. Then wire the two things this page only fakes:

- **Add to cart** — add the selected variant, and for the plan option create the
  subscription / selling-plan line, then open the cart drawer. The scent must
  travel into the cart line item and into the subscription.
- **Reviews and ratings** — from the real review source, not the constants.

Product, variant and selling-plan IDs, the review aggregate, and cart state are
the only data the page needs.
