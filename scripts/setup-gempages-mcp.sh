#!/usr/bin/env bash
# Register the GemPages (GemCommerce) MCP server with Claude Code.
#
# Usage:
#   ./scripts/setup-gempages-mcp.sh <MCP_URL> [--scope user|project|local] [--name gempages]
#
# Where to get <MCP_URL>:
#   Shopify admin -> GemPages -> Preferences -> MCP Connection
#   (or the acceptance email from the GemPages MCP beta waitlist)
#
# GemPages MCP is in beta behind a waitlist; the URL is issued per account,
# so it is not hardcoded here.

set -euo pipefail

NAME=gempages
SCOPE=user
URL=""

die() { printf 'error: %s\n' "$1" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --scope) [ $# -ge 2 ] || die "--scope needs a value"; SCOPE=$2; shift 2 ;;
    --name)  [ $# -ge 2 ] || die "--name needs a value";  NAME=$2;  shift 2 ;;
    -h|--help) sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) die "unknown flag: $1" ;;
    *)  [ -z "$URL" ] || die "unexpected argument: $1"; URL=$1; shift ;;
  esac
done

case "$SCOPE" in user|project|local) ;; *) die "--scope must be user, project or local" ;; esac

if [ -z "$URL" ]; then
  cat >&2 <<'MSG'
error: missing MCP server URL.

Get it from: Shopify admin -> GemPages -> Preferences -> MCP Connection
Then run:    ./scripts/setup-gempages-mcp.sh https://<your-gempages-mcp-endpoint>
MSG
  exit 2
fi

case "$URL" in
  https://*) ;;
  *) die "URL must start with https:// (got: $URL)" ;;
esac

command -v claude >/dev/null 2>&1 || die "the 'claude' CLI is not on PATH; install Claude Code first"

# Re-running should update, not duplicate.
if claude mcp get "$NAME" >/dev/null 2>&1; then
  printf 'note: MCP server "%s" already exists; removing it before re-adding.\n' "$NAME"
  claude mcp remove "$NAME" --scope "$SCOPE" >/dev/null 2>&1 || claude mcp remove "$NAME" >/dev/null 2>&1 || true
fi

claude mcp add --transport http "$NAME" "$URL" --scope "$SCOPE"

printf '\nRegistered. Current servers:\n'
claude mcp list || true

cat <<MSG

Next step — authenticate (the URL alone does not sign you in):

  1. Start Claude Code:            claude
  2. Run:                          /mcp
  3. Pick "$NAME" and complete the OAuth flow in the browser.
     Headless / SSH?               claude mcp login $NAME --no-browser
  4. Verify the tools loaded:      /mcp   (should show "$NAME" as connected)

Then try:  "Use GemPages MCP to research content for <product> in the <market> market."
MSG
