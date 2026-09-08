#!/usr/bin/env bash
# Register a Meta (Facebook/Instagram) Ads MCP server with Claude Code.
#
# Usage:
#   ./scripts/setup-meta-ads-mcp.sh                                  # Meta's official connector
#   ./scripts/setup-meta-ads-mcp.sh --provider pipeboard             # Pipeboard remote MCP
#   ./scripts/setup-meta-ads-mcp.sh --provider pipeboard --token <PIPEBOARD_API_TOKEN>
#
# Flags:
#   --provider official|pipeboard   which server to register (default: official)
#   --scope    user|project|local   where to store the entry  (default: user)
#   --name     <server-name>        override the MCP server name
#   --token    <token>              Pipeboard API token; skips the interactive login
#
# Providers:
#   official   https://mcp.facebook.com/ads      Meta's own AI Connector (open beta, free).
#              Meta Business OAuth, no developer app, no access token to manage.
#              29 tools: reporting, campaign management, catalogs, dataset diagnostics.
#   pipeboard  https://meta-ads.mcp.pipeboard.co/  Third-party (Meta Business Partner).
#              42 tools; adds creative upload, dynamic creative and richer targeting
#              lookups. Your ad data passes through Pipeboard's service.
#
# Both are remote HTTP servers: nothing runs on your machine and there is no
# long-lived Meta token stored in this repo.

set -euo pipefail

PROVIDER=official
SCOPE=user
NAME=""
TOKEN=""

die() { printf 'error: %s\n' "$1" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --provider) [ $# -ge 2 ] || die "--provider needs a value"; PROVIDER=$2; shift 2 ;;
    --scope)    [ $# -ge 2 ] || die "--scope needs a value";    SCOPE=$2;    shift 2 ;;
    --name)     [ $# -ge 2 ] || die "--name needs a value";     NAME=$2;     shift 2 ;;
    --token)    [ $# -ge 2 ] || die "--token needs a value";    TOKEN=$2;    shift 2 ;;
    -h|--help) sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) die "unknown flag: $1" ;;
    *)  die "unexpected argument: $1" ;;
  esac
done

case "$SCOPE" in user|project|local) ;; *) die "--scope must be user, project or local" ;; esac

case "$PROVIDER" in
  official)
    URL="https://mcp.facebook.com/ads"
    [ -n "$NAME" ] || NAME=meta-ads
    [ -z "$TOKEN" ] || die "--token only applies to --provider pipeboard; the official connector uses Meta Business OAuth"
    ;;
  pipeboard)
    URL="https://meta-ads.mcp.pipeboard.co/"
    [ -n "$NAME" ] || NAME=meta-ads-pipeboard
    # Pipeboard accepts the API token as a query parameter instead of the
    # browser login. It lands in the Claude Code config in clear text, so only
    # take this path when the caller explicitly asks for it.
    [ -z "$TOKEN" ] || URL="${URL}?token=${TOKEN}"
    ;;
  *) die "--provider must be official or pipeboard" ;;
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

if [ "$PROVIDER" = pipeboard ] && [ -n "$TOKEN" ]; then
  cat <<MSG

Registered with an inline Pipeboard token — treat the Claude Code config as a
secret from now on, and rotate the token at https://pipeboard.co/api-tokens if
it leaks.
MSG
fi

cat <<MSG

Next step — authenticate (adding the URL does not sign you in):

  1. Start Claude Code:            claude
  2. Run:                          /mcp
  3. Pick "$NAME" and finish the login in the browser.
MSG

if [ "$PROVIDER" = official ]; then
  cat <<'MSG'
     Sign in with the Facebook account that has access to the ad account, then
     pick the business portfolios you want to expose.
MSG
else
  cat <<'MSG'
     Log in to Pipeboard, then connect your Meta ad account to it.
MSG
fi

cat <<MSG
     Headless / SSH?               claude mcp login $NAME --no-browser
  4. Verify the tools loaded:      /mcp   (should read "connected")

Then try:  "List my Meta ad accounts, then show spend, CPM and ROAS by campaign for the last 7 days."

New campaigns are created PAUSED. Read back what the agent built in Ads Manager
before you set anything live.
MSG
