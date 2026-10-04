"""Optional Gemini client with bounded model failover and safe results."""

import os
import random
import time
from typing import Any, Iterable

from dotenv import load_dotenv

load_dotenv()

TRANSIENT_CODES = {429, 500, 502, 503, 504}
DEFAULT_MODEL = "gemini-3.8-flash"
DEFAULT_FALLBACK_MODELS = ("gemini-3.5-flash-lite",)


def _status_code(error: Exception) -> int | None:
    for attribute in ("status_code", "code"):
        value = getattr(error, attribute, None)
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return next((code for code in TRANSIENT_CODES if str(code) in str(error)), None)


def _model_chain(primary: str | None, fallbacks: Iterable[str] | None) -> tuple[str, ...]:
    configured = os.getenv("GEMINI_FALLBACK_MODELS", "")
    configured_fallbacks = tuple(item.strip() for item in configured.split(",") if item.strip())
    candidates = (
        primary or os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
        *(tuple(fallbacks) if fallbacks is not None else configured_fallbacks or DEFAULT_FALLBACK_MODELS),
    )
    return tuple(dict.fromkeys(model for model in candidates if model))


def _failure(reason: str, attempts: int, attempted_models: list[str]) -> dict[str, Any]:
    return {
        "ok": False,
        "text": "",
        "reason": reason,
        "attempts": attempts,
        "model_used": None,
        "attempted_models": attempted_models,
    }


def generate_text(
    prompt: str,
    *,
    api_key: str | None = None,
    model: str | None = None,
    fallback_models: Iterable[str] | None = None,
    attempts: int | None = None,
    delays: tuple[float, ...] = (0.5, 1.5),
) -> dict[str, Any]:
    """Try a primary and lighter models; never raise an API error to callers."""
    resolved_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not resolved_key:
        return _failure("not_configured", 0, [])

    try:
        max_attempts = max(1, attempts or int(os.getenv("GEMINI_MAX_ATTEMPTS", "2")))
    except ValueError:
        max_attempts = 2
    models = _model_chain(model, fallback_models)
    client = None
    total_attempts = 0
    attempted_models: list[str] = []
    last_reason = "service_unavailable"

    try:
        from google import genai

        client = genai.Client(api_key=resolved_key)
        for candidate in models:
            attempted_models.append(candidate)
            for attempt in range(1, max_attempts + 1):
                total_attempts += 1
                try:
                    response = client.models.generate_content(model=candidate, contents=prompt)
                    text = (response.text or "").strip()
                    if text:
                        return {
                            "ok": True,
                            "text": text,
                            "reason": "",
                            "attempts": total_attempts,
                            "model_used": candidate,
                            "attempted_models": attempted_models,
                        }
                    last_reason = "empty_response"
                    break
                except Exception as error:
                    code = _status_code(error)
                    transient = code in TRANSIENT_CODES or isinstance(error, TimeoutError)
                    if not transient:
                        return _failure("api_error", total_attempts, attempted_models)
                    last_reason = f"service_unavailable_{code or 'timeout'}"
                    if attempt < max_attempts:
                        base_delay = delays[min(attempt - 1, len(delays) - 1)] if delays else 0
                        time.sleep(base_delay + random.uniform(0, base_delay * 0.2))
        return _failure(last_reason, total_attempts, attempted_models)
    except Exception:
        return _failure("client_unavailable", total_attempts, attempted_models)
    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass


def get_ai_response(question: str, evidence: list) -> str:
    """Return an evidence response or a deterministic offline summary."""
    prompt = (
        "You are the VersalMotors BI assistant. Answer only from this evidence.\n"
        f"Question: {question}\nEvidence: {str(evidence)[:3000]}\n"
        "Give a short answer in 3-4 lines using only numbers present in the evidence."
    )
    result = generate_text(prompt)
    if result["ok"]:
        return result["text"]
    if not evidence:
        return "No matching evidence is available. Gemini is optional and currently unavailable."
    return "Gemini is temporarily unavailable. The verified database evidence remains available."
