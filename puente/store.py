"""SQLite access. For now: schema creation and LLM call logging (see AGENTS.md, Data model)."""

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
