# VelaHush — Dawn palette

The D1 palette completed into a build-ready token set, with a contrast checker
that fails CI when an edit breaks a rule.

```bash
python3 contrast-check.py          # exit 1 if any pair fails
python3 contrast-check.py --table  # print all 30 pairs
```

`tokens.css` holds the palette, `contrast-check.py` holds the rules, and it
reads the hexes out of the stylesheet — so there is one place to change a colour
and one place to change a threshold, and they cannot drift.

## What the D1 draft got right

All ten of its published ratios verify exactly. Catching that `#E9A23B` was only
1.97 and replacing it was a real save.

Its rule that the CTA needs a second colour on dark sections is also **provably
necessary**, not a preference. Searching the whole HSV space around clay's hue
(9.3°) finds nothing that is both dark enough for white text at 4.5 and light
enough to separate from pine at 3.0 — pine sits at luminance 0.035, so any
button dark enough to carry white type collapses into it. The closest,
`#E0543A`, reaches a 3.23 boundary but drops white text to 3.82.

## Two things this changes

**The CTA keeps one colour everywhere.** WCAG 1.4.11 asks that a component's
*boundary* be distinguishable, not that its fill contrast with the ground. A
cream ring on pine is 11.24, so `--vh-cta-ring` gives the button an unmistakable
edge while the fill stays clay in every section. Two CTA colours would solve the
same problem by making buyers re-learn the buy button halfway down the page.

**Every role that lands on a dark section now has an on-dark value.** The draft
specified only the CTA, which left eucalyptus at 1.98 and the warning at 2.49
against pine — a selected plan and a guardrail notice, both invisible.

## Gaps the draft's ten numbers did not cover

| Pair | Ratio | |
|---|---|---|
| clay `#C94B34` as **text** on cream | 4.22 | fails 4.5 |
| mist `#DDECF2` fill vs cream ground | 1.10 | the panel has no edge |
| eucalyptus on pine | 1.98 | no on-dark secondary existed |
| warning on pine | 2.49 | no on-dark warning existed |

The clay one is the one that bites. The draft defines clay only as a button fill
with white text, but an accent colour always leaks into type — badges, struck
prices, urgency lines, section eyebrows. `--vh-accent-text` (`#BD4631`, 4.69) is
the same hue, darkened until it passes.

Mist is the one that hides. Its own check, `pine on mist` at 10.19, only proves
text *inside* the panel is readable; nobody checked whether the panel is visible
on the page. At 1.10 it is not, so `.vh-mist-panel` draws `--vh-mist-edge`.

## Thin margins

Passing a threshold by a rounding error is not passing it — a hue tweak for
brand reasons, or antialiasing on a thin glyph, puts it back under. The checker
warns (without failing) on anything inside 10% of its threshold. Seven pairs are
currently thin:

| Pair | Ratio | Threshold | Margin |
|---|---|---|---|
| warning text on cream | 4.51 | 4.5 | 0.2% |
| white on clay (both scopes) | 4.63 | 4.5 | 2.9% |
| accent text on pine | 4.57 | 4.5 | 1.6% |
| accent text on cream | 4.69 | 4.5 | 4.2% |
| rule on pine | 3.26 | 3.0 | 8.7% |
| rating stars on cream | 3.29 | 3.0 | 9.7% |

Warning text at **4.51** is the draft's own fix and clears by 0.01. White on clay
at 4.63 is structural — it is what fixes clay's lightness — so it is a warning to
live with, not a bug.

D1's star `#BA812F` cleared the 3.0 graphical-object threshold by 0.05, a 1.7%
margin. `#B27C2D` takes that to 9.7%, which is still inside the warning band but
roughly six times the headroom. Pushing to `#A8752B` (3.65) clears it entirely at
the cost of a visibly browner star — a call worth making deliberately rather than
by default.

## What colour cannot fix

Under protanopia the buy button and the selected plan converge to a contrast of
**1.03** — for those viewers they are the same colour. Deuteranopia gives 1.61.

The audience is US women 35+, where red-green colour blindness runs near 0.4%
rather than the 8% figure usually quoted for men, so the reach is small. The fix
costs nothing anyway and is structural, not chromatic: selection is carried by
the radio mark and the border weight, never by fill alone. `tokens.css` ships
that rule alongside the tokens so it does not get optimised away later.

## Wiring it into CI

```yaml
- run: python3 design-system/velahush-dawn/contrast-check.py
```

No dependencies — standard library only.

## Still open

Three palettes now exist in this repository and nothing has chosen between them:
Modernist (red `#ec3013`, from Claude Design), Cupertino (blue `#0071e3`), and
this one. All three are built and runnable. That decision, not any contrast
ratio, is what is blocking the build.

One note beyond accessibility. Warm cream, deep pine and clay is an
apothecary/home-care palette: it reads *natural, gentle, not chemical*. The page
plan meanwhile carries a surfaces-and-solutions guardrail and a see-your-vet
line — copy that is carefully avoiding exactly that claim. Colour is a claim
too, and here it is making one the words are working to walk back. Pulling pine
toward teal or slate, away from botanical green, keeps the positioning without
the implication.
