"""Audit tests proving Gemini is optional and transient failures are retried."""

from types import SimpleNamespace

from src.ai.fallback import fallback_sql_for_question
from src.ai.gemini_client import generate_text


def test_generate_text_without_api_key_returns_safe_result(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    result = generate_text("test")

    assert result == {
        "ok": False,
        "text": "",
        "reason": "not_configured",
        "attempts": 0,
    }


def test_generate_text_retries_a_503(monkeypatch):
    from google import genai

    calls = []

    class ServiceUnavailable(Exception):
        status_code = 503

    class FakeModels:
        def generate_content(self, **kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                raise ServiceUnavailable("503 unavailable")
            return SimpleNamespace(text="recovered")

    fake_client = SimpleNamespace(models=FakeModels(), close=lambda: None)
    monkeypatch.setattr(genai, "Client", lambda **kwargs: fake_client)

    result = generate_text("test", api_key="test-key", attempts=3, delays=(0, 0))

    assert result["ok"] is True
    assert result["text"] == "recovered"
    assert result["attempts"] == 2
    assert len(calls) == 2


def test_offline_router_supports_every_quick_question():
    questions = [
        "How did completed-sale revenue change by month?",
        "Which branch had the highest completed-sale revenue?",
        "Which available vehicles have been in inventory over 90 days?",
        "Which branch had the most valid complaints?",
    ]

    assert all(fallback_sql_for_question(question)[0] for question in questions)
