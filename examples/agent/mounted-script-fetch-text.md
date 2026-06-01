# Mounted Script Fetch Text

Use a mounted or local script when the agent needs repeatable fetches.

```bash
python examples/agent/fetch_text_url.py \
  --android-mobile \
  --timeout 15000 \
  --max-chars 4000 \
  "https://lite.duckduckgo.com/lite/?q=CloakBrowser"
```

For category-based discovery:

```bash
python examples/agent/search_mobile_text.py \
  --category news \
  --timeout 15000 \
  --max-chars 5000 \
  "OpenAI"
```

For candidate page verification after discovery:

```bash
python examples/agent/verify_candidate_page.py \
  --timeout 15000 \
  --max-chars 8000 \
  "https://example.com"
```

For Docker-style mounted scripts:

```bash
docker run --rm -v "$PWD":/work -w /work cloakbrowser-local \
  python examples/agent/fetch_text_url.py --android-mobile "https://example.com"
```
