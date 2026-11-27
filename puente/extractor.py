"""Turn one free-text message into structured offer/need data with the LLM (AGENTS.md, Extractor)."""

import json
from datetime import datetime
from functools import lru_cache
from typing import Literal
from uuid import uuid4

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from puente import guardrails, store
from puente.config import (
    CANONICAL_ITEMS, CATEGORIES, DEMO_NOW, EXTRACTOR_MODEL, ITEM_TYPES, LLM_EFFORT,
    MODEL_FLAGS, PROMPTS_DIR, ROOT, URGENCIES,
)

load_dotenv(ROOT / ".env")

MAX_TOKENS = 4096


# --- Schema: pydantic for validation, JSON schema for the API's structured outputs ---

class Item(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal[tuple(ITEM_TYPES)]
    category: Literal[tuple(CATEGORIES)]
    what: Literal[tuple(CANONICAL_ITEMS)]
    quantity: float | None = Field(ge=0)
    unit: str | None
    conditions: str | None
    can_deliver: bool | None


class Extraction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    language: str = Field(min_length=2, max_length=3)
    items: list[Item]
    location_text: str | None
    available_from: str | None
    available_until: str | None
    urgency: Literal[tuple(URGENCIES)]
    urgency_reason: str
    needs_verification: bool
    flags: list[Literal[tuple(MODEL_FLAGS)]]
    follow_up_question: str | None
    confidence: float = Field(ge=0, le=1)

    @field_validator("available_from", "available_until")
    @classmethod
    def _iso_time(cls, value: str | None) -> str | None:
        if value is not None:
            datetime.fromisoformat(value)  # raises ValueError if not ISO
        return value


def _nullable(schema: dict) -> dict:
    return {"anyOf": [schema, {"type": "null"}]}


_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ITEM_TYPES},
        "category": {"type": "string", "enum": CATEGORIES},
        "what": {"type": "string", "enum": CANONICAL_ITEMS},
        "quantity": _nullable({"type": "number"}),
        "unit": _nullable({"type": "string"}),
        "conditions": _nullable({"type": "string"}),
        "can_deliver": _nullable({"type": "boolean"}),
    },
    "required": ["type", "category", "what", "quantity", "unit", "conditions", "can_deliver"],
    "additionalProperties": False,
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "language": {"type": "string"},
        "items": {"type": "array", "items": _ITEM_SCHEMA},
        "location_text": _nullable({"type": "string"}),
        "available_from": _nullable({"type": "string"}),
        "available_until": _nullable({"type": "string"}),
        "urgency": {"type": "string", "enum": URGENCIES},
        "urgency_reason": {"type": "string"},
        "needs_verification": {"type": "boolean"},
        "flags": {"type": "array", "items": {"type": "string", "enum": MODEL_FLAGS}},
        "follow_up_question": _nullable({"type": "string"}),
        "confidence": {"type": "number"},
    },
    "required": list(Extraction.model_fields),
    "additionalProperties": False,
}


# --- Prompt and client ---

@lru_cache(maxsize=1)
def _system_prompt() -> str:
    text = (PROMPTS_DIR / "extractor.md").read_text(encoding="utf-8")
    return (
        text.replace("{{CANONICAL_ITEMS}}", ", ".join(CANONICAL_ITEMS))
        .replace("{{DEMO_NOW}}", DEMO_NOW.isoformat(timespec="minutes"))
    )


@lru_cache(maxsize=1)
def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def _call_model(messages: list[dict], message_id: str) -> anthropic.types.Message:
    response = _client().messages.create(
        model=EXTRACTOR_MODEL,
        max_tokens=MAX_TOKENS,
        system=_system_prompt(),
        output_config={"effort": LLM_EFFORT, "format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}},
        messages=messages,
    )
    store.log_llm_call(message_id, "extract", EXTRACTOR_MODEL,
                       response.usage.input_tokens, response.usage.output_tokens)
    return response


def _parse(response: anthropic.types.Message) -> Extraction:
    """Validate the model output. Raises ValueError with a readable reason if it is unusable."""
    if response.stop_reason == "refusal":
        raise ValueError("model declined the request")
    if response.stop_reason == "max_tokens":
        raise ValueError("output was cut off (max_tokens)")
    text = next((b.text for b in response.content if b.type == "text"), "")
    try:
        return Extraction.model_validate(json.loads(text))
    except (json.JSONDecodeError, ValidationError) as err:
        raise ValueError(f"invalid output: {err}") from err


def _fallback(message_id: str, reasons: list[str]) -> dict:
    """Empty extraction used when the LLM fails; the coordinator reviews the message by hand."""
    return {
        "message_id": message_id, "language": None, "items": [], "location_text": None,
        "available_from": None, "available_until": None, "urgency": "orange",
        "urgency_reason": "extraction failed, needs manual review", "needs_verification": False,
        "flags": [], "follow_up_question": None, "confidence": 0.0,
        "status": "needs_review", "review_reasons": reasons, "extraction_failed": True,
    }


# --- Public API ---

def extract(message_text: str, message_id: str | None = None) -> dict:
    """Extract structured data from one message. Never raises; failures return status needs_review."""
    message_id = message_id or f"msg-{uuid4().hex[:8]}"
    messages = [{"role": "user", "content": guardrails.wrap_message(message_text)}]
    errors: list[str] = []

    result: dict | None = None
    for _attempt in range(2):  # first try + one retry
        try:
            response = _call_model(messages, message_id)
        except anthropic.APIError as err:
            errors.append(f"API error: {type(err).__name__}")
            continue
        try:
            result = _parse(response).model_dump()
            break
        except ValueError as err:
            errors.append(str(err)[:300])
            previous = next((b.text for b in response.content if b.type == "text"), "")
            messages = messages[:1] + [
                {"role": "assistant", "content": previous or "(no output)"},
                {"role": "user", "content": f"That output was not valid: {str(err)[:300]}. "
                                            "Return the corrected JSON object only."},
            ]

    if result is None:
        result = _fallback(message_id, errors)
    else:
        result["message_id"] = message_id

    result = guardrails.apply_safety_net(result, message_text)  # runs even if the LLM failed
    return guardrails.apply_code_rules(result)  # also sets status
