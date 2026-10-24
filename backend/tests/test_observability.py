from __future__ import annotations

import json
import logging


def test_request_log_is_structured_and_excludes_query_values(api_client, caplog) -> None:
    caplog.set_level(logging.INFO, logger="versalmotors.api")
    response = api_client.get("/health/live?password=must-not-appear")
    assert response.status_code == 200

    records = [json.loads(record.message) for record in caplog.records if record.name == "versalmotors.api"]
    access = records[-1]
    assert access["route"] == "/health/live"
    assert access["method"] == "GET"
    assert access["status"] == 200
    assert access["error_category"] == "none"
    assert access["request_id"] == response.headers["x-request-id"]
    assert "must-not-appear" not in caplog.text
    assert "password" not in caplog.text
