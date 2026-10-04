"""Audit tests proving Gemini is optional and transient failures are retried."""

from types import SimpleNamespace

import pandas as pd

from src.ai.fallback import (
    build_fallback_evidence,
    fallback_response,
    fallback_sql_for_question,
    run_with_reviewed_fallback,
)
from src.ai.gemini_client import generate_text
from src.ai.guardrails import build_grounded_response


def test_generate_text_without_api_key_returns_safe_result(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    result = generate_text("test")

    assert result["ok"] is False
    assert result["reason"] == "not_configured"
    assert result["attempts"] == 0
    assert result["attempted_models"] == []


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


def test_generate_text_uses_lighter_model_after_primary_503(monkeypatch):
    from google import genai

    calls = []

    class ServiceUnavailable(Exception):
        status_code = 503

    class FakeModels:
        def generate_content(self, **kwargs):
            calls.append(kwargs["model"])
            if kwargs["model"] == "primary-model":
                raise ServiceUnavailable("high demand")
            return SimpleNamespace(text="lighter model response")

    monkeypatch.setattr(
        genai, "Client",
        lambda **kwargs: SimpleNamespace(models=FakeModels(), close=lambda: None),
    )

    result = generate_text(
        "test", api_key="test-key", model="primary-model",
        fallback_models=("lighter-model",), attempts=2, delays=(0, 0),
    )

    assert result["ok"] is True
    assert result["model_used"] == "lighter-model"
    assert result["attempts"] == 3
    assert calls == ["primary-model", "primary-model", "lighter-model"]


def test_generate_text_handles_429_across_all_models_without_raw_error(monkeypatch):
    from google import genai

    class RateLimited(Exception):
        status_code = 429

    class FakeModels:
        def generate_content(self, **kwargs):
            raise RateLimited("private raw provider message")

    monkeypatch.setattr(
        genai, "Client",
        lambda **kwargs: SimpleNamespace(models=FakeModels(), close=lambda: None),
    )
    result = generate_text(
        "test", api_key="test-key", model="primary",
        fallback_models=("lighter",), attempts=1, delays=(0,),
    )

    assert result["ok"] is False
    assert result["reason"] == "service_unavailable_429"
    assert "private raw provider message" not in str(result)


def test_invalid_generated_sql_uses_reviewed_query():
    calls = []

    def runner(sql):
        calls.append(sql)
        if "read_csv" in sql:
            raise ValueError("blocked")
        return pd.DataFrame({"month": ["2026-01-01"], "revenue": [45000.0]})

    result, _, used_fallback = run_with_reviewed_fallback(
        "How did completed-sale revenue change by month?",
        "SELECT * FROM read_csv('secret.csv')",
        runner,
    )

    assert used_fallback is True
    assert result["revenue"].tolist() == [45000.0]
    assert len(calls) == 2


def test_offline_evidence_and_response_are_grounded():
    frame = pd.DataFrame({"branch_id": [3], "branch_name": ["Tema"], "complaint_count": [12]})
    evidence = build_fallback_evidence(
        "Which branch had the most valid complaints?", frame
    )
    response = fallback_response("Which branch had the most valid complaints?", evidence)

    assert evidence[0]["type"] == "fact"
    assert evidence[0]["source_table"] == "complaints"
    assert response == "Tema had the most valid complaints, with 12."


def test_monthly_revenue_fallback_answers_the_change_question():
    frame = pd.DataFrame({
        "month": [pd.Timestamp("2026-08-01"), pd.Timestamp("2026-09-01")],
        "revenue": [100_000.0, 125_000.0],
        "previous_month_revenue": [None, 100_000.0],
        "change_amount": [None, 25_000.0],
        "change_pct": [None, 25.0],
    })
    question = "How did completed-sale revenue change by month?"
    evidence = build_fallback_evidence(question, frame)

    response = fallback_response(question, evidence)

    assert response == (
        "Completed-sale revenue in September 2026 was GHS 125,000.00. "
        "It increased by GHS 25,000.00 (25.0%) from the previous month."
    )


def test_branch_revenue_fallback_is_not_mislabeled_as_monthly():
    frame = pd.DataFrame({"branch_name": ["Accra"], "revenue": [800_000.0]})
    question = "Which branch had the highest completed-sale revenue?"
    evidence = build_fallback_evidence(question, frame)

    assert fallback_response(question, evidence) == (
        "Accra had the highest completed-sale revenue at GHS 800,000.00."
    )


def test_offline_empty_result_is_safe():
    evidence = build_fallback_evidence("complaints", pd.DataFrame())
    assert fallback_response("complaints", evidence) == "No matching verified records were found for this question."


def test_grounded_response_removes_facts_heading_from_user_output():
    evidence = [{"value": 12}]
    result = build_grounded_response("FACTS: There were 12 complaints.", evidence)

    assert result["status"] == "verified"
    assert result["response"] == "There were 12 complaints."
    assert "FACTS:" not in result["response"]


def test_offline_router_supports_every_quick_question():
    questions = [
        "How did completed-sale revenue change by month?",
        "Which branch had the highest completed-sale revenue?",
        "Which available vehicles have been in inventory over 90 days?",
        "Which branch had the most valid complaints?",
    ]

    assert all(fallback_sql_for_question(question)[0] for question in questions)
