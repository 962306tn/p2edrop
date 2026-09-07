#!/usr/bin/env bash
# Install Anthropic's Claude Commerce Agents blueprint and Shopify's
# implementation of it, plus the commerce-builder plugin for Claude Code.
#
# Usage:
#   ./scripts/setup-commerce-agents.sh [--dir DIR] [--shop your-store.com]
#                                      [--skip-blueprint] [--skip-plugin]
#
#   --dir DIR         where to clone (default: the parent of this repo)
#   --shop DOMAIN     write SHOP_DOMAIN into the storefront .env
#   --skip-blueprint  only install Shopify's implementation
#   --skip-plugin     don't register the commerce-builder Claude Code plugin
#
# What it installs:
#   Shopify/claude-for-commerce-examples  storefront + merchant agent for a real store
#   anthropics/commerce-agents            the blueprint, its four demo verticals,
#                                         and the commerce-builder plugin
#
# Needs Python 3.11+ and Node 22. Nothing here places an order or takes payment.

set -euo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
DIR=$(dirname "$REPO_ROOT")
SHOP=""
WITH_BLUEPRINT=1
WITH_PLUGIN=1

SHOPIFY_REPO=https://github.com/Shopify/claude-for-commerce-examples.git
BLUEPRINT_REPO=https://github.com/anthropics/commerce-agents.git

die() { printf 'error: %s\n' "$1" >&2; exit 1; }
step() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }

while [ $# -gt 0 ]; do
  case "$1" in
    --dir)  [ $# -ge 2 ] || die "--dir needs a value";  DIR=$2;  shift 2 ;;
    --shop) [ $# -ge 2 ] || die "--shop needs a value"; SHOP=$2; shift 2 ;;
    --skip-blueprint) WITH_BLUEPRINT=0; shift ;;
    --skip-plugin)    WITH_PLUGIN=0;    shift ;;
    -h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

# --- prerequisites ---------------------------------------------------------
command -v git >/dev/null || die "git is required"
command -v python3 >/dev/null || die "python3 is required"
command -v npm >/dev/null || die "npm (Node 22) is required"

python3 - <<'PY' || die "Python 3.11+ is required"
import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)
PY

NODE_MAJOR=$(node -p 'process.versions.node.split(".")[0]')
[ "$NODE_MAJOR" -ge 22 ] || die "Node 22+ is required (found $(node --version))"

mkdir -p "$DIR"

# Clone if missing, otherwise leave the working copy alone.
clone() {
  local url=$1 dest=$2
  if [ -d "$dest/.git" ]; then
    printf 'already cloned: %s\n' "$dest"
  else
    git clone --depth 1 "$url" "$dest"
  fi
}

# --- Shopify's implementation ----------------------------------------------
SHOPIFY_DIR="$DIR/claude-for-commerce-examples"

step "Shopify implementation -> $SHOPIFY_DIR"
clone "$SHOPIFY_REPO" "$SHOPIFY_DIR"

step "Python packages (storefront + merchant)"
[ -d "$SHOPIFY_DIR/.venv" ] || python3 -m venv "$SHOPIFY_DIR/.venv"
# requirements.txt has `-e ./vendor`, which pip resolves against the working
# directory, so install from inside the checkout. It also pulls the blueprint's
# packages from Anthropic's repository at the commit the file pins.
(cd "$SHOPIFY_DIR" && ./.venv/bin/pip install --quiet --upgrade pip && ./.venv/bin/pip install -r requirements.txt)

step "Web app packages"
(cd "$SHOPIFY_DIR" && npm install)

step "Environment files"
[ -f "$SHOPIFY_DIR/.env" ] || cp "$SHOPIFY_DIR/.env.example" "$SHOPIFY_DIR/.env"
[ -f "$SHOPIFY_DIR/merchant/.env" ] || cp "$SHOPIFY_DIR/merchant/.env.example" "$SHOPIFY_DIR/merchant/.env"
if [ -n "$SHOP" ]; then
  # Replace the SHOP_DOMAIN line in place, keeping the rest of the file.
  python3 - "$SHOPIFY_DIR/.env" "$SHOP" <<'PY'
