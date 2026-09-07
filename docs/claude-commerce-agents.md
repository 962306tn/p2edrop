# Claude Commerce Agents on Shopify

Anthropic published **Claude Commerce Agents** on 2 September 2026: an open
(Apache-2.0) blueprint for two agents, plus reference implementations in retail,
travel, telecom and ticketing. Shopify published its implementation of the same
blueprint the same day — the one that talks to a real store.

- Blueprint: <https://github.com/anthropics/commerce-agents>
- Shopify implementation: <https://github.com/Shopify/claude-for-commerce-examples>
- Announcement: <https://claude.com/blog/claude-for-commerce-agents>
- Webinar (10 Sep 2026): <https://www.anthropic.com/webinars/building-claude-commerce-agents>
- Shopify UCP docs: <https://shopify.dev/docs/agents>

The two agents:

| Agent | Who it serves | What it does |
|---|---|---|
| **Storefront (shopping)** | customers | searches the live catalog over [UCP](https://shopify.dev/docs/agents), builds a real cart, answers from the store's policies and FAQs, hands off to the store's own checkout |
| **Merchant** | staff | reads products, orders and inventory over the Admin GraphQL API, proposes changes, applies the ones an operator approves |

Neither places an order nor takes payment. `complete_checkout` is never called;
every merchant write is staged in a ledger and only applied by an explicit
`POST /api/merchant/changes/{id}/apply`. The Admin token is read once, in
`merchant/api/agent_config.py`, and never reaches the model, a route, or a log.

## Install

```bash
./scripts/setup-commerce-agents.sh --shop your-store.com
```

Clones both repositories next to this one, builds a virtualenv for each, installs
the Node workspaces, writes the `.env` files from their templates, runs the offline
test suite, and registers the `commerce-builder` plugin with Claude Code.

Flags: `--dir DIR` (where to clone), `--shop DOMAIN`, `--skip-blueprint`,
`--skip-plugin`. Needs Python 3.11+ and Node 22.

Then put your key in `claude-for-commerce-examples/.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
```

The key is the only thing the chat needs — the reads, the tests, and the local
store all run without it.

## Run

**Merchant agent, no Shopify account.** `SHOPIFY_LOCAL_STORE=1` swaps the Admin API
for `merchant/api/local_store.py`, an in-process store seeded from
`merchant/data/seed.json`:

```bash
cd ../claude-for-commerce-examples
SHOPIFY_LOCAL_STORE=1 ./.venv/bin/uvicorn merchant.api.main:app --port 8005

curl -X POST localhost:8005/api/merchant/session      # returns session_id
curl -H "X-Session-Id: <id>" localhost:8005/api/merchant/overview
```

Every read (`/overview`, `/listings`, `/alerts`, `/chat`) needs the session header;
without it the route answers *Start a session first*. This example ships no web UI —
`/api/merchant` is the whole surface, and the operator app is yours to build.

Against a real development store, put `SHOPIFY_SHOP_DOMAIN` and `SHOPIFY_ADMIN_TOKEN`
in `merchant/.env` instead, seed with `merchant/scripts/seed_store.py`, and check with
`merchant/scripts/smoke_live.py`. `merchant/README.md` lists the scope each read needs.

**Storefront agent against a live store.** `SHOP_DOMAIN` is any domain serving
`/.well-known/ucp`:

```bash
cd ../claude-for-commerce-examples
SHOP_DOMAIN=your-store.com ./.venv/bin/uvicorn storefront.api.main:app --port 8004
npm run dev -w storefront/web                          # http://localhost:3005
```

The web app brands itself from the store — name, logo, colors, best sellers — so the
same code is a storefront for any shop. `demostore.mock.shop` is Shopify's public demo
store and the default.

**Blueprint demos, no store and no network.** Four verticals on local fixtures:

```bash
cd ../commerce-agents
./.venv/bin/python scripts/run_demo.py retail          # travel, telecom, entertainment
```

Retail serves 87 fixture products on `http://localhost:3000`, API on `:8000`.

## Sign in with Shop (optional)

Set `SHOPIFY_UCP_CLIENT_ID` / `SHOPIFY_UCP_CLIENT_SECRET` from a
[Dev Dashboard](https://shopify.dev/docs/agents) app and `search_catalog` returns
personalized results. Without the pair the sign-in routes answer 503 and every session
is a guest — identical to running with no credentials. Buyer tokens are keyed by session
and never reach the model, the browser, or the logs.

Order tracking follows [Order MCP](https://shopify.dev/docs/agents/orders/order-mcp) v1:
only orders placed through the agent are visible, only when a buyer asks, and the
credential needs the `read_global_api_orders` scope. Without that scope the backend
disables its order tools and the agent points customers at the confirmation email.

## Building your own agent

The blueprint ships a Claude Code plugin, `commerce-builder` — six skills and four
commands. The setup script installs it; by hand it is:

```bash
claude plugin marketplace add anthropics/commerce-agents
claude plugin install commerce-builder@claude-commerce-agents
```

| Command | Does |
|---|---|
| `/scaffold-commerce-agent` | interviews you about your stack and scaffolds a shopping agent, a merchant agent, or both |
| `/add-commerce-flow <flow>` | adds one flow: copies its skill, wires its tools, writes its first eval cases |
| `/author-commerce-evals` | builds the eval suite and a replay gate for CI |
| `/review-commerce-agent` | maps an agent you already run against the reference, row by row |

The scaffold and the review write their decisions to your project's `CLAUDE.md` under
`## Commerce agent decision record`; the other two read that section instead of asking again.

Then wire the backend methods the scaffold stubbed (`docs/backends.md` in the blueprint),
read `docs/safety.md` for the fencing and gates a deployment owes its users, and deploy
per `docs/deployment.md` — Bedrock, Vertex AI, or Microsoft Foundry.

## Tests

```bash
cd ../claude-for-commerce-examples
SHOP_DOMAIN=demostore.mock.shop ./.venv/bin/python -m pytest -q     # 231 tests, no network
```

The storefront's tests replay `storefront/data/recorded_responses.json` through an
`httpx.MockTransport`. Pin `SHOP_DOMAIN` for the run: `test_health_and_session` asserts
the demo domain by name, so it fails against a `.env` pointing at your own store.

## If the storefront can't reach the shop

`httpx.ProxyError: 403 Forbidden` from `storefront/scripts/smoke.py` means the network
policy denied the shop's domain, not that the install is broken. In a Claude Code on the
web session the environment's network policy has to allow the store host — see
<https://code.claude.com/docs/en/claude-code-on-the-web>. The merchant example with
`SHOPIFY_LOCAL_STORE=1` and the blueprint demos need no outbound access at all.

## Alternative, no code

For a managed storefront agent on the online store, [Shopify Inbox](https://apps.shopify.com/inbox)
does it without any of the above.
