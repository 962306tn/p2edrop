#!/usr/bin/env bash
# Register the Topview MCP server with Claude Code.
#
# Usage:
#   ./scripts/setup-topview-mcp.sh                       # official endpoint
#   ./scripts/setup-topview-mcp.sh <MCP_URL>             # override it
#   ./scripts/setup-topview-mcp.sh --scope project
#
# Unlike GemPages, Topview publishes one shared endpoint - no waitlist, no
# per-account URL - so it is the default here. Authentication is OAuth in the
# browser, the same as any remote MCP server.
#
# MCP is included on Topview's Pro, Business, Ultra and Team plans. The REST API
# (what pipeline/topview.py uses for batch rendering) is Pro and Business only.

set -euo pipefail

NAME=topview
SCOPE=user
URL=https://mcp.topview.ai/claude

die() { printf 'error: %s\n' "$1" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --scope) [ $# -ge 2 ] || die "--scope needs a value"; SCOPE=$2; shift 2 ;;
    --name)  [ $# -ge 2 ] || die "--name needs a value";  NAME=$2;  shift 2 ;;
    -h|--help) sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) die "unknown flag: $1" ;;
    *)  URL=$1; shift ;;
  esac
done

case "$SCOPE" in user|project|local) ;; *) die "--scope must be user, project or local" ;; esac
case "$URL" in https://*) ;; *) die "URL must start with https:// (got: $URL)" ;; esac

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

Next step - authenticate (the URL alone does not sign you in):

  1. Start Claude Code:            claude
  2. Run:                          /mcp
  3. Pick "$NAME" and complete the OAuth flow in the browser.
     Headless / SSH?               claude mcp login $NAME --no-browser
  4. Verify the tools loaded:      /mcp   (should show "$NAME" as connected)

Then try:  "Generate a 9:16 Seedance clip: <one scene description>."

For batch work from a brief, use the pipeline instead - it is resumable and does
not depend on the chat staying open:

  python3 pipeline/build_pack.py plan.json --out out/<slug>
  python3 pipeline/topview.py render out/<slug>/manifest.json
MSG