import pathlib, re, sys
path, shop = pathlib.Path(sys.argv[1]), sys.argv[2]
text = path.read_text()
new = re.sub(r"(?m)^SHOP_DOMAIN=.*$", f"SHOP_DOMAIN={shop}", text)
path.write_text(new if new != text else text + f"\nSHOP_DOMAIN={shop}\n")
PY
  printf 'SHOP_DOMAIN=%s\n' "$SHOP"
fi
printf 'add ANTHROPIC_API_KEY to %s\n' "$SHOPIFY_DIR/.env"

step "Offline test suite"
# The storefront's health test asserts the demo shop by name, so pin SHOP_DOMAIN
# for the run: this checks the install, not whichever store .env points at.
(cd "$SHOPIFY_DIR" && SHOP_DOMAIN=demostore.mock.shop ./.venv/bin/python -m pytest -q)

# --- Anthropic's blueprint --------------------------------------------------
BLUEPRINT_DIR="$DIR/commerce-agents"

if [ "$WITH_BLUEPRINT" = 1 ]; then
  step "Anthropic blueprint -> $BLUEPRINT_DIR"
  clone "$BLUEPRINT_REPO" "$BLUEPRINT_DIR"

  step "Blueprint packages"
  [ -d "$BLUEPRINT_DIR/.venv" ] || python3 -m venv "$BLUEPRINT_DIR/.venv"
  # The seven packages install editable from their own directories, so cd first.
  (cd "$BLUEPRINT_DIR" \
     && ./.venv/bin/pip install --quiet --upgrade pip \
     && ./.venv/bin/pip install -r requirements.txt \
     && ./.venv/bin/pip install -r requirements-dev.txt)

  step "Demo web apps (retail, travel, telecom, entertainment)"
  (cd "$BLUEPRINT_DIR/examples" && npm ci)

  [ -f "$BLUEPRINT_DIR/.env" ] || cp "$BLUEPRINT_DIR/.env.example" "$BLUEPRINT_DIR/.env"
fi

# --- Claude Code plugin -----------------------------------------------------
if [ "$WITH_PLUGIN" = 1 ] && [ "$WITH_BLUEPRINT" = 1 ]; then
  if command -v claude >/dev/null; then
    step "commerce-builder plugin for Claude Code"
    claude plugin marketplace add "$BLUEPRINT_DIR" || true
    claude plugin install commerce-builder@claude-commerce-agents || true
  else
    printf '\nclaude CLI not found; skipping the commerce-builder plugin\n' >&2
  fi
fi

# --- what to run next -------------------------------------------------------
cat <<EOF

$(printf '\033[1mDone.\033[0m')

Merchant agent, no Shopify account needed (in-process store from merchant/data/seed.json):
  cd $SHOPIFY_DIR
  SHOPIFY_LOCAL_STORE=1 ./.venv/bin/uvicorn merchant.api.main:app --port 8005
  curl -X POST localhost:8005/api/merchant/session      # then /overview, /listings, /alerts

Storefront agent against a live store (needs outbound access to the shop's /.well-known/ucp):
  cd $SHOPIFY_DIR
  SHOP_DOMAIN=${SHOP:-your-store.com} ./.venv/bin/uvicorn storefront.api.main:app --port 8004
  npm run dev -w storefront/web                          # http://localhost:3005
EOF

if [ "$WITH_BLUEPRINT" = 1 ]; then
cat <<EOF

Blueprint demos on fixtures (no store, no network):
  cd $BLUEPRINT_DIR
  ./.venv/bin/python scripts/run_demo.py retail          # also: travel, telecom, entertainment
EOF
fi
