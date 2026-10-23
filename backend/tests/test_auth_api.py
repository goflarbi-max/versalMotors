from backend.tests.conftest import authenticate


def _csrf(client) -> str:
    return client.get("/api/v1/auth/csrf").json()["csrf_token"]


def test_protected_routes_require_authentication(api_client):
    response = api_client.get("/api/v1/overview/kpis")

    assert response.status_code == 401
    assert response.json()["message"] == "Authentication required"
    assert "request_id" in response.json()


def test_login_cookie_me_and_logout(api_client):
    authenticate(api_client)

    cookie = api_client.cookies.get("versal_session")
    assert cookie
    login_cookie = api_client.cookies.jar._cookies["testserver.local"]["/"]["versal_session"]
    assert login_cookie.secure is True
    assert login_cookie.has_nonstandard_attr("HttpOnly")
    assert api_client.get("/api/v1/auth/me").json() == {
        "authenticated": True,
        "email": "demo@versalmotors.com",
    }

    token = _csrf(api_client)
    response = api_client.post(
        "/api/v1/auth/logout",
        headers={"Origin": "https://testserver", "X-CSRF-Token": token},
    )
    assert response.status_code == 204
    assert api_client.get("/api/v1/auth/me").status_code == 401


def test_wrong_and_unknown_users_receive_same_safe_message(api_client):
    token = _csrf(api_client)
    wrong = api_client.post(
        "/api/v1/auth/login",
        json={"email": "demo@versalmotors.com", "password": "wrong"},
        headers={"Origin": "https://testserver", "X-CSRF-Token": token},
    )
    token = _csrf(api_client)
    unknown = api_client.post(
        "/api/v1/auth/login",
        json={"email": "unknown@versalmotors.com", "password": "wrong"},
        headers={"Origin": "https://testserver", "X-CSRF-Token": token},
    )

    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json()["message"] == unknown.json()["message"] == "Invalid email or password"


def test_login_requires_allowed_origin_and_matching_csrf(api_client):
    payload = {"email": "demo@versalmotors.com", "password": "VersalDemo2026!"}
    no_origin = api_client.post("/api/v1/auth/login", json=payload)
    wrong_csrf = api_client.post(
        "/api/v1/auth/login",
        json=payload,
        headers={"Origin": "https://testserver", "X-CSRF-Token": "wrong"},
    )

    assert no_origin.status_code == 403
    assert wrong_csrf.status_code == 403


def test_login_locks_after_five_failures(api_client):
    for attempt in range(5):
        token = _csrf(api_client)
        response = api_client.post(
            "/api/v1/auth/login",
            json={"email": "locked@versalmotors.com", "password": "wrong"},
            headers={"Origin": "https://testserver", "X-CSRF-Token": token},
        )
        assert response.status_code == (429 if attempt == 4 else 401)

    assert response.headers["retry-after"] == "60"
    assert "Try again in 60 seconds" in response.json()["message"]


def test_tampered_cookie_is_rejected(api_client):
    authenticate(api_client)
    cookie = api_client.cookies.get("versal_session")
    api_client.cookies.set("versal_session", f"{cookie}tampered", domain="testserver.local", path="/")

    assert api_client.get("/api/v1/auth/me").status_code == 401
