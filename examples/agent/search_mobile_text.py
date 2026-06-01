#!/usr/bin/env python3
"""Fetch lightweight/mobile discovery text with CloakBrowser."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from helper import (
    ANDROID_CHROME_MOBILE_UA,
    ANDROID_MOBILE_VIEWPORT,
    IPHONE_SAFARI_UA,
    IPHONE_VIEWPORT,
    fetch_text,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch mobile-friendly discovery results by task category.")
    parser.add_argument("query")
    parser.add_argument("--category", choices=("search", "news", "academic"), default="search")
    parser.add_argument(
        "--engine",
        choices=("google", "duckduckgo"),
        default="duckduckgo",
        help="Used for the 'search' and 'news' categories.",
    )
    parser.add_argument("--timeout", type=int, default=15000)
    parser.add_argument("--max-chars", type=int, default=5000)
    parser.add_argument("--user-agent")
    parser.add_argument("--default-user-agent", action="store_true", help="Do not override CloakBrowser's default UA.")
    args = parser.parse_args()

    url = build_category_url(args.category, args.query, args.engine)
    user_agent, viewport = resolve_mobile_profile(
        default_user_agent=args.default_user_agent,
        user_agent=args.user_agent,
    )
    result = fetch_text(
        url,
        timeout=args.timeout,
        user_agent=user_agent,
        viewport=viewport,
        max_chars=args.max_chars,
    )

    print(f"QUERY: {args.query}")
    print(f"CATEGORY: {args.category}")
    print(f"SEARCH_URL: {url}")
    print(f"OK: {result.ok}")
    print(f"TITLE: {result.title}")
    print(f"FINAL_URL: {result.final_url}")
    print(f"ERROR_KIND: {result.error_kind or ''}")
    if result.error:
        print(f"ERROR: {result.error}")
    print("VISIBLE_TEXT:")
    print(result.visible_text)
    return 0 if result.ok else 1


def build_category_url(category: str, query: str, engine: str) -> str:
    if category == "news":
        if engine == "duckduckgo":
            return "https://lite.duckduckgo.com/lite/?" + urlencode({"q": f"{query} news"})
        return "https://news.google.com/search?" + urlencode({
            "q": query,
            "hl": "en-US",
            "gl": "US",
            "ceid": "US:en",
        })
    if category == "academic":
        return "https://arxiv.org/search/?" + urlencode({
            "query": query,
            "searchtype": "all",
            "abstracts": "show",
            "order": "-announced_date_first",
            "size": "50",
        })
    if engine == "duckduckgo":
        return "https://lite.duckduckgo.com/lite/?" + urlencode({"q": query})
    return "https://www.google.com/search?" + urlencode({"q": query, "hl": "en"})


def resolve_mobile_profile(*, default_user_agent: bool, user_agent: str | None) -> tuple[str | None, dict[str, int] | None]:
    if default_user_agent:
        return None, None
    if user_agent:
        return user_agent, ANDROID_MOBILE_VIEWPORT
    return ANDROID_CHROME_MOBILE_UA, ANDROID_MOBILE_VIEWPORT


if __name__ == "__main__":
    raise SystemExit(main())
