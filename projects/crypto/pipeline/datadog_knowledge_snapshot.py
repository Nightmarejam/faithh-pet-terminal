#!/usr/bin/env python3
"""Collect Datadog Knowledge Center pages into local machine-readable files."""

from __future__ import annotations

import argparse
import json
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "ops"
DATADOG_HOST = "www.datadoghq.com"
DATADOG_PREFIX = "/knowledge-center/"
DEFAULT_SEEDS = [
    "https://www.datadoghq.com/knowledge-center/observability/",
    "https://www.datadoghq.com/knowledge-center/distributed-tracing/",
    "https://www.datadoghq.com/knowledge-center/log-management/",
    "https://www.datadoghq.com/knowledge-center/metrics/",
    "https://www.datadoghq.com/knowledge-center/software-catalog/",
    "https://www.datadoghq.com/knowledge-center/end-to-end-testing/",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Snapshot Datadog Knowledge Center pages")
    parser.add_argument("--seed-url", action="append", default=None, help="Seed URL(s), can be passed multiple times.")
    parser.add_argument("--max-pages", type=int, default=25)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--delay-sec", type=float, default=0.6)
    parser.add_argument("--max-paragraphs", type=int, default=80)
    return parser.parse_args()


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    cleaned = parsed._replace(query="", fragment="")
    return urlunparse(cleaned)


def in_scope(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and parsed.netloc == DATADOG_HOST and parsed.path.startswith(DATADOG_PREFIX)


class KnowledgeCenterParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title: str = ""
        self.meta_description: str = ""
        self.headings: list[str] = []
        self.paragraphs: list[str] = []
        self.links: list[str] = []

        self._capture_text = False
        self._capture_title = False
        self._buffer: list[str] = []
        self._tag_stack: list[str] = []
        self._in_script_like = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._tag_stack.append(tag)
        attrs_map = {k: v for k, v in attrs}

        if tag in {"script", "style", "noscript"}:
            self._in_script_like = True
            return

        if tag == "title":
            self._capture_title = True
            self._buffer.clear()
            return

        if tag in {"h1", "h2", "h3", "p", "li"}:
            self._capture_text = True
            self._buffer.clear()

        if tag == "meta":
            if (attrs_map.get("name") or "").lower() == "description":
                self.meta_description = (attrs_map.get("content") or "").strip()

        if tag == "a":
            href = attrs_map.get("href")
            if href:
                self.links.append(href.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"}:
            self._in_script_like = False
            if self._tag_stack:
                self._tag_stack.pop()
            return

        text = " ".join("".join(self._buffer).split()).strip()
        if self._capture_title and tag == "title":
            self.title = text
            self._capture_title = False
            self._buffer.clear()
        elif self._capture_text and tag in {"h1", "h2", "h3", "p", "li"}:
            if text:
                if tag in {"h1", "h2", "h3"}:
                    self.headings.append(text)
                else:
                    self.paragraphs.append(text)
            self._capture_text = False
            self._buffer.clear()

        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._in_script_like:
            return
        if self._capture_text or self._capture_title:
            self._buffer.append(data)


@dataclass
class PageRecord:
    url: str
    title: str
    meta_description: str
    headings: list[str] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    outbound_links: list[str] = field(default_factory=list)
    fetched_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_json(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "meta_description": self.meta_description,
            "headings": self.headings,
            "paragraphs": self.paragraphs,
            "outbound_links": self.outbound_links,
            "fetched_at_utc": self.fetched_at_utc,
        }


def fetch_page(url: str, timeout: float) -> tuple[PageRecord, list[str]]:
    headers = {"User-Agent": "faithh-knowledge-snapshot/1.0"}
    response = requests.get(url, timeout=timeout, headers=headers)
    response.raise_for_status()
    parser = KnowledgeCenterParser()
    parser.feed(response.text)

    resolved_links: list[str] = []
    for href in parser.links:
        absolute = normalize_url(urljoin(url, href))
        if in_scope(absolute):
            resolved_links.append(absolute)

    rec = PageRecord(
        url=url,
        title=parser.title,
        meta_description=parser.meta_description,
        headings=list(dict.fromkeys(parser.headings)),
        paragraphs=parser.paragraphs,
        outbound_links=list(dict.fromkeys(resolved_links)),
    )
    return rec, rec.outbound_links


def crawl(seeds: list[str], max_pages: int, timeout: float, delay_sec: float, max_paragraphs: int) -> dict[str, Any]:
    queue: deque[str] = deque()
    seen: set[str] = set()
    fetched: list[PageRecord] = []
    failures: list[dict[str, str]] = []

    for seed in seeds:
        candidate = normalize_url(seed)
        if in_scope(candidate):
            queue.append(candidate)

    while queue and len(fetched) < max_pages:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        try:
            page, links = fetch_page(url, timeout=timeout)
            page.paragraphs = page.paragraphs[:max_paragraphs]
            fetched.append(page)
            for link in links:
                if link not in seen:
                    queue.append(link)
        except requests.RequestException as exc:
            failures.append({"url": url, "error": str(exc)[:220]})
        time.sleep(delay_sec)

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "seed_urls": seeds,
        "fetched_pages": [p.to_json() for p in fetched],
        "fetched_count": len(fetched),
        "failure_count": len(failures),
        "failures": failures,
    }


def write_outputs(report: dict[str, Any]) -> tuple[Path, Path, Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    summary_ts = OUT_DIR / f"datadog_kc_snapshot_{stamp}.json"
    summary_latest = OUT_DIR / "datadog_kc_snapshot_latest.json"
    pages_jsonl = OUT_DIR / f"datadog_kc_pages_{stamp}.jsonl"

    summary_blob = json.dumps(report, indent=2)
    summary_ts.write_text(summary_blob, encoding="utf-8")
    summary_latest.write_text(summary_blob, encoding="utf-8")

    lines = [json.dumps(page, ensure_ascii=True) for page in report["fetched_pages"]]
    pages_jsonl.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    return summary_ts, summary_latest, pages_jsonl


def main() -> int:
    args = parse_args()
    seeds = args.seed_url if args.seed_url else DEFAULT_SEEDS
    report = crawl(
        seeds=seeds,
        max_pages=args.max_pages,
        timeout=args.timeout,
        delay_sec=args.delay_sec,
        max_paragraphs=args.max_paragraphs,
    )
    summary_ts, summary_latest, pages_jsonl = write_outputs(report)
    print(
        json.dumps(
            {
                "summary_timestamped": str(summary_ts),
                "summary_latest": str(summary_latest),
                "pages_jsonl": str(pages_jsonl),
                "fetched_count": report["fetched_count"],
                "failure_count": report["failure_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
