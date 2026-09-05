#!/usr/bin/env python3
"""Assert every colour pair in tokens.css meets its WCAG threshold.

Values are read from tokens.css, so this file holds the rules and that file
holds the palette — editing a hex there and breaking a rule fails here.

    python3 contrast-check.py          # check, exit 1 on any failure
    python3 contrast-check.py --table  # print the full matrix as well

Exit codes: 0 all pass · 1 at least one fail.
No dependencies; standard library only, so it drops into CI as-is.
"""
import re
import sys
import pathlib

TOKENS = pathlib.Path(__file__).with_name("tokens.css")

# --- WCAG 2.2 relative luminance and contrast ------------------------------

def _channel(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def luminance(hex_colour):
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)

def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

# --- Read the palette out of the stylesheet ---------------------------------

def load_scopes(css):
    """Return {'light': {...}, 'dark': {...}} of token name -> hex.

    Dark inherits from light, then overrides — the same way the cascade
    resolves it in the browser, so the check sees what a visitor sees.
    """
    def block(selector, label):
        # ^ needs MULTILINE to anchor on the selector's own line; . needs
        # DOTALL to run to the block's closing brace.
        m = re.search(re.escape(selector) + r"[^{]*\{(.*?)\n\}", css, re.S | re.M)
        if not m:
            sys.exit("contrast-check: could not find the %s block" % label)
        return dict(re.findall(r"(--vh-[a-z-]+)\s*:\s*(#[0-9A-Fa-f]{6})", m.group(1)))

    light = block(":root", "light")
    dark = dict(light)
    dark.update(block(".vh-dark,", "dark"))
    return {"light": light, "dark": dark}

# --- The rules ---------------------------------------------------------------
# (foreground, background, minimum, what it is)
#
# 4.5  body text                     WCAG 1.4.3 AA
# 3.0  large text, and the boundary of a UI component   WCAG 1.4.11
TEXT, UI = 4.5, 3.0
# Pass, but by so little that any later tweak breaks it. Warned, never failed.
MARGIN = 1.10

RULES = [
    ("--vh-text",           "--vh-surface",      TEXT, "body text"),
    ("--vh-text-secondary", "--vh-surface",      TEXT, "secondary text"),
    ("--vh-accent-text",    "--vh-surface",      TEXT, "accent as text (badge, struck price)"),
    ("--vh-warn",           "--vh-surface",      TEXT, "warning text"),
    ("--vh-cta-text",       "--vh-cta",          TEXT, "label on the buy button"),
    ("--vh-cta-text",       "--vh-cta-hover",    TEXT, "label on hover"),
    ("--vh-cta-text",       "--vh-cta-active",   TEXT, "label on active"),
    ("--vh-selected-text",  "--vh-selected",     TEXT, "label on the selected plan"),
    ("--vh-star",           "--vh-surface",      UI,   "rating stars"),
    ("--vh-line-strong",    "--vh-surface",      UI,   "rule that separates meaning"),
    ("--vh-mist-edge",      "--vh-surface",      UI,   "border of the mist panel"),
]

# A double focus ring is one component, so the rule is that AT LEAST ONE of its
# two colours separates from the ground. Asserting a single member instead just
# invites flipping the pair around until the assertion passes.
EITHER = [
    (("--vh-focus-inner", "--vh-focus-outer"), "--vh-surface", UI, "focus ring against the page"),
    (("--vh-focus-inner", "--vh-focus-outer"), "--vh-cta",     UI, "focus ring against the buy button"),
]

# Checked once per scope with the right ground for that scope.
BOUNDARY = [
    ("light", "--vh-cta", "--vh-surface", UI, "buy button edge on cream"),
    ("dark",  "--vh-cta-ring", "--vh-surface", UI, "buy button ring on pine"),
]

# Reported, never enforced: no palette passes these, and the fix is structural
# (a mark and a border), not a colour.
ADVISORY = [
    ("--vh-cta", "--vh-selected",
     "buy button vs selected plan — under protanopia these converge to ~1.03, "
     "so selection must also carry a radio mark and a border"),
    ("--vh-surface-mist", "--vh-surface",
     "mist fill vs page ground — 1.10, which is why .vh-mist-panel draws a border"),
]

def main():
    css = TOKENS.read_text()
    scopes = load_scopes(css)
    show_table = "--table" in sys.argv
    failures = []
    warnings = []

    for scope, tokens in scopes.items():
        checks = [(f, b, m, w) for f, b, m, w in RULES]
        checks += [(f, b, m, w) for s, f, b, m, w in BOUNDARY if s == scope]
        print("\n%s section" % scope.upper())

        for pair, bg, minimum, what in EITHER:
            best = max((contrast(tokens[f], tokens[bg]), tokens[f]) for f in pair)
            ok = best[0] >= minimum
            if not ok:
                failures.append("%s/%s: best of the pair is %.2f, needs %.1f"
                                % (scope, what, best[0], minimum))
            if show_table or not ok:
                print("  %-5s %5.2f  need %.1f   %-42s %s on %s"
                      % ("PASS" if ok else "FAIL", best[0], minimum, what, best[1], tokens[bg]))

        for fg, bg, minimum, what in checks:
            if fg not in tokens or bg not in tokens:
                failures.append("%s/%s: %s or %s is not defined" % (scope, what, fg, bg))
                continue
            ratio = contrast(tokens[fg], tokens[bg])
            ok = ratio >= minimum
            # Clearing a threshold by a rounding error is not clearance: a hue
            # tweak or antialiasing on a thin glyph puts it back under.
            thin = ok and ratio < minimum * MARGIN
            if not ok:
                failures.append("%s/%s: %.2f, needs %.1f (%s on %s)"
                                % (scope, what, ratio, minimum, tokens[fg], tokens[bg]))
            if thin:
                warnings.append("%s/%s: %.2f against a %.1f threshold — under 10%% of margin"
                                % (scope, what, ratio, minimum))
            if show_table or not ok:
                print("  %-5s %5.2f  need %.1f   %-42s %s on %s"
                      % ("FAIL" if not ok else ("THIN" if thin else "PASS"),
                         ratio, minimum, what, tokens[fg], tokens[bg]))
        if not show_table:
            print("  %d pairs checked" % (len(checks) + len(EITHER)))

    print("\nADVISORY — not enforced")
    for fg, bg, note in ADVISORY:
        ratio = contrast(scopes["light"][fg], scopes["light"][bg])
        print("  %5.2f  %s" % (ratio, note))

    if warnings:
        print("\nTHIN MARGIN — passes, but only just")
        for w in warnings:
            print("  " + w)

    if failures:
        print("\n%d FAILURE(S):" % len(failures))
        for f in failures:
            print("  " + f)
        return 1
    print("\nAll pairs pass.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
