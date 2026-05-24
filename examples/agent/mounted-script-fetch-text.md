# Mounted Script Fetch Text

Use a mounted or local script when the agent needs repeatable fetches.

```bash
python examples/agent/fetch_text_url.py \
  --iphone \
  --timeout 15000 \
  --max-chars 4000 \
  "https://lite.duckduckgo.com/lite/?q=CloakBrowser"
```

For candidate page verification:

```bash
python examples/agent/verify_candidate_page.py \
  --timeout 15000 \
  --max-chars 8000 \
  "https://example.com"
```

For Docker-style mounted scripts:

```bash
docker run --rm -v "$PWD":/work -w /work cloakhq/cloakbrowser \
  python examples/agent/fetch_text_url.py --iphone "https://example.com"
```
