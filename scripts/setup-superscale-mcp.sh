#!/usr/bin/env bash
# Register the Superscale MCP server with Claude Code.
#
# Usage:
#   ./scripts/setup-superscale-mcp.sh                    # product MCP (needs Pro plan and up)
#   ./scripts/setup-superscale-mcp.sh --docs             # docs MCP, no account needed
#   ./scripts/setup-superscale-mcp.sh <MCP_URL> [--scope project]
#
# Superscale ships no REST API - api.superscale.ai does not resolve, and the
# docs publish no API key or base url. MCP is the whole integration surface.
#
# Auth is OAuth 2.1 through Clerk with PKCE and dynamic client registration, so
# there is no key to paste: /mcp opens a browser and Claude Code registers itself.

set -euo pipefail

NAME=superscale
SCOPE=user
URL=https://mcp.superscale.ai/mcp

die() { printf 'error: %s\n' "$1" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --docs)  NAME=superscale-docs; URL=https://docs.superscale.ai/mcp; shift ;;
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

if claude mcp get "$NAME" >/dev/null 2>&1; then
  printf 'note: MCP server "%s" already exists; removing it before re-adding.\n' "$NAME"
  claude mcp remove "$NAME" --scope "$SCOPE" >/dev/null 2>&1 || claude mcp remove "$NAME" >/dev/null 2>&1 || true
fi

claude mcp add --transport http "$NAME" "$URL" --scope "$SCOPE"

printf '\nRegistered. Current servers:\n'
claude mcp list || true

cat <<MSG

Next step - authenticate (the docs server needs no login; the product one does):

  1. Start Claude Code:            claude
  2. Run:                          /mcp
  3. Pick "$NAME" and complete the OAuth flow in the browser.
     Headless / SSH?               claude mcp login $NAME --no-browser
  4. Verify the tools loaded:      /mcp   (should show "$NAME" as connected)

A 401 that never resolves usually means the plan does not include MCP - it is
Pro and above. The clips rendered by pipeline/ are still yours either way:
  python3 pipeline/superscale.py assemble out/<slug>/manifest.json --run
MSG
