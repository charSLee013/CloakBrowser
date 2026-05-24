# Heredoc Fetch Text

Agents often emit multiline Python through stdin. Treat that as a normal path.

```bash
python - <<'PY'
from helper import IPHONE_SAFARI_UA, IPHONE_VIEWPORT, fetch_text

result = fetch_text(
    "https://lite.duckduckgo.com/lite/?q=CloakBrowser",
    user_agent=IPHONE_SAFARI_UA,
    viewport=IPHONE_VIEWPORT,
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

Use heredoc when the agent needs to compose a small one-off probe. If the script will be reused, prefer a mounted script file.
