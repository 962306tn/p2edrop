#!/usr/bin/env bash
# Cai dat Meta Ads CLI chinh chu (PyPI: meta-ads, lenh: `meta`) + khoi tao ads/.env
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ADS_DIR="$REPO_ROOT/ads"

say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m[x]\033[0m %s\n' "$*" >&2; exit 1; }

# 1. uv (trinh cai dat Python tool cua Astral) -------------------------------
if ! command -v uv >/dev/null 2>&1; then
  say "Chua co uv, dang cai (curl -LsSf https://astral.sh/uv/install.sh | sh)"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
command -v uv >/dev/null 2>&1 || die "uv van chua co trong PATH. Them: export PATH=\"\$HOME/.local/bin:\$PATH\""

# 2. Python 3.12+ (yeu cau cua meta-ads) ------------------------------------
PY=""
for c in python3.13 python3.12; do
  if command -v "$c" >/dev/null 2>&1; then PY="$(command -v "$c")"; break; fi
done
if [ -z "$PY" ]; then
  say "Khong thay python3.12+, de uv tu tai ban 3.12"
  uv python install 3.12
  PY="3.12"
fi

# 3. Cai / cap nhat CLI -----------------------------------------------------
say "Cai meta-ads (Meta Ads CLI chinh chu) bang uv"
uv tool install meta-ads --python "$PY" --upgrade

export PATH="$HOME/.local/bin:$PATH"
command -v meta >/dev/null 2>&1 || die "Khong tim thay lenh 'meta'. Them \$HOME/.local/bin vao PATH roi chay lai."
say "Phien ban: $(meta --version 2>&1)"

# 4. File .env --------------------------------------------------------------
mkdir -p "$ADS_DIR"
if [ ! -f "$ADS_DIR/.env" ]; then
  cp "$ADS_DIR/.env.example" "$ADS_DIR/.env"
  warn "Da tao ads/.env tu mau. Dien ACCESS_TOKEN / AD_ACCOUNT_ID / PAGE_ID roi chay lai script nay."
else
  say "Da co ads/.env"
fi

# 5. Kiem tra ket noi -------------------------------------------------------
set +e
( cd "$ADS_DIR" && meta auth status )
say "Kiem tra token that su hop le (goi API):"
( cd "$ADS_DIR" && meta ads adaccount list --limit 5 )
RC=$?
set -e
if [ $RC -ne 0 ]; then
  warn "Chua goi duoc API. Kiem tra ACCESS_TOKEN (system user token) va quyen ads_management."
  warn "Luu y: 'meta auth status' chi kiem tra co token hay khong, KHONG kiem tra token con song."
else
  say "OK. Buoc tiep theo:"
  echo "   cd ads && meta ads page list        # lay PAGE_ID"
  echo "   cd ads && meta ads dataset list     # lay PIXEL_ID"
  echo "   python3 scripts/meta_ads_launch.py validate"
fi
