# Brief in, videos out: Topview + Superscale

## What each vendor actually exposes

Worth stating plainly, because it decides the whole design:

| | Topview | Superscale |
| --- | --- | --- |
| REST API | yes - `https://api.topview.ai` | **none.** `api.superscale.ai` does not resolve, and the docs publish no key, bearer or base url |
| MCP server | yes - `https://mcp.topview.ai/claude`, plus an official stdio server on npm | yes - `https://mcp.superscale.ai/mcp`, OAuth, Pro plan and up |
| Batch rendering from a brief | `pipeline/` calls the API directly | not possible headlessly - drive it from the chat |

So: **Topview renders, driven by the pipeline. Superscale finishes, driven by MCP.**
Anything that says otherwise is guessing.

## 1. Connect the MCP servers

```bash
./scripts/setup-topview-mcp.sh          # https://mcp.topview.ai/claude
./scripts/setup-superscale-mcp.sh       # https://mcp.superscale.ai/mcp
./scripts/setup-superscale-mcp.sh --docs   # docs knowledge base, no account needed
```

Adding a URL does not sign you in. Start Claude Code, run `/mcp`, pick the server,
finish the OAuth flow in the browser, then run `/mcp` again and confirm `connected`.
Headless: `claude mcp login <name> --no-browser`.

Superscale authenticates with OAuth 2.1 through Clerk - PKCE and dynamic client
registration - so there is no key to paste anywhere. A 401 that never clears
usually means the plan does not include MCP; it starts at Pro.

Topview also publishes an official stdio MCP server on npm if you would rather run
it locally than over HTTP:

```json
{ "mcpServers": { "topview-ai": {
    "command": "npx", "args": ["-y", "topview-ai-mcp"],
    "env": { "TOPVIEW_UID": "...", "TOPVIEW_API_KEY": "..." } } } }
```

## 2. Set up the Topview API for batch rendering

```bash
cp .env.example .env      # git-ignored
# TOPVIEW_API_KEY + TOPVIEW_UID from the Topview dashboard -> API Keys
python3 pipeline/topview.py doctor
```

`doctor` calls the account endpoint and prints your credit balance. If that
answers, the key, the uid and the base url are all correct. A 403 means the plan
has no API access (Ultra and Team are MCP-only) - use the MCP route instead.

Both headers go on every request: `Authorization: Bearer <key>` and
`Topview-Uid: <uid>`. Topview signals failure **inside** an HTTP 200 - the body is
`{code, message, result}` and `code` is the real status - so the pipeline reads
`code`, not the HTTP status, and turns `4100` into "not enough credits" rather
than a silent success.

Endpoints in use, all verified against Topview's own published client:

| task | submit |
| --- | --- |
| text to video | `POST /v1/common_task/text2video/task/submit` |
| image to video | `POST /v2/common_task/image2video/task/submit` (note: v2) |
| omni reference | `POST /v1/common_task/omni_reference/task/submit` |
| text to image | `POST /v1/common_task/text2image/task/submit` |
| image edit | `POST /v1/common_task/image_edit/task/submit` |

Each returns a `taskId`; the matching `/task/query?taskId=...` is polled until
`status` is `success`, and the file lands in `result.videos[].filePath`. A clip can
fail *inside* a task that reports success, so the pipeline checks both levels.

## 3. Run a brief

```bash
python3 pipeline/build_pack.py plan.json --out out/velahush-tof
python3 pipeline/topview.py estimate out/velahush-tof/manifest.json
python3 pipeline/topview.py render   out/velahush-tof/manifest.json --only 01-dog-owns-the-sofa
python3 pipeline/topview.py render   out/velahush-tof/manifest.json
python3 pipeline/superscale.py assemble out/velahush-tof/manifest.json --run
```

In a Claude Code session you type none of this - hand over the brief and the
`video-brief` skill walks the same path, writing `plan.json` for you and stopping
for your go-ahead before it spends credits.

`plan.json` is the creative layer: one entry per format x angle, each with a hook,
a backup hook, voiceover, caption, CTA and 3-6 scenes.
`pipeline/briefs/example-plan.json` is a working two-variant example, and
`example-brief.md` is the kind of input it was written from.

What lands in `out/<slug>/`:

