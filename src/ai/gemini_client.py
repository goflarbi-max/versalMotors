"""Optional Gemini client with bounded retries and safe failure results."""

import os
import time
from typing import Any

from dotenv import load_dotenv

load_dotenv()

TRANSIENT_CODES = {429, 500, 502, 503, 504}


def _status_code(error: Exception) -> int | None:
    for attribute in ("status_code", "code"):
        value = getattr(error, attribute, None)
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    match = next((code for code in TRANSIENT_CODES if str(code) in str(error)), None)
    return match


def generate_text(
    prompt: str,
    *,
    api_key: str | None = None,
    model: str | None = None,
    attempts: int = 3,
    delays: tuple[float, ...] = (0.5, 1.5),
) -> dict[str, Any]:
    """Generate text, retry transient API failures, and never raise to the UI."""
    resolved_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not resolved_key:
        return {"ok": False, "text": "", "reason": "not_configured", "attempts": 0}

    client = None
    try:
        from google import genai

        client = genai.Client(api_key=resolved_key)
        for attempt in range(1, max(1, attempts) + 1):
            try:
                response = client.models.generate_content(
                    model=model or os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
                    contents=prompt,
                )
                text = (response.text or "").strip()
                if text:
                    return {"ok": True, "text": text, "reason": "", "attempts": attempt}
                return {"ok": False, "text": "", "reason": "empty_response", "attempts": attempt}
            except Exception as error:
                code = _status_code(error)
                transient = code in TRANSIENT_CODES or isinstance(error, TimeoutError)
                if not transient or attempt >= attempts:
                    reason = f"service_unavailable_{code}" if transient else "api_error"
                    return {"ok": False, "text": "", "reason": reason, "attempts": attempt}
                time.sleep(delays[min(attempt - 1, len(delays) - 1)])
    except Exception:
        return {"ok": False, "text": "", "reason": "client_unavailable", "attempts": 0}
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
    return f"Gemini is unavailable; verified database evidence is shown instead: {evidence[:2]}"
