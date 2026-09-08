---
name: video-brief
description: Turn a marketing brief into ready-to-render video prompts and render them on Topview (Seedance, Veo, Kling) and Superscale. Use when the user drops a brief, product description, or angle list and wants ad videos, UGC clips, TOF/MOF/BOF creatives, or a batch of variants - in any language.
---

# Brief -> prompt pack -> rendered videos

The split that makes this work: **you write the creative, the scripts do the plumbing.**
Never hand-write task ids, poll loops, or per-scene JSON - `pipeline/` already does that,
and it is what keeps a re-run from paying twice for the same clip.

## Steps

### 1. Read the brief, fill the gaps

Needed before writing anything: brand + product, market, language, funnel stage,
formats and how many angles each, duration, aspect ratio, tone. Anything the brief
does not say, choose a sane default and state the choice in one line - do not
interrogate the user. Only ask when a wrong guess would waste render credits
(for example: language, or vertical vs square).

### 2. Write `plan.json`

Copy the shape of `pipeline/briefs/example-plan.json`. Rules that matter:

- One entry in `variants` per format x angle. `id` is `NN-short-slug`, unique.
- `hook` must land in the first 2 seconds and be a sentence a human would actually
  say. `backup_hook` is a genuinely different opening, not a paraphrase.
- 3-6 `scenes` per variant. Each scene: `visual` (what the camera sees - subject,
  place, time of day, action), plus `camera`, `duration`, `vo`, and `overlay` when
  there is burned-in text. Write visuals as shots, not as summaries of the message.
- Keep the brand promise out of the model prompt: no claims, no logos, no packaging
  text. Those belong in `caption`, `cta` and the captions burned in later.
- `style` and `negative_prompt` at plan level keep 10 variants looking like one campaign.
- Language: write `hook`, `vo`, `caption`, `cta` in the brief's target language;
  keep `visual`/`camera` in English - the video models are trained on English prompts.
- `defaults.model` must be a name Topview actually accepts - check
  `pipeline/models.json`, which also carries each model's allowed aspect ratios,
  resolutions (integer heights) and durations. Seedance 1.5 Pro is a good default
  for 9:16 ad work; Veo 3.1 when the scene needs native audio.
- A scene with a product photo gets `first_frame: <path>` and renders as
  image-to-video instead; the renderer uploads the file itself.

Validate as you go: `python3 pipeline/build_pack.py plan.json` fails loudly on a
malformed plan.

### 3. Build the pack

```bash
python3 pipeline/build_pack.py plan.json --out out/<slug>
```

Produces per variant: `script.md` (human review), `seedance.txt` (paste-into-UI
prompts), `topview.json` (API bodies), `superscale.json` (post-production hand-off),
plus `manifest.json` and `INDEX.md` for the whole pack.

### 4. Price it, then show before you spend

```bash
python3 pipeline/topview.py estimate out/<slug>/manifest.json
python3 pipeline/topview.py render out/<slug>/manifest.json --dry-run --limit 2
```

Show the user `INDEX.md`, one full variant `script.md`, and the credit estimate.
Rendering costs credits, so **get an explicit go-ahead before the first real
render**, and suggest `--only <variant>` for a single-variant test first. Never
pass `--yes` on the user's first run - that flag exists for unattended repeats.

### 5. Render

```bash
python3 pipeline/topview.py render out/<slug>/manifest.json --only 01-...   # test one
python3 pipeline/topview.py render out/<slug>/manifest.json                 # the rest
python3 pipeline/superscale.py assemble out/<slug>/manifest.json --run      # stitch
```

Resumable: task ids live in `out/<slug>/.state.json`. If a run times out or the
laptop sleeps, re-run the same command - it picks the tasks back up instead of
re-submitting. Failed clips stay failed until `--retry-failed`.

## Superscale, and when the Topview API is not available

Superscale has **no REST API** - it is MCP only. So the polished edit is something
you ask for in chat through its MCP server, handing it
`prompts/<variant>/superscale.json`. `superscale.py assemble --run` is the local
ffmpeg cut that does not need Superscale at all. Never write code that posts to a
Superscale REST endpoint; there isn't one.

Topview's Ultra and Team plans include MCP but not the REST API. If
`topview.py doctor` returns 403, do not keep retrying - switch to the Topview MCP
server (`/mcp` in Claude Code, see `docs/topview-superscale.md`) and drive rendering
through its tools, feeding it the prompts from `seedance.txt` one variant at a time.
The pack, the review step and the credit-consent rule stay exactly the same.

## Do not

- Do not invent endpoint paths, model names or field names. The verified ones are in
  `pipeline/providers.json` and `pipeline/models.json`; `topview.py doctor` checks
  credentials and prints the credit balance.
- Do not render every variant before the user has seen a single one.
- Do not put subtitles in the model prompt unless `overlay` asks for it - burned-in
  text is added in post, where it is legible and correct.
