"""Project-wide constants for Puente (see AGENTS.md)."""

from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "prompts"
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "puente.db"

# Demo clock: all time logic uses this, never the real clock.
DEMO_NOW = datetime.fromisoformat("2026-12-04T10:00")

TOWN = "Valencia"
KNOWN_TOWNS = [
    "Valencia", "Paiporta", "Catarroja", "Massanassa", "Alfafar", "Sedaví",
    "Benetússer", "Picanya", "Aldaia", "Chiva", "Utiel",
]

MATCH_RADIUS_KM = 10.0
MAX_CANDIDATES = 10
MIN_CONFIDENCE = 0.5
DUPLICATE_WINDOW_HOURS = 2
DONATION_URL = "https://example.org/donate"  # placeholder, replace with the official channel

# Models
EXTRACTOR_MODEL = "claude-haiku-5-5"
MATCHER_MODEL = "claude-haiku-5-5"
JUDGE_MODEL = "claude-sonnet-5-5"
LLM_EFFORT = "low"

# Allowed values (extractor schema)
ITEM_TYPES = ["need", "offer"]
CATEGORIES = ["transport", "shelter", "supplies", "volunteers"]
CANONICAL_ITEMS = [
    "water", "food", "blankets", "clothes", "baby_supplies", "shovels",
    "cleaning_supplies", "generator", "van", "car", "bed", "storage",
    "volunteer_general", "volunteer_medical", "volunteer_electrician", "other",
]
URGENCIES = ["red", "orange", "green"]
MODEL_FLAGS = ["injection", "scam", "money", "unsafe_donation", "out_of_scope"]
CODE_FLAGS = ["duplicate_suspect", "surplus"]
