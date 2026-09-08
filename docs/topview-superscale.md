# Brief in, videos out: Topview + Superscale

Two ways to drive Topview, and you want both for different jobs:

| | Topview MCP | Topview REST API (`pipeline/`) |
| --- | --- | --- |
| Feels like | chatting - "make me a clip of..." | a build - one command, 30 clips |
| Good for | one-offs, iterating on a shot, storyboards | a brief that fans out into variants |
| Survives a closed chat | no | yes, resumable from `.state.json` |
| Plans | Pro, Business, Ultra, Team | **Pro and Business only** |

The pipeline is the part that answers "gen automatically when I hand over a brief".
MCP is the part that answers "let me poke at one shot until it looks right".

## 1. Connect the MCP server

```bash
./scripts/setup-topview-mcp.sh
```

That registers `https://mcp.topview.ai/claude` at user scope. Adding the URL does
not sign you in - start Claude Code, run `/mcp`, pick `topview`, finish the OAuth
flow in the browser, then run `/mcp` again and confirm it reads `connected`.

Headless: `claude mcp login topview --no-browser`.

Prefer to commit the config for a team? `cp .mcp.json.example .mcp.json` - it now
carries both `gempages` and `topview`. Use either user scope or project scope for a
given server, not both.

## 2. Set up the API for batch rendering

```bash
cp .env.example .env      # git-ignored
# TOPVIEW_API_KEY + TOPVIEW_UID from the Topview dashboard -> API Keys
python3 pipeline/topview.py doctor
```

`doctor` sends a deliberately empty body to each candidate endpoint and reads the
answer for you:

- **400 / 422** - the path is right, it is only rejecting the empty body. This is
  the result you want.
- **401** - key wrong or missing.
- **403** - the key has no API access. You are on Ultra or Team; use MCP instead.
- **404** - wrong path. Put whichever candidate returned 400 into
  `pipeline/providers.json` under `topview.modules.video_gen.submit`.

Why the probe exists: Topview's documented shape - base `https://api.topview.ai`,
headers `Authorization: Bearer <key>` and `Topview-Uid: <uid>`, then
`POST /v1/<module>/task/submit` returning a `taskId` you poll at
`/v1/<module>/task/query` - is stable and confirmed for `url2video`,
`video_avatar` and the `common_task/*` family. The exact module name for plain
text/image-to-video generation is the one thing this repo could not verify from
public docs, so it is configuration with a self-check rather than a hardcoded guess.

Nothing else in the pipeline hardcodes an endpoint or a field name; even the JSON
body keys are a mapping in `providers.json` (`payload_keys`), so a renamed field is
a config edit.

## 3. Run a brief

```bash
python3 pipeline/build_pack.py plan.json --out out/velahush-tof
python3 pipeline/topview.py render out/velahush-tof/manifest.json --dry-run
python3 pipeline/topview.py render out/velahush-tof/manifest.json --only 01-dog-owns-the-sofa
python3 pipeline/topview.py render out/velahush-tof/manifest.json
python3 pipeline/superscale.py push out/velahush-tof/manifest.json
```

In a Claude Code session you do not type any of this - hand over the brief and the
`video-brief` skill (`.claude/skills/video-brief/`) walks the same path, writing
`plan.json` for you and stopping for your go-ahead before it spends credits.

`plan.json` is the creative layer: one entry per format x angle, each with a hook,
a backup hook, voiceover, caption, CTA and 3-6 scenes.
`pipeline/briefs/example-plan.json` is a working two-variant example, and
`example-brief.md` is the kind of input it was written from.

What lands in `out/<slug>/`:

```
INDEX.md                      one table, every variant, every hook
manifest.json                 the render jobs
prompts/<variant>/script.md   human review copy
prompts/<variant>/seedance.txt  flat prompts, paste straight into the Topview UI
prompts/<variant>/topview.json  the API bodies
prompts/<variant>/superscale.json  post-production hand-off
renders/<variant>/scene-NN.mp4
final/<variant>.mp4           after the Superscale pass or assemble.sh
.state.json                   task ids - why a re-run resumes instead of re-paying
```

### Flags worth knowing

| Flag | Why |
| --- | --- |
| `--dry-run` | print payloads, submit nothing, spend nothing |
| `--only <variant>` | prove one variant looks right before paying for ten |
| `--limit N` | cap a run |
| `--retry-failed` | re-submit clips that failed; without it they stay skipped |
| `--config <path>` | point at a different `providers.json` |

Concurrency is `topview.max_concurrent_tasks` (default 3) - raise it to match your
plan's concurrency limit, not above it, or submits start getting rejected.

## 4. Superscale

Superscale ships **disabled**: it documents its product at `docs.superscale.ai` but
does not publish a REST surface stable enough to hardcode, and a wrong guess here
would fail silently mid-campaign rather than loudly at setup.

So the pipeline gives you two honest paths:

- **Manual (default).** Every variant gets `prompts/<variant>/superscale.json` -
  clips, hook, caption, CTA, overlays, aspect ratio - to drop into the Superscale
  UI. `superscale.py push` also writes `out/<slug>/assemble.sh`, which concatenates
  that variant's clips locally with ffmpeg, so a brief still ends as a watchable
  cut with no second vendor involved.
- **API.** If your account exposes one, fill `base_url`, `paths.submit`,
  `paths.query` and `api_key_env` under `superscale` in `pipeline/providers.json`,
  set `"enabled": true`, export `SUPERSCALE_API_KEY`, and re-run `push`. Each
  variant goes up as one job carrying the rendered clip URLs. `superscale.py check`
  tells you whether the config is complete before you rely on it.

## Troubleshooting

- **`403` on every endpoint in `doctor`** - Ultra/Team plan. MCP works; the REST API
  does not. Use the MCP route in step 1.
- **`no task id in submit response`** - the path answered but the response shape is
  different from what `task_id_keys` lists. Add the key it actually uses to
  `providers.json`.
- **`task succeeded but no asset url`** - same idea for the output: the pipeline
  looks for any `http(s)` URL ending in a media extension. If your response hands
  back a bare id instead, that module needs a download step adding.
- **A run timed out** - task ids are already in `.state.json`. Re-run the same
  command; it resumes. Nothing is submitted twice.
- **Everything is slow / submits rejected** - lower `max_concurrent_tasks`.
- **Works locally, not in Claude Code on the web** - remote sessions run behind an
  egress proxy, and `api.topview.ai` and `docs.topview.ai` are not on its allowlist.
  Render from local Claude Code or your own machine.

## References

- Topview: [Getting started with the API](https://docs.topview.ai/docs/getting-started)
- Topview: [One API for every AI video and image model](https://www.topview.ai/openapi)
- Topview: [MCP for marketing workflows](https://www.topview.ai/mcp)
- Superscale: [Quickstart](https://docs.superscale.ai/getting-started/quickstart)
- Claude Code: [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)
