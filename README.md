# p2edrop

Tooling that connects the services behind a dropshipping workflow to Claude Code.

| What | Where |
| --- | --- |
| Landing pages on Shopify via GemPages MCP | [`docs/gempages-mcp.md`](docs/gempages-mcp.md) |
| Brief -> ad videos via Topview + Superscale | [`docs/topview-superscale.md`](docs/topview-superscale.md) |

Topview renders (REST API + MCP); Superscale finishes (MCP only - it ships no REST API).

```bash
./scripts/setup-gempages-mcp.sh https://<your-gempages-mcp-endpoint>
./scripts/setup-topview-mcp.sh
./scripts/setup-superscale-mcp.sh

cp .env.example .env            # Topview API key + uid, for batch rendering
python3 pipeline/topview.py doctor      # checks auth, prints your credit balance
```

Then hand Claude a brief - the `video-brief` skill turns it into a prompt pack and
renders it. `python3 pipeline/build_pack.py pipeline/briefs/example-plan.json` shows
the shape without touching the network.

Nothing here needs pip: the pipeline is Python 3.9+ stdlib only.
