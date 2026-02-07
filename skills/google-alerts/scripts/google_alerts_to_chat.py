#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12.3",
#   "pyyaml>=6.0.2",
#   "feedparser>=6.0.11",
#   "httpx>=0.27.0",
#   "google-genai>=1.0.0",
#   "trafilatura>=1.12.2",
# ]
# ///

from __future__ import annotations

import asyncio
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape, unescape
from typing import Any
from urllib.parse import parse_qs, urlparse

import feedparser
import httpx
import trafilatura
import typer
import yaml
from google import genai
from google.genai import types

app = typer.Typer(add_completion=False, no_args_is_help=True)


TAG_RE = re.compile(r"<[^>]+>")


@dataclass(slots=True)
class FeedItem:
    source: str
    title: str
    link: str
    published: str
    snippet: str
    markdown: str


@dataclass(slots=True)
class ScoredItem:
    item: FeedItem
    include: bool
    score: float
    reason: str


def log_info(message: str) -> None:
    typer.echo(f"[INFO] {message}", err=True)


def load_config(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError("Invalid config: root must be a mapping")

    sources = config.get("rss_sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("Invalid config: rss_sources must be a non-empty list")

    return config


def init_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY environment variable")
    return genai.Client(api_key=api_key)


def parse_feed(source_name: str, url: str, max_items: int) -> list[FeedItem]:
    parsed = feedparser.parse(url)
    items: list[FeedItem] = []

    for entry in parsed.entries[:max_items]:
        title = clean_text(str(entry.get("title", "Untitled")))
        link = str(entry.get("link", "")).strip()
        published = str(entry.get("published", "")).strip()
        snippet = clean_text(str(entry.get("summary", "")))

        if not title or not link:
            continue

        items.append(
            FeedItem(
                source=source_name,
                title=title,
                link=link,
                published=published,
                snippet=snippet,
                markdown="",
            )
        )

    return items


def render_template(template: str, **values: str) -> str:
    return template.format(**values)


def clean_text(value: str) -> str:
    text = unescape(value or "")
    text = TAG_RE.sub(" ", text)
    return " ".join(text.split()).strip()


def extract_news_link(raw_link: str) -> str:
    parsed = urlparse(raw_link)
    host = parsed.netloc.lower()
    if host.endswith("google.com") and parsed.path == "/url":
        params = parse_qs(parsed.query)
        for key in ("url", "q"):
            value = params.get(key)
            if value and value[0]:
                return value[0]
    return raw_link


async def fetch_article_markdown_async(
    item: FeedItem,
    client: httpx.AsyncClient,
    max_markdown_chars: int,
) -> FeedItem | None:
    try:
        resolved_link = extract_news_link(item.link)
        response = await client.get(
            resolved_link,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
                )
            },
        )
    except httpx.HTTPError:
        return None

    if response.status_code != 200:
        return None

    content_type = response.headers.get("content-type", "").lower()
    if "html" not in content_type and "xml" not in content_type:
        return None

    markdown = await asyncio.to_thread(
        trafilatura.extract,
        response.text,
        output_format="markdown",
        include_links=True,
        include_formatting=True,
        favor_recall=True,
    )
    if not markdown:
        return None

    clean_markdown = markdown.strip()
    if not clean_markdown:
        return None

    if len(clean_markdown) > max_markdown_chars:
        clean_markdown = clean_markdown[:max_markdown_chars]

    return FeedItem(
        source=item.source,
        title=item.title,
        link=resolved_link,
        published=item.published,
        snippet=item.snippet,
        markdown=clean_markdown,
    )


async def collect_readable_items_async(
    feed_items: list[FeedItem],
    max_markdown_chars: int,
    label: str,
    max_concurrency: int,
) -> list[FeedItem]:
    if not feed_items:
        return []

    semaphore = asyncio.Semaphore(max(1, max_concurrency))

    async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as async_client:

        async def worker(item: FeedItem) -> FeedItem | None:
            async with semaphore:
                return await fetch_article_markdown_async(
                    item=item,
                    client=async_client,
                    max_markdown_chars=max_markdown_chars,
                )

        tasks = [asyncio.create_task(worker(item)) for item in feed_items]
        readable_items: list[FeedItem] = []

        with typer.progressbar(length=len(tasks), label=label) as progress_bar:
            for completed_task in asyncio.as_completed(tasks):
                result = await completed_task
                if result is not None:
                    readable_items.append(result)
                progress_bar.update(1)

    return readable_items


