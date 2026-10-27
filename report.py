#!/usr/bin/env python3
"""
Build report.html from the eval results. Zero JavaScript, one file.

    python3 report.py   (run eval.py, eval.py hard, eval.py holdout first)
"""

import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHOWCASE = [("results.json", "L01"), ("results.json", "L06"), ("results.json", "L05")]
FIELDS_SHOWN = ["origin_city", "destination_city", "move_date", "home_type", "bedrooms",
                "origin_floor", "origin_elevator", "long_carry", "inventory", "specialty_items",
                "extra_stops", "packing", "storage", "language"]
ROUTE_LABEL = {"inbox": "Inbox: a human approves", "ask": "Ask the customer first",
               "auto_quote": "Auto-quote"}

e = html.escape


def load(name, base=HERE):
    return json.loads((base / name).read_text())


def leads_by_id():
    out = {}
    for f in ("leads.json", "hard_leads.json", "holdout_leads.json"):
        for lead in load(f, HERE / "samples"):
            out[lead["id"]] = lead
    return out


def marked(text, quotes):
    """Escape the lead and wrap each cited phrase in <mark>."""
    out = e(text)
    for q in sorted({q for q in quotes if q}, key=len, reverse=True):
        eq = e(q)
        if eq in out:
            out = out.replace(eq, f"<mark>{eq}</mark>", 1)
    return out.replace("\n", "<br>")


def fmt(v):
    if v is None:
        return '<span class="muted">not stated</span>'
    if isinstance(v, list):
        return e(", ".join(map(str, v))) if v else '<span class="muted">none</span>'
    if isinstance(v, bool):
        return "yes" if v else "no"
    return e(str(v))


def showcase(row, lead):
    sheet = row["sheet"]
    quotes = [f["evidence"] for f in row["flags"]]
    rows = "".join(
        f"<tr><th>{e(k.replace('_', ' '))}</th><td>{fmt(sheet[k]['value'])}</td></tr>"
        for k in FIELDS_SHOWN if k in sheet)
    if row["weight_lb"]:
        lo, hi = row["weight_lb"]
        rows += f"<tr><th>est. weight</th><td>{lo:,}–{hi:,} lb <span class='muted'>(sample rule of thumb)</span></td></tr>"
    flags = "".join(
        f"<li><b>{e(f['rule'])}</b> → {e(f['action'])}. {e(f['reason'])}"
        + (f"<br><span class='cite'>Customer's words: “{e(f['evidence'])}”"
           f"{' ✓ found in message' if f['evidence_in_lead'] else ' ✗ NOT found in message'}</span>"
           if f["evidence"] else "")
        + "</li>" for f in row["flags"]) or "<li>No flags.</li>"
    return f"""
<article class="case">
  <h3>{e(lead['id'])} · {e(lead['channel'])} <span class="tag">{e(lead['label'])}</span></h3>
  <div class="grid">
    <div><h4>1 · Messy input</h4><p class="lead">{marked(lead['text'], quotes)}</p></div>
    <div><h4>2 · Quote sheet</h4><table class="sheet">{rows}</table></div>
    <div><h4>3 · Playbook decision</h4>
      <p class="route route-{e(row['route'])}">{e(ROUTE_LABEL[row['route']])}</p>
      <ul class="flags">{flags}</ul></div>
  </div>
</article>"""


def score_row(name, t, n, note):
    return (f"<tr><td>{e(name)}</td><td>{t['fields_ok']}/{t['fields']}</td>"
            f"<td>{t['flags_hit']}/{t['flags_want']}</td><td>{t['flags_false']}</td>"
            f"<td>{t['route_ok']}/{n}</td><td>{t['quotes_ok']}/{t['quotes']}</td><td>{note}</td></tr>")


