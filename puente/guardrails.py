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


def merge_duplicate_items(items: list[dict]) -> list[dict]:
    """Merge items with the same type and `what` (e.g. nappies + formula = one baby_supplies need).

    Quantity becomes the largest of the merged quantities, not the sum, so a need is not double counted.
    """
    merged: dict[tuple, dict] = {}
    for index, item in enumerate(items):
        # `other` items describe different things, so they are never merged.
        key = (item["type"], item["what"]) if item["what"] != "other" else ("other", index)
        if key not in merged:
            merged[key] = dict(item)
            continue
        kept = merged[key]
        quantities = [q for q in (kept["quantity"], item["quantity"]) if q is not None]
        kept["quantity"] = max(quantities) if quantities else None
        conditions = [c for c in (kept["conditions"], item["conditions"]) if c]
        kept["conditions"] = "; ".join(dict.fromkeys(conditions)) or None
    return list(merged.values())


def drop_unsafe_items(result: dict) -> dict:
    """Rule 7: if the message is flagged unsafe_donation, no food offers are created (homemade food)."""
    if "unsafe_donation" in result.get("flags", []):
        result["items"] = [
            it for it in result["items"] if not (it["type"] == "offer" and it["what"] == "food")
        ]
    return result


def set_status(result: dict) -> dict:
    """Decide the message status from flags, items and location (AGENTS.md status values).

    Priority: needs_review > declined > needs_follow_up > new.
    """
    if result.get("status") == "needs_review":  # extraction already failed
        return result
    flags = set(result.get("flags", []))
    reasons = result.setdefault("review_reasons", [])
    if flags & {"injection", "scam"}:
        reasons.append("flagged: " + ", ".join(sorted(flags & {"injection", "scam"})))
    if result.get("confidence", 0) < MIN_CONFIDENCE:
        reasons.append("low confidence")
    if reasons:
        result["status"] = "needs_review"
    elif not result["items"] and flags & {"money", "unsafe_donation", "out_of_scope"}:
        result["status"] = "declined"
    elif result["items"] and not result.get("location_text"):
        result["status"] = "needs_follow_up"
    else:
        result["status"] = "new"
    return result


def apply_code_rules(result: dict) -> dict:
    """Code-set rules: unsafe items, duplicates, per-item verification (only volunteer_medical), status."""
    if result.get("status") != "needs_review":
        result = drop_unsafe_items(result)
        result["items"] = merge_duplicate_items(result["items"])
    for item in result.get("items", []):
        item["needs_verification"] = item.get("what") == "volunteer_medical"
    return set_status(result)
