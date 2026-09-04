# Connecting GemPages MCP to Claude Code

GemPages MCP (server name: **GemCommerce MCP**) lets an AI agent read and build
GemPages landing pages and talk to the connected Shopify store from inside a chat.
It is a **remote MCP server over streamable HTTP with OAuth**.

## Before you start

GemPages MCP is in **beta behind a waitlist**. You need:

1. GemPages installed on your Shopify store.
2. Access to the MCP beta (waitlist approval).
3. Your account's MCP endpoint URL — it is **issued per account**, there is no
   shared public URL. Find it at:

   > Shopify admin → GemPages → **Preferences → MCP Connection**

   (the same panel also gives you a ready-made connection prompt). It is also in
   the beta acceptance email.

## Setup

```bash
./scripts/setup-gempages-mcp.sh https://<your-gempages-mcp-endpoint>
```

The script registers the server at **user scope**, so it is available in every
project, then prints the authentication steps. Re-running it updates the existing
entry instead of creating a duplicate.

Equivalent by hand:

```bash
claude mcp add --transport http gempages https://<your-gempages-mcp-endpoint> --scope user
```

## Authenticate

Adding the URL does **not** sign you in. In a Claude Code session:

```
/mcp
```

Pick `gempages`, complete the OAuth flow in the browser, then run `/mcp` again —
it should read `connected` and the GemPages tools appear in the tool list.

No browser (SSH / headless)?

```bash
claude mcp login gempages --no-browser
```

Then grant the tool permissions GemPages asks for. Their docs recommend setting the
required permissions to **Always allow** so multi-step page edits don't stall on a
prompt for every call.

Useful commands:

| Command | What it does |
| --- | --- |
| `claude mcp list` | list servers and their health |
| `claude mcp get gempages` | show scope, type, URL, auth status |
| `claude mcp logout gempages` | clear stored OAuth credentials |
| `claude mcp remove gempages -s user` | unregister |

## Per-project instead of per-user

If you would rather commit the config so teammates pick it up from the repo, copy
`.mcp.json.example` to `.mcp.json` and export the URL in your shell:

```bash
cp .mcp.json.example .mcp.json
export GEMPAGES_MCP_URL=https://<your-gempages-mcp-endpoint>   # add to ~/.zshrc or ~/.bashrc
```

`.mcp.json` supports `${VAR}` expansion in `url` and `headers`, so the endpoint
stays out of git. Claude Code asks for approval the first time it loads a
project-scoped `.mcp.json`.

Use **either** user scope **or** project scope — registering the same name in both
is confusing to debug.

## Connect a store

Authenticating the MCP server is not the same as connecting a store to it. GemPages
issues a **store connection code** shaped like `GC-######` (Shopify admin → GemPages →
Preferences → MCP Connection, next to the endpoint URL).

Once `/mcp` reports `gempages` as connected, hand the code to the agent in the session:

```
Connect a new store in GemCommerce MCP. Code: GC-XXXXXX
```

The MCP server exposes its own store-connection tool; the agent picks it up from the
tool list once the server is authenticated. If nothing happens, run `/mcp` and confirm
`gempages` is `connected` rather than `Needs authentication` — an unauthenticated
server loads no tools at all, so the code has nowhere to go.

Treat the code like a credential: do not commit it.

## Smoke test

```
Use GemPages MCP to research content for <product> for the <market> market.
```

## Troubleshooting

- **`has a "url" but no "type"`** — the `.mcp.json` entry is missing
  `"type": "http"`; Claude Code falls back to treating it as a stdio server.
- **Stuck on "Needs authentication"** — you added the URL but never ran `/mcp`.
- **OAuth callback fails to redirect** — copy the full callback URL from the
  browser address bar and paste it into the prompt in Claude Code. A fixed port
  helps behind strict firewalls: `claude mcp add --transport http --callback-port 8080 ...`
- **Works locally but not in Claude Code on the web** — remote sessions run behind
  an egress proxy. If `gempages.net` is not allowlisted for that environment, the
  MCP cannot be reached from there; use local Claude Code.

## References

- GemPages: [Getting Started with GemPages MCP](https://help.gempages.net/articles/introduction-to-gempages-mcp)
- GemPages: [Using GemPages MCP for Content Research](https://help.gempages.net/articles/gempages-mcp-content-research)
- Claude Code: [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)
- Anthropic: [Custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)
