"""Deterministic input and evidence guardrails for AI responses."""

import json
import os
import re
from typing import Any

NUMBER_RE = re.compile(r"(?:GHS\s*)?\b\d[\d,]*\.?\d*\b%?")
INJECTION_PATTERNS = ("ignore your instructions", "ignore previous", "system prompt", "drop table", "delete from", ";--")
UNANSWERABLE_KEYWORDS = ("weather", "football", "president", "celebrity", "recipe", "joke")
UNANSWERABLE_PHRASES = (
    "competitor", "competition", "predict", "forecast", "next year's sales",
    "next year sales",
)
KNOWN_GIBBERISH = {"asdf", "qwerty", "asdfgh", "lorem ipsum"}


def validate_question(question: str) -> tuple[bool, str]:
    text = question.strip()
    if len(text) < 3:
        return False, "Question too short. Please ask a business question."
    if len(text) > 500:
        return False, "Question too long (maximum 500 characters)."
    lowered = text.lower()
    if lowered in KNOWN_GIBBERISH:
        return False, "Please ask a specific versalMotors business question."
    for pattern in INJECTION_PATTERNS:
        if pattern in lowered:
            return False, "The question contains a disallowed instruction."
    return True, ""


def handle_unanswerable(question: str) -> str | None:
    lowered = question.lower()
    if any(word in lowered for word in UNANSWERABLE_KEYWORDS):
        return "I can only answer questions supported by versalMotors business data."
    if any(phrase in lowered for phrase in UNANSWERABLE_PHRASES):
        return (
            "The available versalMotors data cannot support competitor comparisons "
            "or future forecasts. I can report verified historical performance instead."
        )
    return None


def check_api_key() -> bool:
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))


def extract_numbers(text: str) -> list[str]:
    return [match.replace("GHS", "").replace(",", "").replace("%", "").strip() for match in NUMBER_RE.findall(text or "")]


def verify_facts_against_evidence(response_text: str, evidence: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    evidence_blob = json.dumps(evidence, default=str).replace(",", "").lower()
    missing = [number for number in extract_numbers(response_text) if number and number.lower() not in evidence_blob]
    return not missing, missing


def build_grounded_response(raw_response: str, evidence: list[dict[str, Any]], fallback_insights: str = "") -> dict[str, Any]:
    if not evidence or not raw_response:
        return {"status": "fallback", "response": fallback_insights or "No verified evidence was returned.", "missing": []}
    facts = re.search(r"FACTS:(.*?)(?:\n\n|$)", raw_response, re.DOTALL | re.IGNORECASE)
    verified, missing = verify_facts_against_evidence(facts.group(1) if facts else raw_response, evidence)
    if not verified:
        return {"status": "unverified", "response": fallback_insights or "Use the evidence table as the verified result.", "missing": missing}
    display_response = re.sub(
        r"^\s*FACTS:\s*", "", raw_response, count=1, flags=re.IGNORECASE
    ).strip()
    return {"status": "verified", "response": display_response, "missing": []}
