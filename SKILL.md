---
name: cloakbrowser-agent-text
description: Use CloakBrowser as a thin Agent text-retrieval harness for one-shot URL fetching, mobile search pages, readiness checks, and structured failure kinds.
---

# CloakBrowser Agent Text Retrieval

Use this repo as a stealth Chromium runtime, not as a broad Agent framework.

## Default Path

Prefer `helper.fetch_text()` when the task is "open this URL and inspect the page text":

```python
from helper import fetch_text

result = fetch_text("https://example.com", timeout=15000)
print(result.title)
print(result.visible_text[:4000])
print(result.error_kind)
```

This avoids repeatedly writing:

```python
browser = launch(headless=True)
page = browser.new_page()
page.goto(url)
print(page.title())
print(page.evaluate("document.body.innerText"))
browser.close()
```

## Mobile Search Pages

For search result pages, prefer mobile or lightweight pages to reduce load time and network traffic:

```python
from helper import IPHONE_SAFARI_UA, IPHONE_VIEWPORT, fetch_text

result = fetch_text(
    "https://lite.duckduckgo.com/lite/?q=example",
    user_agent=IPHONE_SAFARI_UA,
    viewport=IPHONE_VIEWPORT,
    timeout=15000,
)
```

The iPhone UA plus mobile viewport is useful for DuckDuckGo or Google search pages. It is not a universal stealth improvement: CloakBrowser is Chromium, so strong bot defenses may notice a Safari-on-iPhone UA mismatch. If a page is sensitive, try the default UA or `ANDROID_CHROME_MOBILE_UA` with `ANDROID_MOBILE_VIEWPORT`.

## Readiness Check

Use `readiness_check()` only to isolate environment problems:

```python
from helper import readiness_check

result = readiness_check()
print(result.ok, result.stage, result.error_kind, result.error)
```

Readiness is not a substitute for real fetching. It only checks the local launch/page/about:blank lifecycle by default. Add `external_url=...` only when you want a real network probe.

## Error Kinds

Handle these before guessing:

- `browser_init_failed`: CloakBrowser did not launch or create a context.
- `navigation_timeout`: the page did not finish the requested navigation in time.
- `empty_visible_text`: navigation worked, but `document.body.innerText` was empty.
- `challenge_detected`: page text looked like an anti-bot or CAPTCHA challenge.
- `unknown_error`: inspect `error` and decide whether to retry or switch strategy.

## Examples

- `examples/agent/fetch_text_url.py`: fetch one URL from a mounted script.
- `examples/agent/search_mobile_text.py`: search with a lightweight/mobile page.
- `examples/agent/verify_candidate_page.py`: verify a candidate URL and print evidence.
- `examples/agent/heredoc-fetch-text.md`: stdin/heredoc usage.
- `examples/agent/mounted-script-fetch-text.md`: mounted script usage.
