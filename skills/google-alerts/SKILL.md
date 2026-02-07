---
name: google-alerts
description: Ingest Google Alerts RSS feeds, optionally filter and score items with Google GenAI using YAML-defined prompts, generate one global summary, and produce Google Chat webhook JSON payloads.
---

# Google Alerts

Automate Google Alerts monitoring from RSS feeds and transform results into a structured Google Chat payload.

## What This Skill Does

- Reads one YAML config with RSS sources and prompts.
- Pulls entries from each Google Alerts feed.
- Resolves Google redirect links to the original news URL.
- Downloads each article asynchronously and converts it to Markdown.
- Keeps only items with successful fetch + Markdown extraction (skips 404/errors).
- Optionally scores and filters entries with Google GenAI.
- Summarizes all selected news globally with one prompt.
- Builds Google Chat JSON with:
  - A global summary section.
  - A collapsible section per source with header `Source (N)`.
  - A title-only clickable list for each source.

## Files

- `scripts/google_alerts_to_chat.py`: CLI script.
- `assets/config.example.yaml`: starter config.

## Requirements

Set environment variable:

```bash
export GOOGLE_API_KEY="your_api_key"
```

## Quick Start

```bash
# Dry run: print JSON to stdout
uv run skills/google-alerts/scripts/google_alerts_to_chat.py \
  --config skills/google-alerts/assets/config.example.yaml \
  --dry-run

# Save payload to file
uv run skills/google-alerts/scripts/google_alerts_to_chat.py \
  --config skills/google-alerts/assets/config.example.yaml \
  --output /tmp/google-alerts-chat.json

# Send directly to webhook (or set webhook in YAML)
uv run skills/google-alerts/scripts/google_alerts_to_chat.py \
  --config skills/google-alerts/assets/config.example.yaml \
  --webhook-url "https://chat.googleapis.com/v1/spaces/..."
```

## Config Model

See `assets/config.example.yaml`.

Key sections:

- `rss_sources`: list of named RSS feeds.
- `filtering.enabled`: toggle AI filtering.
- `filtering.scoring_prompt`: prompt template for include/score decision.
- `global_summary_prompt`: prompt template to summarize all selected items.
- `chat`: title and optional webhook URL.
- `limits.max_fetch_concurrency`: concurrent article fetch workers (default: 8).

Prompt variables available in templates:

- For scoring prompt: `{source}`, `{title}`, `{link}`, `{published}`, `{snippet}`, `{markdown_excerpt}`
- For global summary prompt: `{items}`

## Expected AI Output for Filtering

The filtering prompt must request strict JSON output:

```json
{"include": true, "score": 0.82, "reason": "Relevant to market expansion"}
```

## Notes

- If filtering is disabled, all RSS items are included.
- Only readable articles are reported (successful HTTP + Markdown extraction).
- If global summary generation fails, the script falls back to deterministic text.
- Google Chat formatting is generated as `cardsV2` JSON suitable for incoming webhooks.