def score_item(
    client: genai.Client,
    model_name: str,
    temperature: float,
    prompt_template: str,
    item: FeedItem,
) -> ScoredItem:
    prompt = render_template(
        prompt_template,
        source=item.source,
        title=item.title,
        link=item.link,
        published=item.published,
        snippet=item.snippet,
        markdown_excerpt=item.markdown[:2000],
    )

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
        ),
    )

    parsed = parse_json_response(response.text)
    include = bool(parsed.get("include", False))
    score = float(parsed.get("score", 0.0))
    reason = str(parsed.get("reason", "")).strip()

    return ScoredItem(item=item, include=include, score=score, reason=reason)


def parse_json_response(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).strip()
    try:
        result = json.loads(raw)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    return {"include": False, "score": 0.0, "reason": "Invalid JSON from model"}


def summarize_source(
    client: genai.Client,
    model_name: str,
    temperature: float,
    summary_prompt: str,
    source_name: str,
    items: list[ScoredItem],
) -> str:
    if not items:
        return "No relevant news selected for this source."

    rendered_items = "\n".join(
        (
            f"- {entry.item.title} ({entry.item.link}) score={entry.score:.2f}\n"
            f"  Content excerpt:\n{entry.item.markdown[:1200]}"
        )
        for entry in items
    )

    prompt = render_template(
        summary_prompt,
        source=source_name,
        items=rendered_items,
    )

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=temperature),
    )
    summary = (response.text or "").strip()

    if summary:
        return summary

    return fallback_summary(items)


def fallback_summary(items: list[ScoredItem]) -> str:
    if not items:
        return "No relevant news selected for this source."

    top_titles = ", ".join(entry.item.title for entry in items[:3])
    return f"Selected {len(items)} relevant items. Main topics include: {top_titles}."


def summarize_global(
    client: genai.Client,
    model_name: str,
    temperature: float,
    global_summary_prompt: str,
    grouped: dict[str, list[ScoredItem]],
) -> str:
    all_items: list[ScoredItem] = [
        scored_item for source_items in grouped.values() for scored_item in source_items
    ]
    if not all_items:
        return "No readable and relevant news found today."

    rendered_items = "\n".join(
        (
            f"- [{entry.item.source}] {entry.item.title} ({entry.item.link}) score={entry.score:.2f}\n"
            f"  Content excerpt:\n{entry.item.markdown[:1000]}"
        )
        for entry in all_items
    )

    prompt = render_template(global_summary_prompt, items=rendered_items)
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=temperature),
    )
    summary = (response.text or "").strip()
    if summary:
        return summary
    return fallback_global_summary(grouped)


def fallback_global_summary(grouped: dict[str, list[ScoredItem]]) -> str:
    total_items = sum(len(items) for items in grouped.values())
    if total_items == 0:
        return "No readable and relevant news found today."

    source_chunks = [
        f"{source_name}: {len(items)}"
        for source_name, items in grouped.items()
        if items
    ]
    source_counts = ", ".join(source_chunks)
    return f"Selected {total_items} items across sources ({source_counts})."


def build_google_chat_payload(
    title: str,
    global_summary: str,
    grouped: dict[str, list[ScoredItem]],
) -> dict[str, Any]:
    sections: list[dict[str, Any]] = [
        {
            "header": "Global Summary",
            "widgets": [{"textParagraph": {"text": escape(global_summary)}}],
        }
    ]

    for source_name, items in grouped.items():
        if items:
            links_html = "<br>".join(
                f'- <a href="{escape(entry.item.link)}">{escape(entry.item.title)}</a>'
                for entry in items
            )
        else:
            links_html = "- No links available"

        sections.append(
            {
                "header": escape(f"{source_name} ({len(items)})"),
                "collapsible": True,
                "uncollapsibleWidgetsCount": 0,
                "widgets": [
                    {
                        "textParagraph": {
                            "text": links_html,
                        }
                    },
                ],
            }
        )

    return {
        "text": title,
        "cardsV2": [
            {
                "cardId": "google-alerts-digest",
                "card": {
                    "header": {
                        "title": title,
                        "subtitle": datetime.now(tz=timezone.utc).strftime(
                            "Generated %Y-%m-%d"
                        ),
                    },
                    "sections": sections,
                },
            }
        ],
    }


def post_webhook(payload: dict[str, Any], webhook_url: str) -> None:
    with httpx.Client(timeout=20.0) as client:
        response = client.post(webhook_url, json=payload)
        response.raise_for_status()


