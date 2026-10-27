#!/usr/bin/env python3
"""
Step 3 of 3: score the agent against hand-written answers.

    python3 eval.py        # main set
    python3 eval.py hard   # hard set
    python3 eval.py holdout

Reads samples/leads.json, samples/expected.json (written BEFORE the first
model run; frozen copy in cache/expected.FROZEN-before-first-run.json) and the
cached quote sheets from extract.py. Runs the Playbook engine and prints:
fields right, flags right / missed / false, route right, quotes found verbatim.
Writes results.json for report.py.
"""

import json
import sys
from pathlib import Path

import engine

HERE = Path(__file__).resolve().parent
NO_MEANS_FALSE = ("storage", "packing")


def field_ok(name, want, got):
    if name in ("origin_city", "destination_city"):
        if want is None:
            return not got
        return isinstance(got, str) and want in got.lower()
    if name == "specialty_items":
        got = got if isinstance(got, list) else []
        found = all(any(w in str(g).lower() for g in got) for w in want)
        return found and len(got) == len(want)
    if name in NO_MEANS_FALSE:
        return bool(got) == bool(want)
    return got == want


def main():
    prefix = next((a + "_" for a in sys.argv[1:] if a in ("hard", "holdout")), "")
    leads = json.loads((HERE / "samples" / f"{prefix}leads.json").read_text())
    expected = json.loads((HERE / "samples" / f"{prefix}expected.json").read_text())
    rows, totals = [], dict(fields=0, fields_ok=0, flags_want=0, flags_hit=0, flags_false=0,
                            route_ok=0, quotes=0, quotes_ok=0, extract_failed=0)
    for lead in leads:
        lid, text, want = lead["id"], lead["text"], expected[lead["id"]]
        record = json.loads((HERE / "cache" / f"{lid}.json").read_text())
        sheet = record.get("sheet")
        if not isinstance(sheet, dict):
            totals["extract_failed"] += 1
            totals["fields"] += len(want["fields"])
            totals["flags_want"] += len(want["flags"])
            rows.append({"id": lid, "extract_failed": True, "errors": record.get("errors")})
            continue
        result = engine.apply(sheet, text)
        wrong = {}
        for name, w in want["fields"].items():
            g = engine.val(sheet, name)
            totals["fields"] += 1
            if field_ok(name, w, g):
                totals["fields_ok"] += 1
            else:
                wrong[name] = {"want": w, "got": g}
        got_flags = {f["rule"] for f in result["flags"]}
        want_flags = set(want["flags"])
        missed, false = sorted(want_flags - got_flags), sorted(got_flags - want_flags)
        totals["flags_want"] += len(want_flags)
        totals["flags_hit"] += len(want_flags & got_flags)
        totals["flags_false"] += len(false)
        totals["route_ok"] += result["route"] == want["route"]
        qc = engine.quote_check(sheet, text)
        totals["quotes"] += len(qc)
        totals["quotes_ok"] += sum(qc.values())
        rows.append({
            "id": lid, "route": result["route"], "route_want": want["route"],
            "flags": result["flags"], "missed": missed, "false": false,
            "wrong_fields": wrong, "quotes_not_in_lead": [k for k, ok in qc.items() if not ok],
            "weight_lb": result["weight_lb"], "sheet": sheet,
        })

    print(f"{'lead':5} {'route (want)':26} {'fields':7} {'missed flags':28} {'false flags':22} bad quotes")
    for r in rows:
        if r.get("extract_failed"):
            print(f"{r['id']:5} EXTRACTION FAILED {r['errors']}")
            continue
        n = len(expected[r["id"]]["fields"])
        route = f"{r['route']} ({r['route_want']})" + ("" if r["route"] == r["route_want"] else " X")
        print(f"{r['id']:5} {route:26} {n - len(r['wrong_fields'])}/{n:<5} "
              f"{','.join(r['missed']) or '-':28} {','.join(r['false']) or '-':22} "
              f"{','.join(r['quotes_not_in_lead']) or '-'}")
        for name, d in r["wrong_fields"].items():
            print(f"      field {name}: want {d['want']!r}, got {d['got']!r}")
    t = totals
    print()
    print(f"fields correct : {t['fields_ok']}/{t['fields']}")
    print(f"flags caught   : {t['flags_hit']}/{t['flags_want']}  (missed {t['flags_want'] - t['flags_hit']})")
    print(f"false flags    : {t['flags_false']}")
    print(f"route correct  : {t['route_ok']}/{len(leads)}")
    print(f"quotes verbatim: {t['quotes_ok']}/{t['quotes']}")
    print(f"extract failed : {t['extract_failed']}")
    (HERE / f"{prefix}results.json").write_text(json.dumps({"totals": t, "rows": rows}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
