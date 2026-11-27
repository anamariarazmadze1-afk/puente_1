"""SQLite access: schema, saving extractions, the needs board and LLM call logging (AGENTS.md, Data model)."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from puente.config import DB_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY, sender_name TEXT, sender_phone TEXT, timestamp TEXT, text TEXT,
    language TEXT, location_text TEXT, lat REAL, lon REAL, urgency TEXT, urgency_reason TEXT,
    flags TEXT, follow_up_question TEXT, confidence REAL, status TEXT
);
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT, message_id TEXT, type TEXT, category TEXT, what TEXT,
    quantity REAL, unit TEXT, conditions TEXT, can_deliver INTEGER, available_from TEXT,
    available_until TEXT, capacity_total REAL, capacity_used REAL DEFAULT 0,
    needs_verification INTEGER, verified INTEGER DEFAULT 0, status TEXT
);
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT, need_item_id INTEGER, offer_item_id INTEGER,
    quantity REAL, reason TEXT, status TEXT, created_at TEXT, approved_at TEXT
);
CREATE TABLE IF NOT EXISTS llm_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT, message_id TEXT, step TEXT, model TEXT,
    input_tokens INTEGER, output_tokens INTEGER, timestamp TEXT
);
"""


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Open the database and make sure all tables exist."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    """Create all tables if they do not exist."""
    connect(db_path).close()


def save_extraction(
    conn: sqlite3.Connection,
    extraction: dict,
    text: str,
    sender_name: str | None = None,
    sender_phone: str | None = None,
    timestamp: str | None = None,
) -> None:
    """Store one extracted message and its items. Replaces the message if its id already exists.

    `extraction` is the dict returned by `extractor.extract()`. Each item gets
    `capacity_total = quantity` (1 if missing) and `status = "active"`.
    Location and availability belong to the message and are copied to every item.
    lat/lon stay empty until geocoding is added.
    """
    message_id = extraction["message_id"]
    with conn:
        conn.execute("DELETE FROM items WHERE message_id = ?", (message_id,))
        conn.execute(
            "INSERT OR REPLACE INTO messages (id, sender_name, sender_phone, timestamp, text, language,"
            " location_text, urgency, urgency_reason, flags, follow_up_question, confidence, status)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (message_id, sender_name, sender_phone, timestamp, text, extraction.get("language"),
             extraction.get("location_text"), extraction["urgency"], extraction.get("urgency_reason"),
             json.dumps(extraction.get("flags", [])), extraction.get("follow_up_question"),
             extraction.get("confidence"), extraction["status"]),
        )
        for item in extraction.get("items", []):
            quantity = item.get("quantity")
            conn.execute(
                "INSERT INTO items (message_id, type, category, what, quantity, unit, conditions,"
                " can_deliver, available_from, available_until, capacity_total, capacity_used,"
                " needs_verification, verified, status)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, 0, 'active')",
                (message_id, item["type"], item["category"], item["what"], quantity, item.get("unit"),
                 item.get("conditions"), item.get("can_deliver"), extraction.get("available_from"),
                 extraction.get("available_until"), quantity if quantity is not None else 1,
                 int(bool(item.get("needs_verification")))),
            )


def needs_board(conn: sqlite3.Connection) -> dict[str, dict]:
    """Compare open needs with remaining offers per `what` (AGENTS.md, Quantities and the needs board).

    Returns {what: {"open_need": float, "offer_left": float, "level": "Needed" | "OK" | "Enough"}}.
    Counts only items that are still open (status active or partly_covered) from messages that are
    not declined or under review. Offers from red messages are left out (they are never matched).
    """
    rows = conn.execute(
        """
        SELECT i.what, i.type, i.capacity_total, i.capacity_used, m.urgency,
               COALESCE((SELECT SUM(x.quantity) FROM matches x
                         WHERE x.need_item_id = i.id AND x.status = 'approved'), 0) AS covered
        FROM items i JOIN messages m ON m.id = i.message_id
        WHERE i.status IN ('active', 'partly_covered')
          AND m.status NOT IN ('declined', 'needs_review')
        """
    ).fetchall()
    totals: dict[str, dict] = {}
    for row in rows:
        entry = totals.setdefault(row["what"], {"open_need": 0.0, "offer_left": 0.0})
        if row["type"] == "need":
            entry["open_need"] += max(row["capacity_total"] - row["covered"], 0)
        elif row["urgency"] != "red":
            entry["offer_left"] += max(row["capacity_total"] - row["capacity_used"], 0)
    for entry in totals.values():
        need, offer = entry["open_need"], entry["offer_left"]
        if offer < need:
            entry["level"] = "Needed"
        elif offer > 2 * need:  # includes offers with no open needs at all
            entry["level"] = "Enough"
        else:
            entry["level"] = "OK"
    return totals


def log_llm_call(
    message_id: str | None,
    step: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    db_path: Path = DB_PATH,
) -> None:
    """Record one LLM call. Timestamp is wall-clock time of the call (for cost, not demo logic)."""
    conn = connect(db_path)
    try:
        with conn:  # commits on success
            conn.execute(
                "INSERT INTO llm_calls (message_id, step, model, input_tokens, output_tokens, timestamp)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (message_id, step, model, input_tokens, output_tokens,
                 datetime.now().isoformat(timespec="seconds")),
            )
    finally:
        conn.close()
