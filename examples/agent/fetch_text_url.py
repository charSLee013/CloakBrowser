#!/usr/bin/env python3
"""Fetch title and visible text for one URL with CloakBrowser."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from helper import (
    ANDROID_CHROME_MOBILE_UA,
    ANDROID_MOBILE_VIEWPORT,
    IPHONE_SAFARI_UA,
    IPHONE_VIEWPORT,
    fetch_text,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch one URL as title + visible text.")
    parser.add_argument("url")
    parser.add_argument("--timeout", type=int, default=15000)
    parser.add_argument("--max-chars", type=int, default=4000)
    parser.add_argument("--user-agent")
    ua_group = parser.add_mutually_exclusive_group()
    ua_group.add_argument("--iphone", action="store_true", help="Use an iPhone Safari user-agent.")
    ua_group.add_argument("--android-mobile", action="store_true", help="Use an Android Chrome mobile user-agent.")
    args = parser.parse_args()

    user_agent = args.user_agent
    viewport = None
    if args.iphone:
        user_agent = IPHONE_SAFARI_UA
        viewport = IPHONE_VIEWPORT
    elif args.android_mobile:
        user_agent = ANDROID_CHROME_MOBILE_UA
        viewport = ANDROID_MOBILE_VIEWPORT

    result = fetch_text(
        args.url,
        timeout=args.timeout,
        user_agent=user_agent,
        viewport=viewport,
        max_chars=args.max_chars,
    )
    print_result(result)
    return 0 if result.ok else 1


def print_result(result) -> None:
    print(f"OK: {result.ok}")
    print(f"TITLE: {result.title}")
    print(f"FINAL_URL: {result.final_url}")
    print(f"ERROR_KIND: {result.error_kind or ''}")
    if result.error:
        print(f"ERROR: {result.error}")
    print("VISIBLE_TEXT:")
    print(result.visible_text)


if __name__ == "__main__":
    raise SystemExit(main())
