# Connecting Meta (Facebook/Instagram) Ads MCP to Claude Code

This connects Claude Code to your Meta ad account so it can **pull reporting**
(spend, CPM, CPA, ROAS, breakdowns) and **build campaigns** (campaign → ad set →
ad, budgets, status) from a chat.

Two servers are supported. Both are **remote HTTP MCP servers with OAuth**, so
nothing runs on your machine and no long-lived Meta token is stored in this repo.

| | `official` (default) | `pipeboard` |
| --- | --- | --- |
| Endpoint | `https://mcp.facebook.com/ads` | `https://meta-ads.mcp.pipeboard.co/` |
| Who runs it | Meta (first-party) | Pipeboard, a badged Meta Business Partner |
| Auth | Meta Business OAuth — same login as Ads Manager | Pipeboard login, then connect your ad account |
| Tools | 29 — reporting, campaign management, catalogs, dataset diagnostics | 42 — adds image/creative upload, dynamic creative, richer targeting lookups |
| Where your data goes | Meta only | through Pipeboard's service |
| Price | Free (open beta) | Free plan, then paid tiers |

Start with `official`: it is first-party, so your ad data and credentials never
leave Meta. Reach for `pipeboard` only if you need creative upload or the
targeting-search tools the official server does not expose.

## Before you start

- A Facebook account with access to the ad account, via a **business portfolio**
  in Meta Business Manager.
- No developer app, no App Review, no access token to generate — the official
  connector uses the same login as Ads Manager.
- Meta is rolling the connector out in phases. A successful OAuth flow does
  **not** guarantee every business portfolio has it enabled yet.

## Setup

```bash
./scripts/setup-meta-ads-mcp.sh                        # Meta's official connector
./scripts/setup-meta-ads-mcp.sh --provider pipeboard   # Pipeboard instead
```

The script registers the server at **user scope**, so it is available in every
project, then prints the authentication steps. Re-running it updates the existing
entry instead of creating a duplicate.

Equivalent by hand:

```bash
claude mcp add --transport http meta-ads https://mcp.facebook.com/ads --scope user
```

## Authenticate

Adding the URL does **not** sign you in. In a Claude Code session:

```
/mcp
```

Pick `meta-ads`, complete the login in the browser — sign in with Facebook, then
**select the business portfolios** you want to expose — and run `/mcp` again. It
should read `connected` and the Meta Ads tools appear in the tool list.

No browser (SSH / headless)?

```bash
claude mcp login meta-ads --no-browser
```

Useful commands:

| Command | What it does |
| --- | --- |
| `claude mcp list` | list servers and their health |
| `claude mcp get meta-ads` | show scope, type, URL, auth status |
| `claude mcp logout meta-ads` | clear stored OAuth credentials |
| `claude mcp remove meta-ads -s user` | unregister |

## Smoke test

Read first — it costs nothing and proves the connection:

```
List my Meta ad accounts, then show spend, CPM, CTR and ROAS by campaign
for the last 7 days.
```

Then a write, which lands paused:

```
Create a PAUSED sales campaign named "Test - <product>" in <account>,
one ad set at 200k VND/day targeting <audience>, and stop before creating the ad.
```

## Spending safety

The agent can move real money. A few habits that keep that boring:

- **Campaigns are created `PAUSED` by default.** Leave it that way, and activate
  from Ads Manager once you have read back what was built.
- **Do not blanket-approve the write tools.** Keep `create` / `update` /
  `activate` on per-call approval; "Always allow" is fine for the reporting ones.
- **Check the budget unit.** The Marketing API takes budgets in *cents* of the
  account currency, so `daily_budget: 200000` on a VND account is 2 000 VND, not
  200 000. State the amount in words and have the agent read the campaign back.
- **Say which ad account.** With several portfolios connected, name the
  `act_XXXXXXXXX` in the prompt rather than letting it pick.
- Revoke access any time under Facebook → Settings → **Business integrations**.

## Per-project instead of per-user

To commit the config so it is picked up from the repo, copy `.mcp.json.example`
to `.mcp.json`. The Meta endpoint is public and carries no secret, so it can be
hardcoded there. Claude Code asks for approval the first time it loads a
project-scoped `.mcp.json`.

Use **either** user scope **or** project scope — registering the same name in
both is confusing to debug.

## Troubleshooting

- **`has a "url" but no "type"`** — the `.mcp.json` entry is missing
  `"type": "http"`; Claude Code falls back to treating it as a stdio server.
- **Stuck on "Needs authentication"** — you added the URL but never ran `/mcp`.
- **Connected, but no ad accounts / empty results** — the business portfolio was
  not ticked during OAuth, or the phased rollout has not reached it. Re-run the
  login and check the portfolio selection.
- **`(#100) Invalid parameter` on campaign creation** — objectives must be the
  outcome-based (ODAX) values: `OUTCOME_SALES`, `OUTCOME_TRAFFIC`,
  `OUTCOME_LEADS`, `OUTCOME_ENGAGEMENT`, `OUTCOME_AWARENESS`,
  `OUTCOME_APP_PROMOTION`. Legacy ones like `CONVERSIONS` or `LINK_CLICKS` are
  rejected.
- **Works locally but not in Claude Code on the web** — remote sessions run
  behind an egress proxy, and `facebook.com` / `pipeboard.co` are not
  allowlisted there, so the MCP is unreachable from a web session. Use local
  Claude Code for anything touching Meta Ads.

## References

- Meta for Business: [Introducing Meta Ads AI Connectors](https://www.facebook.com/business/news/meta-ads-ai-connectors)
- Meta: [Marketing API — AI Connectors](https://developers.facebook.com/docs/marketing-api/ai-connectors)
- Pipeboard: [meta-ads-mcp](https://github.com/pipeboard-co/meta-ads-mcp)
- Claude Code: [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)