def main():
    leads = leads_by_id()
    main_r, hard_r, hold_r = load("results.json"), load("hard_results.json"), load("holdout_results.json")
    v1_main, v1_hard = load("runs/v1/results.json"), load("runs/v1/hard_results.json")
    by_id = {r["id"]: r for r in main_r["rows"]}
    cases = "".join(showcase(by_id[i], leads[i]) for _, i in SHOWCASE)
    scores = "".join([
        score_row("v1 · main (10)", v1_main["totals"], 10, "written with the rules; proves the plumbing"),
        score_row("v1 · hard (5)", v1_hard["totals"], 5, "<b>written to break it</b>"),
        score_row("v2 · main (10)", main_r["totals"], 10, "no regression"),
        score_row("v2 · hard (5)", hard_r["totals"], 5, "after the fix: <b>not</b> independent"),
        score_row("v2 · holdout (5)", hold_r["totals"], 5, "frozen answers, never used to tune"),
    ])
    misses = []
    for r in v1_hard["rows"]:
        if r.get("missed"):
            lead = leads[r["id"]]
            wrong = "; ".join(f"{k}: wanted {d['want']!r}, got {d['got']!r}" for k, d in r["wrong_fields"].items())
            misses.append(
                f"<li><b>{e(r['id'])}</b>: “{e(lead['text'][:150])}{'…' if len(lead['text']) > 150 else ''}”"
                f"<br>Missed <b>{e(', '.join(r['missed']))}</b>. Routed <b>{e(r['route'])}</b>, should be "
                f"<b>{e(r['route_want'])}</b>.{(' ' + e(wrong)) if wrong else ''}</li>")
    playbook_rows = []
    for line in (HERE / "playbook.md").read_text().splitlines():
        if line.startswith("| ") and not line.startswith("| id") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            playbook_rows.append("<tr>" + "".join(f"<td>{e(c)}</td>" for c in cells) + "</tr>")

    page = TEMPLATE.format(cases=cases, scores=scores, misses="".join(misses),
                           playbook="".join(playbook_rows))
    (HERE / "report.html").write_text(page)
    print(f"report.html written, {len(page):,} bytes")


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quote Playbook + Inbox</title>
<meta name="description" content="A sample moving-quote agent: messy lead in, quote sheet out, a written Playbook decides what a human must see, with an eval that shows its failures.">
<style>
:root {{ --bg:#fbfaf7; --fg:#1d1d1b; --muted:#6b6a65; --line:#e3e0d8; --card:#ffffff;
  --mark:#fff0a8; --inbox:#9a3412; --ask:#1d4ed8; --auto:#166534; --accent:#7c2d12; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#141413; --fg:#ecebe6; --muted:#a3a29b; --line:#2e2d2a; --card:#1c1c1a;
  --mark:#5c4a00; --inbox:#fdba74; --ask:#93c5fd; --auto:#86efac; --accent:#fdba74; }} }}
:root[data-theme="dark"] {{ --bg:#141413; --fg:#ecebe6; --muted:#a3a29b; --line:#2e2d2a; --card:#1c1c1a;
  --mark:#5c4a00; --inbox:#fdba74; --ask:#93c5fd; --auto:#86efac; --accent:#fdba74; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg);
  font:16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; }}
main {{ max-width:1080px; margin:0 auto; padding:32px 16px 64px; }}
h1 {{ font-size:clamp(1.7rem,4vw,2.4rem); line-height:1.15; margin:0 0 8px; }}
h2 {{ margin:48px 0 12px; font-size:1.35rem; }}
h3 {{ margin:0 0 12px; font-size:1.05rem; }}
h4 {{ margin:0 0 6px; font-size:.8rem; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); }}
p {{ margin:0 0 12px; }}
a {{ color:var(--accent); }}
.muted, .cite {{ color:var(--muted); }}
.cite {{ font-size:.88rem; }}
.sample {{ border:1px solid var(--line); background:var(--card); padding:10px 14px; border-radius:8px; font-size:.92rem; }}
blockquote {{ margin:0 0 12px; padding:2px 0 2px 14px; border-left:3px solid var(--line); }}
.case {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px; margin:16px 0; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; }}
.lead {{ font-family:ui-monospace, SFMono-Regular, Menlo, monospace; font-size:.85rem; overflow-wrap:anywhere; }}
mark {{ background:var(--mark); color:inherit; padding:0 2px; }}
table {{ border-collapse:collapse; width:100%; font-size:.9rem; }}
th, td {{ text-align:left; padding:5px 8px; border-bottom:1px solid var(--line); vertical-align:top; overflow-wrap:anywhere; }}
.sheet th {{ color:var(--muted); font-weight:500; width:40%; }}
.scroll {{ overflow-x:auto; }}
.scroll table {{ min-width:640px; }}
.route {{ font-weight:700; }}
.route-inbox {{ color:var(--inbox); }} .route-ask {{ color:var(--ask); }} .route-auto_quote {{ color:var(--auto); }}
.flags {{ padding-left:18px; margin:0; }} .flags li {{ margin-bottom:8px; }}
.tag {{ font-size:.75rem; font-weight:500; color:var(--muted); }}
footer {{ margin-top:56px; padding-top:16px; border-top:1px solid var(--line); font-size:.9rem; color:var(--muted); }}
</style></head>
<body><main>

