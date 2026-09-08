#!/usr/bin/env bash
# Point the installed Claude for Commerce examples at all vibes space.
#
# Usage:
#   ./scripts/configure-commerce-agents.sh [--dir CHECKOUT] [--check]
#
#   --dir CHECKOUT  the claude-for-commerce-examples checkout
#                   (default: the sibling of this repo)
#   --check         run the checkout's test suite afterwards
#
# Copies four things from config/commerce-agents/ into the checkout:
#   root.env                     -> .env                             (storefront)
#   merchant.env                 -> merchant/.env                    (merchant)
#   thresholds.json              -> merchant/data/thresholds.json    (alert rules)
#   storefront_agent_config.py   -> storefront/api/agent_config.py   (brand and search notes)
#
# The two .env files are merged, not overwritten: a key that already has a value in the
# checkout keeps it, so credentials filled in there survive a re-run. Neither template
# carries a secret.

set -euo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
SRC="$REPO_ROOT/config/commerce-agents"
DIR=$(dirname "$REPO_ROOT")/claude-for-commerce-examples
CHECK=0

die() { printf 'error: %s\n' "$1" >&2; exit 1; }
step() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }

while [ $# -gt 0 ]; do
  case "$1" in
    --dir) [ $# -ge 2 ] || die "--dir needs a value"; DIR=$2; shift 2 ;;
    --check) CHECK=1; shift ;;
    -h|--help) sed -n '2,21p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -f "$DIR/requirements.txt" ] || die "not a claude-for-commerce-examples checkout: $DIR
run ./scripts/setup-commerce-agents.sh first, or pass --dir"

# Write the template, then restore the destination's value for each key the template
# leaves blank. The template owns every setting it states; the checkout owns the
# credentials, which is exactly the set of keys the template ships empty.
merge_env() {
  local template=$1 dest=$2
  python3 - "$template" "$dest" <<'PY'
import pathlib, re, sys

template, dest = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
text = template.read_text()

blank = set(re.findall(r"(?m)^([A-Z_][A-Z0-9_]*)=$", text))
kept = []
if dest.exists():
    for line in dest.read_text().splitlines():
        m = re.fullmatch(r"([A-Z_][A-Z0-9_]*)=(.+)", line.strip())
        if not m or m.group(1) not in blank:
            continue                  # comments, empty values, keys the template sets
        key, value = m.group(1), m.group(2)
        text = re.sub(rf"(?m)^{re.escape(key)}=$", f"{key}={value}", text)
        kept.append(key)

dest.write_text(text)
print(f"  {dest}" + (f" (kept {', '.join(sorted(kept))})" if kept else ""))
PY
}

step "Environment"
merge_env "$SRC/root.env" "$DIR/.env"
merge_env "$SRC/merchant.env" "$DIR/merchant/.env"

step "Alert thresholds and storefront config"
cp "$SRC/thresholds.json" "$DIR/merchant/data/thresholds.json"
printf '  %s\n' "$DIR/merchant/data/thresholds.json"
cp "$SRC/storefront_agent_config.py" "$DIR/storefront/api/agent_config.py"
printf '  %s\n' "$DIR/storefront/api/agent_config.py"

if [ "$CHECK" = 1 ]; then
  step "Test suite"
  # The storefront's health test asserts the demo shop by name, so pin SHOP_DOMAIN for
  # the run: it checks the code, not whichever store .env points at.
  (cd "$DIR" && SHOP_DOMAIN=demostore.mock.shop ./.venv/bin/python -m pytest -q)
fi

cat <<EOF

$(printf '\033[1mConfigured.\033[0m') Still to fill in, in the checkout and nowhere else:

  $DIR/.env               ANTHROPIC_API_KEY
  $DIR/merchant/.env      ANTHROPIC_API_KEY, SHOPIFY_OPERATOR,
                          SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET

Both files are gitignored there. docs/claude-commerce-agents.md has the Dev Dashboard
steps and the scope table.

Read-only first, before the merchant agent is pointed at the live catalog:

  cd $DIR
  SHOPIFY_LOCAL_STORE=1 ./.venv/bin/uvicorn merchant.api.main:app --port 8005
  ./.venv/bin/python merchant/scripts/smoke_live.py --read-only
EOF
