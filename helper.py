"""Small Agent-facing helpers for common CloakBrowser text retrieval tasks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cloakbrowser import launch_context


IPHONE_SAFARI_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
    "Mobile/15E148 Safari/604.1"
)

ANDROID_CHROME_MOBILE_UA = (
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36"
)

IPHONE_VIEWPORT = {"width": 390, "height": 844}
ANDROID_MOBILE_VIEWPORT = {"width": 412, "height": 915}

_CHALLENGE_MARKERS = (
    "checking if the site connection is secure",
    "our systems have detected unusual traffic from your computer network",
    "please verify you are a human",
    "verify you are human",
    "cf-browser-verification",
    "checking your browser",
    "access denied",
)


@dataclass
class FetchTextResult:
    ok: bool
    title: str = ""
    visible_text: str = ""
    final_url: str = ""
    error_kind: str | None = None
    error: str = ""


@dataclass
class ReadinessResult:
    ok: bool
    stage: str
    error_kind: str | None = None
    error: str = ""


def fetch_text(
    url: str,
    *,
    timeout: int = 15000,
    user_agent: str | None = None,
    viewport: dict[str, int] | None = None,
    max_chars: int | None = None,
    wait_until: str = "domcontentloaded",
    headless: bool = True,
    **launch_kwargs: Any,
) -> FetchTextResult:
    """Open one URL and return title, visible text, final URL, and error kind."""
    context = None
    title = ""
    final_url = ""
    try:
        context_kwargs: dict[str, Any] = {"headless": headless}
        if user_agent:
            context_kwargs["user_agent"] = user_agent
        if viewport is not None:
            context_kwargs["viewport"] = viewport
        context_kwargs.update(launch_kwargs)

        context = launch_context(**context_kwargs)
        page = context.new_page()
        page.goto(url, timeout=timeout, wait_until=wait_until)
        title = page.title() or ""
        final_url = getattr(page, "url", "") or ""
        visible_text = page.evaluate("document.body.innerText") or ""
        if max_chars is not None:
            visible_text = visible_text[:max_chars]

        if _looks_like_challenge(title, final_url, visible_text):
            return FetchTextResult(
                ok=False,
                title=title,
                visible_text=visible_text,
                final_url=final_url,
                error_kind="challenge_detected",
                error="page text looks like an anti-bot challenge",
            )
        if not visible_text.strip():
            return FetchTextResult(
                ok=False,
                title=title,
                visible_text=visible_text,
                final_url=final_url,
                error_kind="empty_visible_text",
                error="document.body.innerText was empty",
            )
        return FetchTextResult(
            ok=True,
            title=title,
            visible_text=visible_text,
            final_url=final_url,
        )
    except Exception as exc:
        return FetchTextResult(
            ok=False,
            title=title,
            final_url=final_url,
            error_kind="browser_init_failed" if context is None else _classify_exception(exc),
            error=str(exc),
        )
    finally:
        if context is not None:
            try:
                context.close()
            except Exception:
                pass


def readiness_check(
    *,
    timeout: int = 5000,
    external_url: str | None = None,
    external_timeout: int | None = None,
    headless: bool = True,
    **launch_kwargs: Any,
) -> ReadinessResult:
    """Check local browser/page lifecycle, optionally followed by a real URL."""
    context = None
    try:
        context = launch_context(headless=headless, **launch_kwargs)
    except Exception as exc:
        return ReadinessResult(
            ok=False,
            stage="launch",
            error_kind="browser_init_failed",
            error=str(exc),
        )

    try:
        page = context.new_page()
    except Exception as exc:
        _close_context(context)
        return ReadinessResult(
            ok=False,
            stage="new_page",
            error_kind="page_create_failed",
            error=str(exc),
        )

    try:
        page.goto("about:blank", timeout=timeout, wait_until="domcontentloaded")
    except Exception as exc:
        _close_context(context)
        return ReadinessResult(
            ok=False,
            stage="local_navigation",
            error_kind=_classify_exception(exc),
            error=str(exc),
        )

    if external_url:
        try:
            page.goto(
                external_url,
                timeout=external_timeout if external_timeout is not None else timeout,
                wait_until="domcontentloaded",
            )
        except Exception as exc:
            _close_context(context)
            return ReadinessResult(
                ok=False,
                stage="external_navigation",
                error_kind=_classify_exception(exc),
                error=str(exc),
            )

    _close_context(context)
    return ReadinessResult(ok=True, stage="ok")


def _looks_like_challenge(title: str, final_url: str, text: str) -> bool:
    lower_title = title.lower()
    lower_url = final_url.lower()
    lower_text = text.lower()
    lead = lower_text[:1200]

    if "google.com/sorry/" in lower_url:
        return True
    if "consent.google.com/" in lower_url:
        return True
    if lower_title.startswith("before you continue") and "accept all" in lead and "reject all" in lead:
        return True
    return any(marker in lead for marker in _CHALLENGE_MARKERS)


def _classify_exception(exc: Exception) -> str:
    name = exc.__class__.__name__.lower()
    message = str(exc).lower()
    if "timeout" in name or "timeout" in message or "timed out" in message:
        return "navigation_timeout"
    if any(marker in message for marker in _CHALLENGE_MARKERS):
        return "challenge_detected"
    return "unknown_error"


def _close_context(context: Any) -> None:
    try:
        context.close()
    except Exception:
        pass
