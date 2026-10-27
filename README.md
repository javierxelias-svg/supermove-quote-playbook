# Quote Playbook + Inbox (SAMPLE demo for Supermove, FDE AI)

**What it is:** a messy moving lead goes in (text, email, call transcript, WhatsApp in Puerto Rican Spanish). A quote sheet comes out. A written Playbook then decides:
- **auto-quote**,
- **ask the customer** one question, or
- **Inbox**: a human approves, with the reason and the customer's exact words attached.

**Why:** Supermove says quotes went from 45 minutes to 1 minute, and that "a scope change that affects the price of a move" goes to a human. This is the step in between: which quotes are safe to send, plus a score that proves it.

**Results** (20 invented leads, each set run once):

| Version | Set | Result |
|---|---|---|
| v1 | main 10 | 10/10 routes |
| v1 | hard 5 | **1/5 routes**: 4 misses, all unsafe (it auto-quoted leads a human should see) |
| v2 | main 10 | 10/10 routes (no regression) |
| v2 | hard 5 | 5/5 (fixed from these leads, so not independent) |
| v2 | holdout 5 | **5/5**: answers frozen before the run, never used for tuning |

What changed between v1 and v2 is in CHANGES.md.

**Run it** (Python standard library only; the model is called through `claude -p`):
```
python3 extract.py && python3 extract.py hard && python3 extract.py holdout   # cached; --refresh to re-call
python3 eval.py && python3 eval.py hard && python3 eval.py holdout
python3 report.py   # -> report.html
```

**Files:**
- samples/ holds the leads and the hand-written answers.
- playbook.md holds the rules.
- extract.py, engine.py and eval.py are the 3 steps.
- runs/v1 is the snapshot from before the fix.
- RECEIPT.md has the raw output.

**All data is SAMPLE.** Nothing touches a real customer or Supermove's product.
