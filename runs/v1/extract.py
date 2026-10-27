#!/usr/bin/env python3
"""
Step 1 of 3: turn each messy lead into a structured quote sheet.

The model reads the lead and fills a fixed JSON shape. For every field it must
also copy the exact words from the lead that support it ("quote"). The engine
later checks those quotes really appear in the lead.

    python3 extract.py            # uses cache/ when present
    python3 extract.py hard       # the hard set (samples/hard_leads.json)
    python3 extract.py --refresh  # calls the model again for every lead

Model access: `claude -p` (Claude Code, headless). No API key is stored here.
Raw model output is cached in cache/<id>.raw.txt so the report can be rebuilt
without calling the model again.
"""

import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
TODAY = "2026-10-27"

FIELDS = {
    "origin_city": "string: city moving FROM, as written (neighbourhood + city is fine)",
    "destination_city": "string: city moving TO",
    "move_date": "string YYYY-MM-DD: the FINAL agreed move date. Range -> first day. "
                 "Resolve to the next future occurrence after today.",
    "date_changed": "boolean: true only if the customer changed the date during the lead",
    "home_type": "one of apartment|house|townhouse|condo|studio|office|unknown (origin home)",
    "bedrooms": "integer: bedrooms at the ORIGIN home; studio = 0; null for offices",
    "origin_floor": "integer: floor the origin home is on (ground floor = 1)",
    "origin_elevator": "boolean: true if the origin building has an elevator, false if it "
                       "clearly has none (e.g. 'walkup', 'no elevator')",
    "long_carry": "boolean: true if the truck cannot park close to the door",
    "areas_mentioned": "list of any of attic|garage|basement|shed that the lead mentions",
    "inventory": "list of strings: items as written",
    "bed_count": "integer: number of beds in the inventory (a bunk bed = 1)",
    "specialty_items": "list of strings: items needing special handling (piano, safe, "
                       "pool table, hot tub, server rack, antiques, fine art...)",
    "packing": "boolean: true if the customer asks the mover to pack for them",
    "storage": "boolean: true if storage is needed",
    "storage_duration": "string: how long storage is needed, as written",
    "language": "ISO 639-1 code of the lead's language",
    "is_commercial": "boolean: true for office / commercial moves",
}

PROMPT = """You extract moving-quote data from one customer lead. Today is {today}.

Return ONLY a JSON object, no prose, no code fences. It must have exactly these keys:
{keys}

Each key maps to an object: {{"value": <value or null>, "quote": <string or null>}}.

Rules:
- Use null for anything the lead does not state. Never guess. Never infer a floor from a suite number.
- Booleans that the lead never mentions are false, with quote null (e.g. storage, packing, long_carry).
  origin_elevator is null unless the lead says there is or is not one.
- "quote" must be copied character for character from the lead (same language, same spelling),
  the shortest span that supports the value. If value is null, quote is null.
- Lists: value is a list; quote is the span covering the items (or null if the list is empty).

Field meanings:
{meanings}

LEAD ({channel}):
<<<
{text}
>>>"""


def build_prompt(lead):
    return PROMPT.format(
        today=TODAY,
        keys=", ".join(FIELDS),
        meanings="\n".join(f"- {k}: {v}" for k, v in FIELDS.items()),
        channel=lead["channel"],
        text=lead["text"],
    )


def parse(raw):
    """Model text -> dict, or raise ValueError. Never trust the shape."""
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("no JSON object in output")
    data = json.loads(text[start:end + 1])
    if not isinstance(data, dict):
        raise ValueError(f"top level is {type(data).__name__}, not object")
    missing = [k for k in FIELDS if k not in data]
    if missing:
        raise ValueError(f"missing keys: {missing}")
    for k in FIELDS:
        cell = data[k]
        if not isinstance(cell, dict) or "value" not in cell:
            raise ValueError(f"{k} is not a {{value, quote}} object")
        if cell.get("quote") is not None and not isinstance(cell["quote"], str):
            raise ValueError(f"{k}.quote is not a string")
    return data


def call_model(prompt):
    # Run from an empty folder so no project files are loaded as context.
    with tempfile.TemporaryDirectory() as tmp:
        out = subprocess.run(
            ["claude", "-p", "--output-format", "text"],
            input=prompt, capture_output=True, text=True, cwd=tmp, timeout=240,
        )
    if out.returncode != 0:
        raise RuntimeError(f"claude exited {out.returncode}: {out.stderr.strip()[:300]}")
    return out.stdout


def extract(lead, refresh=False):
    lid = lead["id"]
    sheet_path = CACHE / f"{lid}.json"
    if sheet_path.exists() and not refresh:
        return json.loads(sheet_path.read_text())
    prompt = build_prompt(lead)
    attempts, errors = 0, []
    sheet = None
    for _ in range(2):  # first try + one retry on bad output
        attempts += 1
        try:
            raw = call_model(prompt)
            (CACHE / f"{lid}.raw.{attempts}.txt").write_text(raw)
            sheet = parse(raw)
            break
        except Exception as e:  # recorded, never hidden
            errors.append(f"attempt {attempts}: {type(e).__name__}: {e}")
    record = {"id": lid, "attempts": attempts, "errors": errors, "sheet": sheet}
    sheet_path.write_text(json.dumps(record, indent=2, ensure_ascii=False))
    return record


def main():
    refresh = "--refresh" in sys.argv
    prefix = "hard_" if "hard" in sys.argv[1:] else ""
    CACHE.mkdir(exist_ok=True)
    leads = json.loads((HERE / "samples" / f"{prefix}leads.json").read_text())
    if not prefix:
        (CACHE / "prompt-example.txt").write_text(build_prompt(leads[0]))
    with ThreadPoolExecutor(max_workers=5) as pool:
        records = list(pool.map(lambda l: extract(l, refresh), leads))
    for r in records:
        status = "ok" if r["sheet"] else "FAILED"
        print(f"{r['id']}: {status} after {r['attempts']} attempt(s) {r['errors'] or ''}")
    failed = sum(1 for r in records if not r["sheet"])
    print(f"{len(records) - failed}/{len(records)} leads extracted")


if __name__ == "__main__":
    main()
