# Quote Playbook (SAMPLE)

One workflow: a new lead asks for a moving quote. These are the rules a mover's best estimator would follow,
written down so an agent can follow them too. This is a **sample** Playbook written for this demo. A real
customer's Playbook comes from sitting with their estimators.

**Three outcomes:**
- **auto-quote**: nothing in the lead changes the price beyond what the quote sheet already says. The agent sends the quote.
- **ask**: something is missing. The agent asks the customer one clear question before quoting.
- **Inbox (human)**: something could be a scope change that affects the move's price. The quote goes to a human, with the reason and the customer's own words attached.

If any rule says Inbox, the lead goes to the Inbox. Otherwise, if any rule says ask, the agent asks. Otherwise it auto-quotes.
Every flag must quote the exact words in the lead that triggered it.

| id | Trigger (in plain words) | Action | Why |
|---|---|---|---|
| NO_DATE | No specific move date | ask | Price and crew availability depend on the date. "Sometime next year" is not a date. |
| DATE_CHANGED | The customer changed the date during the conversation | ask | Confirm the final date in writing before booking, so the crew is scheduled for the right day. |
| MISSING_ADDRESS | Origin or destination city is missing | ask | Distance drives the price. |
| SPECIALTY_ITEM | Piano, safe, gun safe, pool table, hot tub, server rack, antique or fine art | Inbox | These need special crew, equipment or valuation. A scope change that affects the price. |
| STAIRS_NO_ELEVATOR | Origin is on the 3rd floor or higher with no working elevator (broken counts as none, v2) | Inbox | Stair carries add crew time; the price changes. (The "fifth-floor walkup" question.) |
| LONG_CARRY | The truck can't park close to the door | Inbox | A long carry adds crew time; the price changes. |
| ATTIC_GARAGE_UNKNOWN | Moving out of a house and the attic, garage, basement or shed is never mentioned | ask | The most common hidden volume. Ask before quoting, not on move day. |
| INVENTORY_CONFLICT | More beds listed than the home size can hold (beds > bedrooms + 1, a studio counts as 1) | Inbox | The inventory or the home size is wrong, so the quote would be wrong either way. |
| STORAGE_NO_DURATION | Storage is needed but for how long is unknown | ask | Storage is billed by time; delivery needs a second date. |
| COMMERCIAL | Office or commercial move | Inbox | Different estimator, certificate of insurance, building rules, after-hours work. |
| EXTRA_STOP | A pickup or drop-off besides origin and destination (added v2) | Inbox | Extra miles and time; the price changes. |
| PRICE_COMMITMENT | Customer asks for a guaranteed, fixed or not-to-exceed price (added v2) | Inbox | A price promise is a business decision, not the agent's. |
| LANGUAGE | The lead is not in English | note (doesn't block) | Answer in the customer's language. |

Weight estimate on the quote sheet uses a **sample rule of thumb** (1,000 lb base + 1,200 to 1,800 lb per bedroom).
It is a placeholder, not Supermove's estimator, which calculates weight from rooms and items.
