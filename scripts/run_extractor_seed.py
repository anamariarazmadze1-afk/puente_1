"""Run the extractor on every seed message and save the results as a numbered run.

Usage:  python scripts/run_extractor_seed.py --run 1
Writes eval/results/extractor_run<N>.json (full output) and .md (summary table).
"""

import argparse
import csv
import json
import sqlite3
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from puente.config import DATA_DIR, DB_PATH, EXTRACTOR_MODEL  # noqa: E402
from puente.extractor import extract  # noqa: E402

RESULTS_DIR = ROOT / "eval" / "results"
HAIKU_PRICE_IN, HAIKU_PRICE_OUT = 0.10, 0.50  # USD per 1M tokens (claude-haiku-5-5, <=100K prompt)


def load_seeds() -> list[dict]:
    with open(DATA_DIR / "seed_messages.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def items_summary(items: list[dict]) -> str:
    if not items:
        return "-"
    parts = []
    for it in items:
        qty = "" if it["quantity"] is None else f"×{it['quantity']:g}"
        parts.append(f"{it['type']} {it['what']}{qty}")
    return "; ".join(parts)


def token_totals(since: str) -> tuple[int, int, int]:
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(input_tokens),0), COALESCE(SUM(output_tokens),0)"
            " FROM llm_calls WHERE step='extract' AND timestamp >= ?", (since,)
        ).fetchone()
    finally:
        conn.close()
    return row


def md_cell(text: str) -> str:
    return str(text).replace("|", "/").replace("\n", " ")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=int, required=True, help="run number, e.g. 1 for the baseline")
    args = parser.parse_args()

    seeds = load_seeds()
    started = datetime.now().isoformat(timespec="seconds")
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(lambda s: extract(s["text"], s["id"]), seeds))
    calls, tok_in, tok_out = token_totals(started)
    cost = tok_in / 1e6 * HAIKU_PRICE_IN + tok_out / 1e6 * HAIKU_PRICE_OUT

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_json = RESULTS_DIR / f"extractor_run{args.run}.json"
    out_json.write_text(json.dumps({
        "run": args.run, "started": started, "model": EXTRACTOR_MODEL,
        "llm_calls": calls, "input_tokens": tok_in, "output_tokens": tok_out, "cost_usd": round(cost, 5),
        "results": [{"seed": s, "extraction": r} for s, r in zip(seeds, results)],
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# Extractor run {args.run}",
        "",
        f"Started {started}, model `{EXTRACTOR_MODEL}`, {calls} LLM calls, "
        f"{tok_in} input / {tok_out} output tokens, about ${cost:.4f}.",
        "",
        "| id | text | urgency | items | flags | follow-up | status |",
        "|---|---|---|---|---|---|---|",
    ]
    for s, r in zip(seeds, results):
        urgency = r["urgency"] + (" (keyword)" if r.get("urgency_source") == "keyword" else "")
        lines.append("| " + " | ".join(md_cell(x) for x in [
            s["id"], s["text"][:45] + ("…" if len(s["text"]) > 45 else ""), urgency,
            items_summary(r["items"]), ", ".join(r["flags"]) or "-",
            r["follow_up_question"] or "-", r["status"],
        ]) + " |")
    out_md = RESULTS_DIR / f"extractor_run{args.run}.md"
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"\nSaved {out_json.relative_to(ROOT)} and {out_md.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
