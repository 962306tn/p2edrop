#!/usr/bin/env bash
# Register the ads-platform MCP servers (Meta, TikTok) with Claude Code.
#
# Usage:
#   ./scripts/setup-ads-mcp.sh                                  # Meta only
#   ./scripts/setup-ads-mcp.sh --tiktok <TIKTOK_MCP_URL>        # Meta + TikTok
#   ./scripts/setup-ads-mcp.sh --skip-meta --tiktok <URL>       # TikTok only
#   ./scripts/setup-ads-mcp.sh --scope project                  # default: user
#
# Meta's endpoint is a single public URL (https://mcp.facebook.com/ads), so it is
# hardcoded. TikTok issues its endpoint per account -- find it in
# TikTok Ads Manager -> Business API / MCP Server -- so you must pass it in.
#
# Adding a URL does NOT sign you in. Run /mcp inside Claude Code afterwards.
#
# See docs/ads-automation.md for the full walkthrough, including the guardrails
# you should have in place before letting an agent touch a live ad account.

set -euo pipefail

META_URL="https://mcp.facebook.com/ads"
META_NAME=meta-ads
TIKTOK_NAME=tiktok-ads
TIKTOK_URL=""
SCOPE=user
SKIP_META=0

die() { printf 'error: %s\n' "$1" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --tiktok)      [ $# -ge 2 ] || die "--tiktok needs a URL"; TIKTOK_URL=$2; shift 2 ;;
    --scope)       [ $# -ge 2 ] || die "--scope needs a value"; SCOPE=$2; shift 2 ;;
    --meta-url)    [ $# -ge 2 ] || die "--meta-url needs a value"; META_URL=$2; shift 2 ;;
    --skip-meta)   SKIP_META=1; shift ;;
    -h|--help)     sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)             die "unknown argument: $1" ;;
  esac
done

case "$SCOPE" in user|project|local) ;; *) die "--scope must be user, project or local" ;; esac
[ "$SKIP_META" = 1 ] && [ -z "$TIKTOK_URL" ] && die "nothing to do: --skip-meta with no --tiktok URL"

command -v claude >/dev/null 2>&1 || die "the 'claude' CLI is not on PATH; install Claude Code first"

# Validate every URL up front, so a bad second URL cannot leave the first server
# half-registered.
check_url() {
  case "$2" in https://*) ;; *) die "$1 URL must start with https:// (got: $2)" ;; esac
}
[ "$SKIP_META" = 1 ] || check_url Meta "$META_URL"
[ -z "$TIKTOK_URL" ] || check_url TikTok "$TIKTOK_URL"

register() {
  name=$1 url=$2

  # Re-running should update, not duplicate.
  if claude mcp get "$name" >/dev/null 2>&1; then
    printf 'note: MCP server "%s" already exists; removing it before re-adding.\n' "$name"
    claude mcp remove "$name" --scope "$SCOPE" >/dev/null 2>&1 \
      || claude mcp remove "$name" >/dev/null 2>&1 || true
  fi

  claude mcp add --transport http "$name" "$url" --scope "$SCOPE"
}

[ "$SKIP_META" = 1 ] || register "$META_NAME" "$META_URL"
[ -z "$TIKTOK_URL" ] || register "$TIKTOK_NAME" "$TIKTOK_URL"

if [ -z "$TIKTOK_URL" ] && [ "$SKIP_META" = 0 ]; then
  cat <<'MSG'

note: TikTok was skipped -- its endpoint is issued per account and has no default.
      Find it in TikTok Ads Manager -> Business API / MCP Server, then re-run:
        ./scripts/setup-ads-mcp.sh --skip-meta --tiktok https://<your-endpoint>
MSG
fi

printf '\nRegistered. Current servers:\n'
claude mcp list || true

cat <<MSG

Next step -- authenticate (the URL alone does not sign you in):

  1. Start Claude Code:            claude
  2. Run:                          /mcp
  3. Pick each ads server and complete the OAuth flow in the browser.
     Headless / SSH?               claude mcp login $META_NAME --no-browser
  4. Verify the tools loaded:      /mcp   (each server should read "connected")

Meta needs your Facebook account to hold an advertiser or admin role in the
Business Manager that owns the ad account -- OAuth succeeds without it, but
every tool then comes back empty.

Start read-only:
  "List my active campaigns with spend and ROAS for the last 7 days."

Only once that returns real numbers should you let it create anything -- and
read docs/ads-automation.md first. Campaigns are created PAUSED; keep it that way
and flip them live yourself.
MSG
