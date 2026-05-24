from unittest.mock import MagicMock


class FakePage:
    def __init__(self, *, title="Example Domain", text="Visible text", url="https://example.com/final"):
        self._title = title
        self._text = text
        self.url = url
        self.goto_calls = []

    def goto(self, url, **kwargs):
        self.goto_calls.append((url, kwargs))

    def title(self):
        return self._title

    def evaluate(self, script):
        assert script == "document.body.innerText"
        return self._text


class FakeContext:
    def __init__(self, page):
        self.page = page
        self.closed = False

    def new_page(self):
        return self.page

    def close(self):
        self.closed = True


def test_fetch_text_returns_title_visible_text_and_forwards_mobile_user_agent(monkeypatch):
    import helper

    page = FakePage(text="abcdefghijklmnopqrstuvwxyz")
    context = FakeContext(page)
    launch_calls = []

    def fake_launch_context(**kwargs):
        launch_calls.append(kwargs)
        return context

    monkeypatch.setattr(helper, "launch_context", fake_launch_context)

    result = helper.fetch_text(
        "https://example.com",
        timeout=15000,
        user_agent=helper.IPHONE_SAFARI_UA,
        viewport=helper.IPHONE_VIEWPORT,
        max_chars=10,
        locale="en-US",
    )

    assert result.ok is True
    assert result.title == "Example Domain"
    assert result.visible_text == "abcdefghij"
    assert result.final_url == "https://example.com/final"
    assert result.error_kind is None
    assert page.goto_calls == [("https://example.com", {"timeout": 15000, "wait_until": "domcontentloaded"})]
    assert launch_calls == [{
        "headless": True,
        "user_agent": helper.IPHONE_SAFARI_UA,
        "viewport": helper.IPHONE_VIEWPORT,
        "locale": "en-US",
    }]
    assert context.closed is True


def test_fetch_text_maps_navigation_timeout_and_closes_context(monkeypatch):
    import helper

    class TimeoutPage(FakePage):
        def goto(self, url, **kwargs):
            raise TimeoutError("timed out")

    context = FakeContext(TimeoutPage())
    monkeypatch.setattr(helper, "launch_context", lambda **kwargs: context)

    result = helper.fetch_text("https://slow.example", timeout=100)

    assert result.ok is False
    assert result.error_kind == "navigation_timeout"
    assert "timed out" in result.error
    assert context.closed is True


def test_fetch_text_maps_empty_visible_text(monkeypatch):
    import helper

    context = FakeContext(FakePage(text="   \n\t"))
    monkeypatch.setattr(helper, "launch_context", lambda **kwargs: context)

    result = helper.fetch_text("https://empty.example")

    assert result.ok is False
    assert result.error_kind == "empty_visible_text"
    assert result.title == "Example Domain"
    assert result.final_url == "https://example.com/final"
    assert context.closed is True


def test_fetch_text_detects_common_challenge_text(monkeypatch):
    import helper

    context = FakeContext(FakePage(text="Checking if the site connection is secure"))
    monkeypatch.setattr(helper, "launch_context", lambda **kwargs: context)

    result = helper.fetch_text("https://challenge.example")

    assert result.ok is False
    assert result.error_kind == "challenge_detected"
    assert context.closed is True


def test_readiness_check_reports_local_navigation_stage(monkeypatch):
    import helper

    page = FakePage(title="")
    context = FakeContext(page)
    launch_context = MagicMock(return_value=context)
    monkeypatch.setattr(helper, "launch_context", launch_context)

    result = helper.readiness_check()

    assert result.ok is True
    assert result.stage == "ok"
    assert result.error_kind is None
    assert page.goto_calls == [("about:blank", {"timeout": 5000, "wait_until": "domcontentloaded"})]
    launch_context.assert_called_once_with(headless=True)
    assert context.closed is True


def test_readiness_check_can_optionally_verify_external_url(monkeypatch):
    import helper

    page = FakePage(title="External")
    context = FakeContext(page)
    monkeypatch.setattr(helper, "launch_context", lambda **kwargs: context)

    result = helper.readiness_check(external_url="https://example.com", external_timeout=7000)

    assert result.ok is True
    assert result.stage == "ok"
    assert page.goto_calls == [
        ("about:blank", {"timeout": 5000, "wait_until": "domcontentloaded"}),
        ("https://example.com", {"timeout": 7000, "wait_until": "domcontentloaded"}),
    ]
    assert context.closed is True
