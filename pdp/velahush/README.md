# VelaHush Pet Odor Gun — Zovelle-style product page (GemPages)

Status: sections are BUILT locally (build/01..15.json) but NOT yet uploaded to GemPages —
the upload step was interrupted by an API session limit. Resume from "Upload" below.

## What is already done in Shopify (store yxciec-f7.myshopify.com)
- Old product `VelaHush™ Pet Odor Gun — Cover the Whole Couch…` (1/2/3-gun bundles, gid 15271252296044)
  → ARCHIVED, handle renamed to `velahush-pet-odor-gun-v1-bundles` (no redirect). Reversible.
- New canonical product (gid 15272587166060, Setup × Scent, $49 / $59.90)
  → handle `velahush-pet-odor-gun`, status ACTIVE, title `VelaHush™ Pet Odor Gun`,
    SEO title/description set, tags merged, compareAtPrice $70 on all 4 "Gun + 3 refill pods" variants,
    8 extra media added (before-after, collage, 97-percent, customer-results, five-reasons,
    no-more-struggling, commitment, ultimate) on top of the 4 "velahush" images.
- Refill Pods 3 Pack (gid 15272607285612) → ACTIVE, SEO set. Still has no media.
- Result: exactly ONE live PDP link: /products/velahush-pet-odor-gun

## GemPages
- Shop id: 629191576383390213 (theme id 629191580695135188)
- Draft page created: GP_PRODUCT id **636081050124026729** "VelaHush Pet Odor Gun — Product Page" (no sections yet)
- The existing static landing page "VelaHush" (636027272351974249) was the source of the copied sections.

## Upload (resume here)
For each file in build/index.json order, call `gempages_create_section` with
shopId, themePageID=636081050124026729, name (below), display=true, isMobile=false,
component = the file content (compact JSON string, byte-exact). Then `gempages_update_page`
with sectionPosition = the returned ids in order 01..15. Then `gempages_get_page_links`.

01 PDP · Buy box | 02 PDP · Trust marquee | 03 PDP · Problem | 04 PDP · How it works |
05 PDP · Why a mist | 06 PDP · Infographics | 07 PDP · Three tests | 08 PDP · Refills |
09 PDP · Poster band | 10 PDP · Comparison | 11 PDP · What it is not | 12 PDP · Guarantee |
13 PDP · FAQ | 14 PDP · Final CTA | 15 PDP · Sticky ATC (root tag is Sticky)

Regenerate with `python3 build.py` (reads src/ + lib/, writes build/).
