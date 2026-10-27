#!/usr/bin/env python3
"""
Step 2 of 3: apply the Playbook (playbook.md) to a quote sheet.

No model here. Same sheet in, same flags out, every time. Each flag carries
the customer's exact words that triggered it, and says whether those words
were found in the lead (a guard against the model inventing a quote).
"""

SPECIALTY = ("piano", "safe", "pool table", "hot tub", "server rack", "antique", "fine art", "artwork")
HOUSES = ("house", "townhouse")
ACTIONS = {
    "NO_DATE": "ask", "DATE_CHANGED": "ask", "MISSING_ADDRESS": "ask",
    "SPECIALTY_ITEM": "inbox", "STAIRS_NO_ELEVATOR": "inbox", "LONG_CARRY": "inbox",
    "ATTIC_GARAGE_UNKNOWN": "ask", "INVENTORY_CONFLICT": "inbox",
    "STORAGE_NO_DURATION": "ask", "COMMERCIAL": "inbox", "LANGUAGE": "note",
    "EXTRA_STOP": "inbox", "PRICE_COMMITMENT": "inbox",  # added in v2, see CHANGES.md
}


def val(sheet, key):
    cell = sheet.get(key)
    return cell.get("value") if isinstance(cell, dict) else None


def quote(sheet, key):
    cell = sheet.get(key)
    q = cell.get("quote") if isinstance(cell, dict) else None
    return q if isinstance(q, str) else None


def specialty_hits(sheet):
    items = val(sheet, "specialty_items")
    if not isinstance(items, list):
        return []
    return [i for i in items if isinstance(i, str) and any(s in i.lower() for s in SPECIALTY)]


def apply(sheet, text):
    flags = []

    def flag(rule, reason, evidence):
        flags.append({
            "rule": rule,
            "action": ACTIONS[rule],
            "reason": reason,
            "evidence": evidence,
            # True only if the cited words really appear in the customer's message.
            "evidence_in_lead": bool(evidence) and evidence in text,
        })

    if not val(sheet, "move_date"):
        flag("NO_DATE", "No specific move date. Ask for one before quoting.",
             quote(sheet, "move_date") or None)
    if val(sheet, "date_changed") is True:
        flag("DATE_CHANGED", f"Date changed mid-conversation. Confirm {val(sheet, 'move_date')} in writing.",
             quote(sheet, "date_changed"))
    if not val(sheet, "origin_city") or not val(sheet, "destination_city"):
        missing = [k.split("_")[0] for k in ("origin_city", "destination_city") if not val(sheet, k)]
        flag("MISSING_ADDRESS", f"Missing {' and '.join(missing)}. Distance drives price.", None)
    hits = specialty_hits(sheet)
    if hits:
        flag("SPECIALTY_ITEM", f"Specialty item ({', '.join(hits)}): special crew/valuation, price changes.",
             quote(sheet, "specialty_items"))
    floor, elevator = val(sheet, "origin_floor"), val(sheet, "origin_elevator")
    if isinstance(floor, int) and floor >= 3 and elevator is False:
        flag("STAIRS_NO_ELEVATOR", f"Floor {floor} with no elevator: stair carry changes the price.",
             quote(sheet, "origin_elevator") or quote(sheet, "origin_floor"))
    if val(sheet, "long_carry") is True:
        flag("LONG_CARRY", "Truck can't park at the door: long carry changes the price.",
             quote(sheet, "long_carry"))
    areas = val(sheet, "areas_mentioned")
    if val(sheet, "home_type") in HOUSES and not val(sheet, "is_commercial") and not areas:
        flag("ATTIC_GARAGE_UNKNOWN", "House move, attic/garage/basement never mentioned. Ask before quoting.",
             quote(sheet, "home_type"))
    beds, rooms = val(sheet, "bed_count"), val(sheet, "bedrooms")
    if isinstance(beds, int) and isinstance(rooms, int) and beds > max(rooms, 1) + 1:
        flag("INVENTORY_CONFLICT", f"{beds} beds listed for a {rooms or 'studio'}"
             f"{'-bedroom' if rooms else ''} home: inventory or home size is wrong.",
             quote(sheet, "inventory"))
    if val(sheet, "storage") is True and not val(sheet, "storage_duration"):
        flag("STORAGE_NO_DURATION", "Storage needed, duration unknown. Billed by time; ask.",
             quote(sheet, "storage"))
    if val(sheet, "is_commercial") is True:
        flag("COMMERCIAL", "Commercial move: route to the commercial estimator (COI, building rules).",
             quote(sheet, "is_commercial"))
    stops = val(sheet, "extra_stops")
    if isinstance(stops, list) and stops:
        flag("EXTRA_STOP", f"Extra stop ({', '.join(map(str, stops))}): adds time and miles, price changes.",
             quote(sheet, "extra_stops"))
    if val(sheet, "price_commitment") is True:
        flag("PRICE_COMMITMENT", "Customer wants a guaranteed or maximum price: a human decides that.",
             quote(sheet, "price_commitment"))
    lang = val(sheet, "language")
    if isinstance(lang, str) and lang.lower() not in ("en", ""):
        flag("LANGUAGE", f"Lead is in '{lang}'. Reply in the customer's language.", None)

    actions = {f["action"] for f in flags}
    route = "inbox" if "inbox" in actions else "ask" if "ask" in actions else "auto_quote"
    return {"flags": flags, "route": route, "weight_lb": weight(rooms, val(sheet, "is_commercial"))}


def weight(rooms, commercial):
    """SAMPLE rule of thumb, not Supermove's estimator. None when it can't apply."""
    if commercial or not isinstance(rooms, int):
        return None
    rooms = max(rooms, 1)
    return [1000 + 1200 * rooms, 1000 + 1800 * rooms]


def quote_check(sheet, text):
    """Every non-null quote the model gave, and whether it appears in the lead verbatim."""
    out = {}
    for k, cell in sheet.items():
        q = cell.get("quote") if isinstance(cell, dict) else None
        if isinstance(q, str) and q:
            out[k] = q in text
    return out
