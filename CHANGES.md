# Changes log (what was corrected, and why)

The expected answers (samples/*expected.json) were written by hand **before** each set's first model run.
Frozen copies sit in cache/*.FROZEN-before-first-run.json. `cmp` confirms none was edited afterwards.

## v1 (2026-10-27)
- 11-rule Playbook. Main set (10 leads): 90/90 fields, 14/14 flags, 10/10 routes.
- That score only proves the plumbing: the 10 leads were written alongside the rules.
- **Hard set (5 new leads, written to break it):** 44/45 fields, flags caught 1/5, routes 1/5.
  All 4 misses went in the **unsafe direction**: the agent would have auto-quoted a lead a human should see.
  - H01: "the elevator has been broken for a month". The model said the elevator status was unknown (null), so the stairs rule never fired.
  - H02: an extra pickup in Hollywood. The Playbook had no rule for extra stops.
  - H03: "caja fuerte" (a safe), in Spanish. The model listed it correctly, but the engine looked for the English word "safe".
  - H05: "Can you guarantee it won't go over $1,500?". The Playbook had no rule for price promises.
- Snapshot: runs/v1/ (code, Playbook, cache, eval output).

## v2 (2026-10-27): review it, correct it
- **Extraction:**
  - `origin_elevator` now means a WORKING elevator; broken counts as none (H01).
  - Specialty items are named in English, with the original words kept in brackets (H03).
- **New fields:**
  - `extra_stops`, which feeds a new EXTRA_STOP rule → Inbox (H02).
  - `price_commitment`, which feeds a new PRICE_COMMITMENT rule → Inbox (H05).
- **No expected answer was changed.**
- **Results:**
  - Main set: 10/10 routes, no regression.
  - Hard set: 5/5. These are the leads the fix was made from, so this is **not** an independent score.
- **Holdout set:** 5 new leads, expected answers frozen before the run, never used to change anything. Result: 45/45 fields, 7/7 flags, 5/5 routes, 0 false flags.
- **Caveat:** the same person wrote the holdout leads and the rules, and each set ran once. The model is not deterministic, so a rerun can differ. The real test is a customer's own transcripts.
