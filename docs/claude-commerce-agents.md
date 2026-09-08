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

## Configured for all vibes space

```bash
./scripts/configure-commerce-agents.sh --check
```

Copies four files from `config/commerce-agents/` into the checkout and runs its suite:

| From | To | Holds |
|---|---|---|
| `root.env` | `.env` | `SHOP_DOMAIN=yxciec-f7.myshopify.com`, the hero tagline |
| `merchant.env` | `merchant/.env` | the shop domain, store name, `SHOPIFY_LOW_STOCK_DEFAULT=5`, `MERCHANT_REQUIRE_HOST_APPROVAL=1` |
| `thresholds.json` | `merchant/data/thresholds.json` | low-stock thresholds for the two product types |
| `storefront_agent_config.py` | `storefront/api/agent_config.py` | brand voice, and search notes for the scent and bundle axes |

The two `.env` files are merged, not overwritten. The rule is one line of the script: the
template owns every setting it states, and a key the template ships **blank** keeps whatever
the checkout already has. That blank set is exactly the credentials, so re-running never
costs you a pasted key and never leaves a stale shop domain behind.

Nothing in `config/commerce-agents/` is a secret; all four files are committed. Every
credential lives in the checkout's own gitignored `.env` files.

Two edits were deliberately *not* made, because the reference's own tests assert the values:

- `thresholds.json` keeps ACME's `Workshop tools`, `Storage`, and `canvas-tool-apron`
  entries alongside this store's. They match no product here and keep three tests in
  `merchant/api/tests/test_reads.py` green.
- `slow_mover_min_stock` stays at 12. With no order history, that reports every listing as a
  slow mover on day one; raising it to about 60 while pre-launch silences that and fails
  those same three tests. The file says so beside the value — change it deliberately.

### What is still yours to do

The merchant agent needs an app on the store. Four steps, the first three in the
[Shopify Dev Dashboard](https://shopify.dev/docs/apps/build/dev-dashboard/create-apps-using-dev-dashboard):

1. Create the app.
2. Put the scopes below on a version and release it. Scopes come from the *released*
   version, so adding one later means releasing again and re-approving on the store.
3. Install the app on the store and approve the scopes, then copy the client ID and secret
   from its Settings.
4. Put them in `merchant/.env` as `SHOPIFY_CLIENT_ID` and `SHOPIFY_CLIENT_SECRET`, and set
   `SHOPIFY_OPERATOR` to whoever the change ledger should stamp.

| Scope | What needs it |
|---|---|
| `read_products`, `write_products` | catalog reads; price and content writes |
| `read_inventory`, `write_inventory` | stock levels and restocks |
| `read_orders` | the order scan behind metrics, demand signals, and order issues |
| `read_locations` | the location an inventory move applies at |
| `read_reports` | ShopifyQL metrics — optional, `SHOPIFY_DISABLE_SHOPIFYQL=1` derives them from the order scan instead |
| `read_marketing_events` | `get_campaign_performance` — optional; without it the tool reports it cannot read rather than returning a zero |

There is no token to paste and none to replace tomorrow: `merchant/api/admin_token.py` mints
a 24-hour Admin token from the client ID and secret and mints another when it runs out. The
secret is a password for every scope the app was granted; it is read once, in
`merchant/api/agent_config.py`, and never reaches the model, a route, a log, or an error
message.

Also still open: `ANTHROPIC_API_KEY` in both `.env` files, and whether the storefront serves
`/.well-known/ucp`. The storefront agent needs that endpoint; the merchant agent does not.

### This is a live store, not a development store

The reference tells you to use a development store, because an approved change writes to the
real catalog. all vibes space is a live Advanced-plan store with three products, so:

- `MERCHANT_REQUIRE_HOST_APPROVAL=1` stays on. A chat turn that calls `apply_change` is held
  on the approval gate; the change moves only when the host calls
  `POST /api/merchant/changes/{id}/apply`. Staging sends no Admin mutation at all — the
  suite asserts zero mutations on every staging path.
- Run `SHOPIFY_LOCAL_STORE=1` first. Same backend, same documents, same stage-approve-apply
  path, against an in-process store. Nothing leaves the machine.
- Then `merchant/scripts/smoke_live.py --read-only` against the real store before anything
  writes. Without `--read-only` it makes one reversible price write and puts it back.

### Where it stands now

Configured and green: 231 tests pass with these files in place. The merchant host boots
against `yxciec-f7.myshopify.com` and `/api/merchant/health` reports the credentials as
missing, which is the documented state until the app exists.

Not verified against the live store from this session: the environment's network policy
denies outbound access to the shop's domain (a 403 on CONNECT), so no read has actually run
against all vibes space here. Run the two smoke checks above from a machine that can reach
the store.

One thing worth knowing before reading the merchant agent's first answer: the store has no
orders yet. Every metric derived from the order scan will be empty or `None` with a note,
which is the backend behaving correctly, not a wiring fault.

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
