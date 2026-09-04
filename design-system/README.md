# Cupertino DS

A small, dependency-free design system in the visual language of minimal product
marketing sites: near-black text on white and one signature light grey, a single
saturated blue for actions, tight negative tracking that gets tighter as type
grows, pill-shaped controls, and a lot of vertical air.

It is plain CSS. No build step, no framework, no runtime — so it drops into a
static page, a Shopify theme, or a GemPages custom-CSS block equally well.

```
design-system/
├── src/
│   ├── tokens.css       colour, type, space, radius, motion — light + dark
│   ├── base.css         reset, element defaults, type utilities, layout
│   └── components.css   nav, buttons, cards, tiles, forms, accordion, footer
├── dist/cupertino.css   the three layers concatenated (what you ship)
├── index.html           live specimen page / documentation
└── build.sh             regenerates dist/
```

## Use it

```html
<link rel="stylesheet" href="design-system/dist/cupertino.css">
```

Open `design-system/index.html` in a browser to see every token and component,
with a dark-mode toggle in the nav.

## Rebrand it

No component rule hard-codes a colour, radius or duration — they all read tokens.
So a rebrand is a token override placed *after* the stylesheet:

```css
:root {
  --ap-accent: #7c3aed;   /* buttons */
  --ap-link: #6d28d9;     /* inline + chevron links */
  --ap-radius-lg: 8px;    /* squarer cards */
  --ap-container: 1120px; /* wider editorial column */
}
```

Dark mode follows the OS by default. To force a mode, set `data-ap-theme="dark"`
or `"light"` on `<html>`.

## Edit it

Change a file in `src/`, then:

```bash
./design-system/build.sh
```

## What's in it

**Foundations.** A 4px spacing scale; a fluid section rhythm (`clamp(56px → 120px)`)
that collapses on phones without a media query; three container widths, of which
980px is the editorial column copy should live in; radii of 18px (cards), 28px
(tiles) and pill (controls); one easing curve, `cubic-bezier(.28,.11,.32,1)`,
used by every transition.

**Type.** Nine steps from `.ap-t-caption` (12px) to `.ap-t-hero` (fluid, up to
88px). Each step ships size, line-height and tracking as a matched set, so you
never pair a size with the wrong leading. Body copy is 17px at `-0.022em`.
The `.ap-t-*` classes are independent of heading level, so the document outline
stays honest while the visual hierarchy does what the layout needs.

**Components.** `.ap-nav` (44px, translucent, blurred, sticky), `.ap-btn` in three
variants and three sizes, `.ap-link-chevron` (the tertiary action this system
leans on), `.ap-card`, `.ap-tile`, `.ap-stat`, `.ap-badge`, `.ap-segmented`,
form fields with an invalid state, a native `<details>` accordion, `.ap-table`,
and `.ap-footer`.

## Two ideas worth knowing

**Inverse blocks flip the token scope, not each child.** `.ap-section--inverse`,
`.ap-card--inverse` and `.ap-tile--inverse` redefine `--ap-text`,
`--ap-link`, `--ap-separator` and friends locally, so everything nested inside —
headings, muted copy, links, badges, outline buttons — resolves correctly with no
extra classes. Because the `--on-inverse` companions flip with the theme, the
same markup reads right whether the page is light or dark.

**Blocks separate from whatever ground they sit on.** Cards and tiles fill with
`--ap-fill`, which is the light grey by default and the base surface inside
`.ap-section--grey`. A grey card on a grey section can't happen.

## Conventions

- Every class and custom property is `ap-` / `--ap-` prefixed, so it will not
  collide with a Shopify theme's CSS.
- The reset is limited to `box-sizing` and element defaults. It does not
  scorch the page.
- Interactive targets are at least 44px tall; focus is a visible 3px ring,
  keyboard-only.
- `prefers-reduced-motion` disables transitions and smooth scrolling.
- One accent colour. If something needs to stand out, it competes with the
  buy button — that is the point of the constraint.
- Status hues brighten in dark mode; the light-mode red would fail contrast on
  black. No small-text default uses `--ap-text-tertiary`, which is below WCAG AA
  at 12px — it is available as an explicit opt-in (`.ap-dim`) and for
  placeholders.

## Using it with GemPages

Paste `dist/cupertino.css` into the theme or page custom-CSS field, then write
sections with `ap-` classes. Because the whole system is tokens plus flat
component classes, a section built this way stays editable in the GemPages
visual editor — the classes carry the styling, the editor moves the boxes.

---

Cupertino DS is an original token set and component library written for this
repository. It borrows a well-known *approach* to minimal product marketing
design; it contains no third-party assets, fonts, logos or copy, and is not
affiliated with or endorsed by any company.
