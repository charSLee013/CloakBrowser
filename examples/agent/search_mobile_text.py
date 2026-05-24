#!/usr/bin/env python3
"""Fetch lightweight/mobile search result text with CloakBrowser."""

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
    parser = argparse.ArgumentParser(description="Search and print mobile-friendly result text.")
    parser.add_argument("query")
    parser.add_argument("--engine", choices=("duckduckgo", "google"), default="duckduckgo")
    parser.add_argument("--timeout", type=int, default=15000)
    parser.add_argument("--max-chars", type=int, default=5000)
    parser.add_argument("--user-agent")
    parser.add_argument("--android-mobile", action="store_true", help="Use Android Chrome instead of iPhone Safari.")
    parser.add_argument("--default-user-agent", action="store_true", help="Do not override CloakBrowser's default UA.")
    args = parser.parse_args()

    url = build_search_url(args.engine, args.query)
    user_agent, viewport = resolve_mobile_profile(args)
    result = fetch_text(
        url,
        timeout=args.timeout,
        user_agent=user_agent,
        viewport=viewport,
        max_chars=args.max_chars,
    )

    print(f"QUERY: {args.query}")
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


def build_search_url(engine: str, query: str) -> str:
    if engine == "google":
        return "https://www.google.com/search?" + urlencode({"q": query})
    return "https://lite.duckduckgo.com/lite/?" + urlencode({"q": query})


def resolve_mobile_profile(args) -> tuple[str | None, dict[str, int] | None]:
    if args.default_user_agent:
        return None, None
    if args.user_agent:
        return args.user_agent, None
    if args.android_mobile:
        return ANDROID_CHROME_MOBILE_UA, ANDROID_MOBILE_VIEWPORT
    return IPHONE_SAFARI_UA, IPHONE_VIEWPORT


if __name__ == "__main__":
    raise SystemExit(main())
