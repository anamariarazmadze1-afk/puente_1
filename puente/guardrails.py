"""Guardrails: input wrapping, red keyword safety net and code-set rules (AGENTS.md, Rules 1-3, 5)."""

import re
import unicodedata

from puente.config import MIN_CONFIDENCE

# Danger keywords, written without accents (text is normalised before matching).
# About people in danger, not water levels (AGENTS.md rule 3).
_RED_PATTERNS: dict[str, str] = {
    # English
    "trapped": r"\btrapped\b",
    "not breathing": r"\b(not|isnt|isn't|aint|stopped|no longer)\s+breath(ing|e)\b",
    "can't breathe": r"\b(cant|can't|cannot|can not)\s+breathe\b",
    "unconscious": r"\bunconscious\b",
    "bleeding": r"\bbleed(ing|s)?\b",
    "drowning": r"\bdrown(ing|s)?\b",
    # Spanish
    "atrapado": r"\batrapad[oa]s?\b",
    "no respira": r"\bno\s+respira(n)?\b",
    "inconsciente": r"\binconscientes?\b",
    "sangra": r"\bsangr(a|an|ando)\b",
    "ahogo": r"\b(ahogo|ahogando(se)?|se\s+ahoga(n)?)\b",
    # Catalan
    "atrapat": r"\batrapa(t|da|ts|des)\b",
    "inconscient": r"\binconscients?\b",
    "sagna": r"\bsagn(a|en|ant)\b",
    "s'ofega": r"\b(s'?ofega(n)?|ofegant(-se)?)\b",
}
_RED_REGEXES = {name: re.compile(pattern) for name, pattern in _RED_PATTERNS.items()}


def normalise(text: str) -> str:
    """Lowercase, strip accents and unify apostrophes so keyword matching is robust."""
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def wrap_message(text: str) -> str:
    """Wrap untrusted message text in <message> tags, neutralising any tags inside it."""
    cleaned = re.sub(r"</?\s*message\s*>", "[tag removed]", text, flags=re.IGNORECASE)
    return f"<message>{cleaned}</message>"


def keyword_red(text: str) -> str | None:
    """Return the first danger keyword found in the text, or None."""
    norm = normalise(text)
    for name, regex in _RED_REGEXES.items():
        if regex.search(norm):
            return name
    return None


def apply_safety_net(result: dict, text: str) -> dict:
    """Force urgency to red if a danger keyword appears. Records the source of the urgency."""
    keyword = keyword_red(text)
    result["urgency_source"] = "model"
    result["safety_net_keyword"] = keyword
    if keyword and result.get("urgency") != "red":
        result["urgency"] = "red"
        result["urgency_reason"] = f"safety net: keyword '{keyword}'"
        result["urgency_source"] = "keyword"
    return result


def apply_code_rules(result: dict) -> dict:
    """Code-set rules: per-item verification (only volunteer_medical) and low-confidence review."""
    for item in result.get("items", []):
        item["needs_verification"] = item.get("what") == "volunteer_medical"
    if result.get("confidence", 0) < MIN_CONFIDENCE and result.get("status") != "needs_review":
        result["status"] = "needs_review"
        result.setdefault("review_reasons", []).append("low confidence")
    return result
