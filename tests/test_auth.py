"""Unit tests for the session-scoped VersalMotors authentication layer."""

import json
from pathlib import Path

import bcrypt
import pytest
from streamlit.testing.v1 import AppTest

import src.auth.auth as auth
from src.ui import sidebar, theme


DEMO_EMAIL = "demo@versalmotors.com"
DEMO_PASSWORD = "VersalDemo2026!"
APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.fixture
def auth_state(monkeypatch):
    state = {}
    password_hash = bcrypt.hashpw(
        DEMO_PASSWORD.encode("utf-8"), bcrypt.gensalt(rounds=4)
    ).decode("utf-8")
    monkeypatch.setattr(auth, "_get_session_state", lambda: state)
    monkeypatch.setattr(auth, "_load_users", lambda: {DEMO_EMAIL: password_hash})
    monkeypatch.setattr(auth, "_now", lambda: 1_000.0)
    return state


def test_correct_credentials_pass(auth_state):
    user = auth.verify_credentials(DEMO_EMAIL, DEMO_PASSWORD)
    auth.login(user)

    assert user == {"email": DEMO_EMAIL}
    assert auth_state[auth.AUTHENTICATED_KEY] is True
    assert auth_state[auth.AUTH_EMAIL_KEY] == DEMO_EMAIL


def test_wrong_password_fails_with_safe_message(auth_state):
    with pytest.raises(auth.AuthenticationError) as error:
        auth.verify_credentials(DEMO_EMAIL, "wrong-password")

    assert str(error.value) == auth.INVALID_CREDENTIALS_MESSAGE


def test_unknown_email_uses_same_failure_message(auth_state):
    with pytest.raises(auth.AuthenticationError) as wrong_password:
        auth.verify_credentials(DEMO_EMAIL, "wrong-password")
    auth_state.clear()
    with pytest.raises(auth.AuthenticationError) as unknown_email:
        auth.verify_credentials("unknown@versalmotors.com", DEMO_PASSWORD)

    assert str(wrong_password.value) == str(unknown_email.value)
    assert str(unknown_email.value) == auth.INVALID_CREDENTIALS_MESSAGE


@pytest.mark.parametrize(
    ("email", "password"),
    [("", DEMO_PASSWORD), (DEMO_EMAIL, ""), ("", "")],
)
def test_empty_input_is_rejected_before_verification(auth_state, email, password):
    with pytest.raises(auth.AuthenticationError) as error:
        auth.verify_credentials(email, password)

    assert str(error.value) == "Email and password are required"
    assert auth_state == {}


def test_session_locks_for_60_seconds_after_five_failures(auth_state):
    for _ in range(4):
        with pytest.raises(auth.AuthenticationError, match="Invalid email or password"):
            auth.verify_credentials(DEMO_EMAIL, "wrong-password")

    with pytest.raises(auth.AuthenticationError, match="Try again in 60 seconds"):
        auth.verify_credentials(DEMO_EMAIL, "wrong-password")
    with pytest.raises(auth.AuthenticationError, match="Try again in 60 seconds"):
        auth.verify_credentials(DEMO_EMAIL, DEMO_PASSWORD)

    assert auth_state[auth.FAILED_ATTEMPTS_KEY] == 5
    assert auth_state[auth.LOCKED_UNTIL_KEY] == 1_060.0


def test_password_is_never_stored_in_session_state(auth_state):
    user = auth.verify_credentials(DEMO_EMAIL, DEMO_PASSWORD)
    auth.login(user)

    assert DEMO_PASSWORD not in auth_state
    assert DEMO_PASSWORD not in auth_state.values()
    assert not any("password" in str(key).lower() for key in auth_state)


def test_demo_credentials_work_when_deployment_has_no_auth_config(monkeypatch):
    state = {}
    monkeypatch.delenv("VERSALMOTORS_AUTH_USERS_JSON", raising=False)
    monkeypatch.setattr(auth.st, "secrets", {})
    monkeypatch.setattr(auth, "_get_session_state", lambda: state)

    users = auth._load_users()
    user = auth.verify_credentials(DEMO_EMAIL, DEMO_PASSWORD)

    assert set(users) == {DEMO_EMAIL}
    assert bcrypt.checkpw(
        DEMO_PASSWORD.encode("utf-8"), users[DEMO_EMAIL].encode("utf-8")
    )
    assert user == {"email": DEMO_EMAIL}


def test_unauthenticated_navigation_does_not_register_protected_pages(monkeypatch):
    monkeypatch.setattr(auth, "_is_streamlit_test_session", lambda: False)
    app = AppTest.from_file(APP, default_timeout=30).run()

    assert not app.exception
    assert [title.value for title in app.title] == [
        "VersalMotors Business Intelligence"
    ]
    with pytest.raises(ValueError):
        app.switch_page("pages/overview.py")


def test_login_ui_never_keeps_password_in_user_session_state(monkeypatch):
    password_hash = bcrypt.hashpw(
        DEMO_PASSWORD.encode("utf-8"), bcrypt.gensalt(rounds=4)
    ).decode("utf-8")
    monkeypatch.setenv(
        "VERSALMOTORS_AUTH_USERS_JSON",
        json.dumps({DEMO_EMAIL: password_hash}),
    )
    monkeypatch.setattr(auth, "_is_streamlit_test_session", lambda: False)

    app = AppTest.from_file(APP, default_timeout=30).run()
    app.text_input[0].set_value(DEMO_EMAIL)
    app.text_input[1].set_value(DEMO_PASSWORD)
    app.button(key="sign_in").click().run()

    user_state = app.session_state._state.filtered_state
    assert not app.exception
    assert user_state[auth.AUTHENTICATED_KEY] is True
    assert user_state[auth.AUTH_EMAIL_KEY] == DEMO_EMAIL
    assert DEMO_PASSWORD not in user_state.values()


def test_login_theme_is_always_light_regardless_of_session_state(monkeypatch):
    monkeypatch.setitem(theme.st.session_state, "sidebar_dark_mode", True)

    assert theme.login_theme_type() == "light"


def test_sign_out_resets_stored_theme_to_light(monkeypatch):
    state = {
        sidebar._THEME_KEY: True,
        sidebar._THEME_CONTEXT_KEY: True,
        auth.AUTHENTICATED_KEY: True,
    }
    monkeypatch.setattr(sidebar.st, "session_state", state)
    monkeypatch.setattr(sidebar, "logout", lambda: state.clear())

    sidebar._logout_to_light()

    assert state[sidebar._THEME_KEY] is False
    assert state[sidebar._THEME_CONTEXT_KEY] is False
    assert auth.AUTHENTICATED_KEY not in state

