"""Headless test for the user-visible no-Gemini path."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

import src.ai.gemini_client as gemini_client


def test_complaint_question_survives_model_outage_without_raw_error(monkeypatch):
    calls = []

    def unavailable(*args, **kwargs):
        calls.append((args, kwargs))
        return {
            "ok": False,
            "text": "",
            "reason": "service_unavailable_503",
            "attempts": 4,
            "model_used": None,
            "attempted_models": ["primary", "lighter"],
        }

    monkeypatch.setattr(gemini_client, "generate_text", unavailable)
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path, default_timeout=30).run()
    app.switch_page("pages/ask_the_business.py").run()
    app.chat_input[0].set_value("Which branch had the most valid complaints?").run()

    visible = [
        str(element.value)
        for collection in (app.markdown, app.info, app.warning, app.error)
        for element in collection
    ]
    assert not app.exception
    assert app.dataframe
    assert len(calls) == 1
    assert not any("503" in text or "UNAVAILABLE" in text for text in visible)


def test_all_quick_questions_and_typed_follow_ups_work_in_one_session(monkeypatch):
    calls = []

    def unavailable(*args, **kwargs):
        calls.append((args, kwargs))
        return {
            "ok": False,
            "text": "",
            "reason": "service_unavailable_503",
            "attempts": 4,
            "model_used": None,
            "attempted_models": ["primary", "lighter"],
        }

    monkeypatch.setattr(gemini_client, "generate_text", unavailable)
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path, default_timeout=30).run()
    app.switch_page("pages/ask_the_business.py").run()

    app.button(key="quick_revenue_trend").click().run()
    app.button(key="quick_best_branch").click().run()
    app.button(key="quick_aged_inventory").click().run()
    app.button(key="quick_complaints").click().run()
    app.chat_input[0].set_value(
        "How did completed-sale revenue change by month?"
    ).run()

    assistant_answers = [
        message["content"]
        for message in app.session_state["business_messages"]
        if message["role"] == "assistant"
    ]
    assert not app.exception
    assert len(assistant_answers) == 5
    assert "Completed-sale revenue in" in assistant_answers[0]
    assert "highest completed-sale revenue" in assistant_answers[1]
    assert "oldest available vehicle" in assistant_answers[2]
    assert "most valid complaints" in assistant_answers[3]
    assert "Completed-sale revenue in" in assistant_answers[4]
    # The four buttons bypass Gemini; only the typed question calls the client.
    assert len(calls) == 1