@app.command()
def main(
    config: str = typer.Option(..., help="Path to YAML config file."),
    output: str | None = typer.Option(None, help="Optional output JSON file path."),
    webhook_url: str | None = typer.Option(
        None,
        help="Optional Google Chat webhook URL. Overrides config value.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Run without Gemini calls to test RSS parsing and payload generation.",
    ),
) -> None:
    """Build a Google Chat payload from Google Alerts RSS feeds."""
    log_info(
        "Starting pipeline: load config, fetch RSS, extract article markdown, "
        "filter/score items, build Google Chat payload."
    )
    data = load_config(config)

    chat_cfg = data.get("chat", {})
    model_cfg = data.get("model", {})
    filtering_cfg = data.get("filtering", {})
    limits_cfg = data.get("limits", {})

    title = str(chat_cfg.get("title", "Google Alerts Digest")).strip()
    selected_webhook = webhook_url or str(chat_cfg.get("webhook_url", "")).strip()

    model_name = str(model_cfg.get("name", "gemini-2.0-flash")).strip()
    temperature = float(model_cfg.get("temperature", 0.2))

    filtering_enabled = bool(filtering_cfg.get("enabled", False))
    scoring_prompt = str(filtering_cfg.get("scoring_prompt", "")).strip()
    min_score = float(filtering_cfg.get("min_score", 0.0))

    global_summary_prompt = str(data.get("global_summary_prompt", "")).strip()
    max_items_per_source = int(limits_cfg.get("max_items_per_source", 20))
    max_markdown_chars = int(limits_cfg.get("max_markdown_chars_per_item", 12000))
    max_fetch_concurrency = int(limits_cfg.get("max_fetch_concurrency", 8))

    if filtering_enabled and not scoring_prompt:
        raise ValueError(
            "filtering.scoring_prompt is required when filtering is enabled"
        )
    if not global_summary_prompt:
        raise ValueError("global_summary_prompt is required")

    genai_client = None if dry_run else init_client()
    if dry_run:
        log_info(
            "Dry run enabled: Gemini calls are skipped. Filtering and global summary use deterministic fallback."
        )
    else:
        log_info(
            f"Gemini enabled with model '{model_name}' for scoring and global summary."
        )

    grouped_results: dict[str, list[ScoredItem]] = {}
    sources = data["rss_sources"]
    total_feed_items = 0
    total_readable_items = 0
    total_selected_items = 0

    with typer.progressbar(sources, label="Processing sources") as source_bar:
        for source in source_bar:
            source_name = str(source.get("name", "")).strip()
            source_url = str(source.get("url", "")).strip()

            if not source_name or not source_url:
                continue

            feed_items = parse_feed(
                source_name, source_url, max_items=max_items_per_source
            )
            total_feed_items += len(feed_items)

            readable_items = asyncio.run(
                collect_readable_items_async(
                    feed_items=feed_items,
                    max_markdown_chars=max_markdown_chars,
                    label=f"Reading articles {source_name}",
                    max_concurrency=max_fetch_concurrency,
                )
            )
            total_readable_items += len(readable_items)

            scored_items: list[ScoredItem] = []
            if dry_run:
                scored_items = [
                    ScoredItem(
                        item=item,
                        include=True,
                        score=1.0,
                        reason="Dry run: AI filtering skipped",
                    )
                    for item in readable_items
                ]
            elif filtering_enabled:
                with typer.progressbar(
                    readable_items, label=f"Scoring {source_name}"
                ) as item_bar:
                    for item in item_bar:
                        scored = score_item(
                            client=genai_client,
                            model_name=model_name,
                            temperature=temperature,
                            prompt_template=scoring_prompt,
                            item=item,
                        )
                        if scored.include and scored.score >= min_score:
                            scored_items.append(scored)
            else:
                scored_items = [
                    ScoredItem(
                        item=item,
                        include=True,
                        score=1.0,
                        reason="Filtering disabled",
                    )
                    for item in readable_items
                ]

            grouped_results[source_name] = scored_items
            total_selected_items += len(scored_items)
            log_info(
                f"Source '{source_name}': rss_items={len(feed_items)}, "
                f"readable_items={len(readable_items)}, selected_items={len(scored_items)}."
            )

    if dry_run:
        global_summary = fallback_global_summary(grouped_results)
    else:
        global_summary = summarize_global(
            client=genai_client,
            model_name=model_name,
            temperature=temperature,
            global_summary_prompt=global_summary_prompt,
            grouped=grouped_results,
        )

    payload = build_google_chat_payload(
        title=title,
        global_summary=global_summary,
        grouped=grouped_results,
    )
    log_info(
        f"Payload ready: sources={len(grouped_results)}, total_rss_items={total_feed_items}, "
        f"readable_items={total_readable_items}, selected_items={total_selected_items}."
    )

    if output:
        with open(output, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        log_info(f"Payload JSON saved to '{output}'.")

    if dry_run:
        log_info("Dry run completed successfully.")

    if selected_webhook:
        post_webhook(payload, selected_webhook)
        log_info("Webhook delivery successful. No further action required.")
    else:
        log_info(
            "Webhook URL not provided. Printing payload JSON to stdout so another system/LLM can post it."
        )
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
