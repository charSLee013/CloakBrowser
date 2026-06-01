from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "examples" / "agent" / "search_mobile_text.py"
SKILL_PATH = ROOT / "SKILL.md"


def _load_search_module():
    spec = spec_from_file_location("agent_search_mobile_text", SCRIPT_PATH)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_skill_groups_examples_by_category_and_defaults_to_iphone():
    text = SKILL_PATH.read_text()

    assert "## Search" in text
    assert "## News" in text
    assert "## Academic" in text
    assert "Google`, `Bing`, `Yahoo`, and `DuckDuckGo" in text
    assert "default to a mobile or lightweight results surface first" in text
    assert "This is a default recommendation, not a universal rule" in text
    assert "https://lite.duckduckgo.com/lite/?q=example" in text
    assert "https://lite.duckduckgo.com/lite/?q=example+news" in text
    assert "https://arxiv.org/search/?" in text
    assert "ANDROID_CHROME_MOBILE_UA" in text
    assert "ANDROID_MOBILE_VIEWPORT" in text
    assert "https://www.google.com/search?q=example&hl=en" in text
    assert "https://news.google.com/search?q=example&hl=en-US&gl=US&ceid=US:en" in text
    assert "Google Web Cache" in text
    assert "Wayback Machine" in text
    assert "Jina AI" in text


def test_search_category_defaults_to_duckduckgo_lite():
    module = _load_search_module()

    url = module.build_category_url("search", "example", "duckduckgo")

    assert url == "https://lite.duckduckgo.com/lite/?q=example"


def test_search_category_can_fallback_to_google_web_with_english_results():
    module = _load_search_module()

    url = module.build_category_url("search", "example", "google")

    assert url == "https://www.google.com/search?q=example&hl=en"


def test_news_category_defaults_to_duckduckgo_news_query():
    module = _load_search_module()

    url = module.build_category_url("news", "example", "duckduckgo")

    assert url == "https://lite.duckduckgo.com/lite/?q=example+news"


def test_news_category_can_use_google_news_english_surface():
    module = _load_search_module()

    url = module.build_category_url("news", "example", "google")

    assert url == "https://news.google.com/search?q=example&hl=en-US&gl=US&ceid=US%3Aen"


def test_academic_category_uses_arxiv_search():
    module = _load_search_module()

    url = module.build_category_url("academic", "transformer", "google")

    assert (
        url
        == "https://arxiv.org/search/?query=transformer&searchtype=all&abstracts=show&order=-announced_date_first&size=50"
    )


def test_default_mobile_profile_is_android():
    module = _load_search_module()

    user_agent, viewport = module.resolve_mobile_profile(default_user_agent=False, user_agent=None)

    assert user_agent == module.ANDROID_CHROME_MOBILE_UA
    assert viewport == module.ANDROID_MOBILE_VIEWPORT
