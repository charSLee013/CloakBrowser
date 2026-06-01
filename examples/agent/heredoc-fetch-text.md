# Heredoc Fetch Text

Agents often emit multiline Python through stdin. Treat that as a normal path.

```bash
python - <<'PY'
from helper import ANDROID_CHROME_MOBILE_UA, ANDROID_MOBILE_VIEWPORT, fetch_text

result = fetch_text(
    "https://lite.duckduckgo.com/lite/?q=OpenAI+news",
    user_agent=ANDROID_CHROME_MOBILE_UA,
    viewport=ANDROID_MOBILE_VIEWPORT,
    timeout=15000,
    max_chars=4000,
)

print("OK:", result.ok)
print("TITLE:", result.title)
print("FINAL_URL:", result.final_url)
print("ERROR_KIND:", result.error_kind or "")
print(result.visible_text)
PY
```

Use heredoc when the agent needs a one-off probe. Pick the URL by category:

- general discovery: DuckDuckGo Lite first, then Google Web with `hl=en` if the environment allows it
- news: DuckDuckGo Lite with `+news`, then Google News if it does not redirect to consent
- academic: arXiv search

Default to Android Chrome mobile for Google/mobile routes. Use iPhone explicitly only when you want a lighter page surface and do not need Chromium-family consistency.

If the script will be reused, prefer a mounted script file.