<h1>Quote Playbook + Inbox</h1>
<p>A messy lead goes in, and a quote sheet comes out. A written Playbook then decides one of three things: send the quote, ask the customer one question, or put it in a human's Inbox with the reason and the customer's own words attached. An eval scores the whole thing, and the failures are shown.</p>
<p class="sample"><b>All data on this page is SAMPLE.</b> Every lead was invented for this demo. Nothing here touches a real customer or Supermove's product. The Playbook is a sample written for this demo, not Supermove's.</p>

<h2>The problem, in Supermove's words</h2>
<p class="muted">Quoted word for word from Supermove's public blog, checked against each page on Oct 27, 2026.</p>
<blockquote>“45-minute quote turnarounds compressed to 1 minute, 24/7.” <span class="cite">: <a href="https://www.supermove.com/blog/the-future-of-ai-for-moving-companies">The Future of AI for Moving Companies</a></span></blockquote>
<blockquote>When an Agent hits “a scope change that affects the price of a move, it doesn't guess. It routes the decision to the right person with everything they need already attached.” <span class="cite">: <a href="https://www.supermove.com/blog/introducing-autopilot-the-moving-industrys-first-autonomous-ai">Introducing Autopilot</a></span></blockquote>
<blockquote>“Pick one workflow. Capture how your best people really handle it.” “Run it. Review it. Correct it.” “The more AI can do, the more trust matters.” <span class="cite">: <a href="https://www.supermove.com/blog/2030-came-early-the-7-big-takeaways-from-f50-2026">7 takeaways from F50 2026</a></span></blockquote>
<blockquote>A company “turned a $1,800 quote into a $3,400 invoice.” <span class="cite">: <a href="https://www.supermove.com/blog/why-accurate-estimates-are-crucial-for-a-moving-companys-reputation">Why Accurate Estimates Are Crucial</a></span></blockquote>
<p>This demo is the step in between: <b>which quotes are safe to send, which aren't, and a score that proves it.</b></p>

<h2>Three leads, start to finish</h2>
<p class="muted">Highlighted words are the exact phrases that triggered a rule. The engine checks that every cited phrase really appears in the message.</p>
{cases}

<h2>The score, failures included</h2>
<div class="scroll"><table>
<tr><th>Run</th><th>Fields right</th><th>Flags caught</th><th>False flags</th><th>Route right</th><th>Quotes found verbatim</th><th>What it means</th></tr>
{scores}
</table></div>
<p><b>What v1 got wrong.</b> All four misses went the dangerous way: the agent would have auto-quoted a lead a human should see.</p>
<ul>{misses}</ul>
<p><b>Review it, correct it (v2).</b> Two prompt fixes and two new rules:</p>
<ul>
  <li>Broken elevator now counts as none.</li>
  <li>Specialty items are named in English, so “caja fuerte” is read as a safe.</li>
  <li>New rule: extra stops go to a human.</li>
  <li>New rule: price promises go to a human.</li>
</ul>
<p>No expected answer was changed; each was written before its set first ran. Then 5 holdout leads, never used for tuning, scored 5/5.</p>
<p class="muted"><b>Honest limits:</b> the leads, the rules and the test answers came from the same build session. Each set ran once, and the model can vary between runs. Twenty invented leads are a signal, not proof. Real transcripts are the real test.</p>

<h2>The Playbook (v2)</h2>
<div class="scroll"><table>
<tr><th>Rule</th><th>Trigger</th><th>Action</th><th>Why</th></tr>
{playbook}
</table></div>

<h2>How it works</h2>
<ol>
  <li><b>Extract.</b> A model fills a fixed quote sheet and copies the exact words behind every field. Bad output is retried once. Failures are recorded, never hidden.</li>
  <li><b>Decide.</b> Plain code, no model, applies the Playbook. Same sheet in, same decision out. Every flag cites the customer's words.</li>
  <li><b>Score.</b> The output is compared with hand-written answers: fields, flags caught, flags missed, false flags, and the route.</li>
</ol>

<h2>Week one on a real customer</h2>
<ol>
  <li>Sit with their best estimator for a day and write their real Playbook. Their rules, their thresholds, their words.</li>
  <li>Pull 50 real leads and call transcripts. The estimator marks what they would have done with each. That becomes the eval set.</li>
  <li>Run it, read every miss, fix the prompt or add a rule, and run again. Report the numbers, including the misses.</li>
  <li>Start in shadow mode: the agent decides, a human still sends. It goes live rule by rule, only where the score earns it.</li>
</ol>

<footer>
  Built by Javier Elías Crespo directing Claude Code. Claude Code wrote the code, the sample leads, the rules and the test answers.
  Javier chose the problem and the approach and decided to publish it.
  Python standard library only. Model calls through Claude Code headless.
</footer>
</main></body></html>
"""


if __name__ == "__main__":
    main()
