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

## Category First

When you need discovery rather than a direct page fetch, choose the entrypoint by task category first, then use `fetch_text()`.

All category examples below default to:

- `ANDROID_CHROME_MOBILE_UA`
- `ANDROID_MOBILE_VIEWPORT`

This is not a claim that Android Chrome is universally stealthier. It is the more coherent default for mobile Chromium routes in this repo's current runtime, while still giving lighter pages, faster responses, and lower bandwidth than desktop surfaces.

Keep `iPhone Safari` as an explicit opt-in when you want a lightweight page surface, not as the default Google/mobile stealth profile.

## Search

For mainstream search engines such as `Google`, `Bing`, `Yahoo`, and `DuckDuckGo`, default to a mobile or lightweight results surface first. This is a default recommendation, not a universal rule:

- mobile or lightweight search pages usually expose result links faster than desktop search shells
- they reduce bandwidth and framework noise for one-shot Agent retrieval
- in this Chromium-based runtime, `Android Chrome mobile` is the most coherent default search profile

If the mobile or lightweight route is missing results, heavily degraded, or clearly less stable for a specific site, switch back to the desktop route.

For general discovery in the current examples, start with DuckDuckGo Lite:

```python
from helper import ANDROID_CHROME_MOBILE_UA, ANDROID_MOBILE_VIEWPORT, fetch_text

result = fetch_text(
    "https://lite.duckduckgo.com/lite/?q=example",
    user_agent=ANDROID_CHROME_MOBILE_UA,
    viewport=ANDROID_MOBILE_VIEWPORT,
    timeout=15000,
)
```

If the environment allows Google without `sorry` or consent gates, try Google Web with English results:

```python
result = fetch_text(
    "https://www.google.com/search?q=example&hl=en",
    user_agent=ANDROID_CHROME_MOBILE_UA,
    viewport=ANDROID_MOBILE_VIEWPORT,
    timeout=15000,
)
```

## News

Use a lightweight news query first when the task is about current events, obituaries, company updates, or publication titles:

```python
from helper import ANDROID_CHROME_MOBILE_UA, ANDROID_MOBILE_VIEWPORT, fetch_text

result = fetch_text(
    "https://lite.duckduckgo.com/lite/?q=example+news",
    user_agent=ANDROID_CHROME_MOBILE_UA,
    viewport=ANDROID_MOBILE_VIEWPORT,
    timeout=15000,
)
```

If the environment allows Google News without landing on consent pages, try:

```python
result = fetch_text(
    "https://news.google.com/search?q=example&hl=en-US&gl=US&ceid=US:en",
    user_agent=ANDROID_CHROME_MOBILE_UA,
    viewport=ANDROID_MOBILE_VIEWPORT,
    timeout=15000,
)
```

## Academic

Use arXiv for paper or research discovery before escalating to publisher sites:

```python
from helper import ANDROID_CHROME_MOBILE_UA, ANDROID_MOBILE_VIEWPORT, fetch_text

result = fetch_text(
    "https://arxiv.org/search/?query=example&searchtype=all&abstracts=show&order=-announced_date_first&size=50",
    user_agent=ANDROID_CHROME_MOBILE_UA,
    viewport=ANDROID_MOBILE_VIEWPORT,
    timeout=15000,
)
```

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

## Known Limitations

- `Google Web` and `Google News` may hit `sorry` or consent flows on shared IPs even when `hl=en` is set.
- In this Chromium-based runtime, `Android Chrome mobile` is a better default than `iPhone Safari` for Google/mobile routes because UA, touch/mobile signals, and platform-family expectations are easier to keep aligned.
- `Google Web Cache` may return region-specific pages and is not a stable fallback.
- `Wayback Machine` is often rate-limited with `HTTP 429` from shared container IPs.
- `Jina AI` can return CAPTCHA pages or empty content for anti-bot-protected sites.
- If `Cloudflare`, `Akamai`, or `PerimeterX` still blocks after a few strategy changes, stop escalating and switch to third-party sources.

## Examples

- `examples/agent/fetch_text_url.py`: fetch one URL from a mounted script.
- `examples/agent/search_mobile_text.py`: search with a lightweight/mobile page.
- `examples/agent/verify_candidate_page.py`: verify a candidate URL and print evidence.
- `examples/agent/heredoc-fetch-text.md`: stdin/heredoc usage.
- `examples/agent/mounted-script-fetch-text.md`: mounted script usage.