```
INDEX.md                        one table, every variant, every hook
manifest.json                   the render jobs
prompts/<variant>/script.md     human review copy
prompts/<variant>/seedance.txt  flat prompts, paste straight into the Topview UI
prompts/<variant>/topview.json  the API bodies
prompts/<variant>/superscale.json  hand-off for the Superscale MCP
renders/<variant>/scene-NN.mp4
final/<variant>.mp4             after assemble.sh
.state.json                     task ids - why a re-run resumes instead of re-paying
```

### Models and cost

`pipeline/models.json` carries every model Topview exposes with its real
constraints and per-second credit rate, extracted from Topview's own package
rather than retyped. That buys three things:

- `estimate` tells you what a pack costs **before** you spend anything.
- `render` shows the total and your balance, and asks before the first submit
  (`--yes` skips it, `--dry-run` submits nothing at all).
- `build_pack` warns when a model does not support the aspect ratio, resolution or
  duration you asked for - a warning, not a block, because Topview ships models
  faster than any local table tracks. Unknown models are sent anyway.

Model names are display names, exactly as Topview writes them: `Seedance 1.5 Pro`,
`Veo 3.1`, `Kling V3`, `Wan 2.6`, `Vidu Q3 Pro`, `MiniMax-Hailuo-2.3`,
`Topview Pro`. Resolution is an integer height (`1080`, not `"1080p"`), duration is
in seconds, and `sound` is `"on"` or `"off"`.

### Flags worth knowing

| Flag | Why |
| --- | --- |
| `--dry-run` | print payloads and cost, submit nothing |
| `--only <variant>` | prove one variant looks right before paying for ten |
| `--limit N` | cap a run |
| `--yes` | skip the cost confirmation (for unattended runs) |
| `--retry-failed` | re-submit clips that failed; without it they stay skipped |

Concurrency is `max_concurrent_tasks` (default 3). Topview returns code `4007`
("an unfinished task already exists") if your plan allows fewer, so lower it rather
than fight it.

### Image-to-video

Give a scene a `first_frame` (and optionally `end_frame`) pointing at a local image
and the pipeline switches that clip to the v2 image-to-video endpoint, uploads the
file through Topview's three-step S3 flow, and submits the returned `fileId`. Useful
when the ad has to show the real product rather than a model's idea of it.

## 4. Superscale

There is no API to call, so the pipeline does not pretend otherwise. Two paths:

- **The finished cut, locally.** `superscale.py assemble ... --run` concatenates
  each variant's clips with ffmpeg into `final/<variant>.mp4`. Re-encodes rather
  than stream-copies, because clips from different models carry different codecs.
- **The polished edit, via MCP.** Each variant has a `superscale.json` hand-off -
  clips, hook, caption, CTA, overlays, aspect ratio. Connect the MCP server and
  ask for the edit in chat, pointing at those files.

## Troubleshooting

| Symptom | Meaning |
| --- | --- |
| `401 from Topview` | key or uid wrong - both headers are required |
| `Topview [4100] Credit not enough` | out of credits; `estimate` first next time |
| `Topview [4007]` | plan allows fewer parallel tasks - lower `max_concurrent_tasks` |
| `Topview [6001]` | the prompt tripped Topview's safety check - rewrite that scene |
| `403` on every call | plan has no API access (Ultra/Team) - use MCP |
| a run timed out | task ids are in `.state.json`; re-run the same command to resume |
| Superscale MCP stays 401 | MCP starts at the Pro plan |
| works locally, not on Claude Code web | remote sessions run behind an egress proxy and `api.topview.ai` is not allowlisted - render locally |

## References

- Topview: [API getting started](https://docs.topview.ai/docs/getting-started) · [OpenAPI overview](https://www.topview.ai/openapi) · [MCP](https://www.topview.ai/mcp)
- Topview's official client, the source of the verified endpoints: [`topview-ai-mcp` on npm](https://www.npmjs.com/package/topview-ai-mcp)
- Superscale: [Superscale for Agents](https://docs.superscale.ai/integrations/superscale-for-agents) · [quickstart](https://docs.superscale.ai/getting-started/quickstart)
- Independent audit confirming Superscale has MCP but no REST API: [api-evangelist/superscale](https://github.com/api-evangelist/superscale)
- Claude Code: [Connect to tools via MCP](https://code.claude.com/docs/en/mcp)
