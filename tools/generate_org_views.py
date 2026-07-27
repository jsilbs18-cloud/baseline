#!/usr/bin/env python3
"""Generate org views from 02-organization/org-data/*.yaml.

Reads seats.yaml, candidates.yaml, and sources.yaml, validates them, and writes:

    02-organization/generated/dashboard.html      the ED-facing status page
    02-organization/generated/org-chart.md        org chart (Mermaid, for GitHub)
    02-organization/generated/hiring-dashboard.md text dashboard (for GitHub)

dashboard.html is the deliverable: one self-contained file, four tabs
(Org Chart / Candidate Pipeline / Sourcing / Open Seats), no external
dependencies — send the file itself.

Generated files are never edited by hand: fix the data, re-run this script.

Usage:  python3 tools/generate_org_views.py
"""

import html
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "02-organization" / "org-data"
OUT = ROOT / "02-organization" / "generated"

SEAT_STATUSES = [
    "defined", "approved", "sourcing", "interviewing", "selected",
    "clearance-ethics", "filled", "hold",
]
CANDIDATE_STAGES = [
    "to-meet", "waiting", "screening", "cleared", "stalled",
    "joined", "passed", "withdrawn",
]
ACTIVE_STAGES = ["to-meet", "waiting", "screening", "cleared"]
HIRING_AUTHORITIES = ["detailee", "ipa", "sge", "secondee", "excepted", "direct-hire",
                      "schedule-c", "tbd"]
SOURCE_TYPES = ["private", "government", "person", "group"]
SOURCE_STATUSES = ["to-call", "called-waiting", "produced", "dry"]

STATUS_LABELS = {
    "defined": "Not started", "approved": "Approved", "sourcing": "Sourcing",
    "interviewing": "In talks", "selected": "Selected",
    "clearance-ethics": "In screening", "filled": "On board", "hold": "On hold",
}
STAGE_LABELS = {
    "to-meet": "To meet", "waiting": "Waiting to hear",
    "screening": "In screening", "cleared": "Cleared to start",
    "stalled": "Stalled",
}
SOURCE_TYPE_LABELS = {"private": "Private", "government": "Gov", "person": "Person", "group": "Group"}
SOURCE_COLUMNS = [
    ("to-call", "Need to call"), ("called-waiting", "Called — waiting"),
    ("produced", "Produced"), ("dry", "Dry"),
]
# CSS var per stage/status dot (see the stylesheet below)
STAGE_DOT = {
    "to-meet": "--stage-1", "waiting": "--stage-3", "screening": "--stage-4",
    "cleared": "--good",
    "sourcing": "--stage-1", "interviewing": "--stage-3", "selected": "--stage-4",
    "clearance-ethics": "--stage-5", "filled": "--good", "produced": "--good",
}
BRANCH_ORDER = ["investment", "legal", "research", "front-office", "advisors", "chips"]
BRANCH_LABELS = {
    "investment": "Investment",
    "legal": "Legal",
    "research": "Research",
    "front-office": "Admin / Front Office",
    "advisors": "Senior Advisors",
    "chips": "CHIPS",
}
# Mermaid chart colors (markdown view)
MERMAID_STYLES = {
    "defined": ("#ececec", "#9e9e9e"),
    "approved": ("#e3ecf7", "#5b84b1"),
    "sourcing": ("#d6e6f7", "#2f6db3"),
    "interviewing": ("#fdf0d2", "#c99a2c"),
    "selected": ("#fde3c8", "#d97b29"),
    "clearance-ethics": ("#eadff2", "#7d5ba6"),
    "filled": ("#d8efd8", "#2e7d32"),
    "hold": ("#f2d9d9", "#a94442"),
}

warnings = []


def warn(msg):
    warnings.append(msg)
    print(f"WARNING: {msg}", file=sys.stderr)


# --------------------------------------------------------------------------- #
# Loading & validation
# --------------------------------------------------------------------------- #

def load():
    seats = yaml.safe_load((DATA / "seats.yaml").read_text())["seats"]
    candidates = yaml.safe_load((DATA / "candidates.yaml").read_text())["candidates"] or []
    sources = yaml.safe_load((DATA / "sources.yaml").read_text())["sources"] or []
    return seats, candidates, sources


def validate(seats, candidates, sources):
    seat_ids = {s["id"] for s in seats}
    cand_ids = {c["id"] for c in candidates}
    source_ids = {s["id"] for s in sources}
    for s in seats:
        if s.get("status") not in SEAT_STATUSES:
            warn(f"seat {s['id']}: unknown status {s.get('status')!r}")
        if s.get("hiring_authority") not in HIRING_AUTHORITIES:
            warn(f"seat {s['id']}: unknown hiring_authority {s.get('hiring_authority')!r}")
        parent = s.get("reports_to")
        if parent not in seat_ids and parent != "secretary":
            warn(f"seat {s['id']}: reports_to {parent!r} is not a known seat")
    for c in candidates:
        if c.get("stage") not in CANDIDATE_STAGES:
            warn(f"candidate {c['id']}: unknown stage {c.get('stage')!r}")
        for t in c.get("target_seats", []):
            if t not in seat_ids:
                warn(f"candidate {c['id']}: target seat {t!r} is not a known seat")
        if c.get("via") and c["via"] not in source_ids:
            warn(f"candidate {c['id']}: via {c['via']!r} is not a known source")
        if c.get("stage") in ACTIVE_STAGES and not c.get("owner"):
            warn(f"candidate {c['id']}: active but has no owner")
    for s in sources:
        if s.get("type") not in SOURCE_TYPES:
            warn(f"source {s['id']}: unknown type {s.get('type')!r}")
        if s.get("status") not in SOURCE_STATUSES:
            warn(f"source {s['id']}: unknown status {s.get('status')!r}")
        if s.get("ball_in_court") not in ("them", "us", None):
            warn(f"source {s['id']}: ball_in_court must be them/us/empty")
        for p in s.get("produced", []) or []:
            if p not in cand_ids:
                warn(f"source {s['id']}: produced {p!r} is not a known candidate")
        if s.get("status") == "produced" and not s.get("produced"):
            warn(f"source {s['id']}: status is produced but `produced:` list is empty")


# --------------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------------- #

def incumbents_of(seat):
    v = seat.get("incumbent")
    if not v:
        return []
    return v if isinstance(v, list) else [v]


def filled_positions(seat):
    n = len(incumbents_of(seat))
    if n:
        return min(n, seat.get("headcount", 1))
    return seat.get("headcount", 1) if seat["status"] == "filled" else 0


def in_play(candidates, seat_id):
    return [c for c in candidates
            if seat_id in c.get("target_seats", []) and c.get("stage") in ACTIVE_STAGES]


def fmt_date(d, style="iso"):
    dd = as_date(d)
    if dd is None:
        return str(d) if d else ""
    if style == "short":
        return dd.strftime("%b %d").upper()
    return dd.isoformat()


def as_date(d):
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    try:
        return date.fromisoformat(str(d))
    except (TypeError, ValueError):
        return None


def fmt_yesno(v):
    if v is True:
        return "yes"
    if v is False:
        return "no"
    return str(v) if v is not None else ""


def latest_log(rec):
    log = rec.get("log") or []
    if not log:
        return None, 0
    entries = sorted(log, key=lambda e: as_date(e.get("date")) or date.min, reverse=True)
    return entries[0], len(entries) - 1


def has_example_records(*record_lists):
    return any(str(r.get("id", "")).startswith("example-")
               for records in record_lists for r in records)


def node_id(seat_id):
    """Mermaid-safe node id (hyphens can break flowchart parsing)."""
    return seat_id.replace("-", "_")


def esc(v):
    return html.escape(str(v)) if v is not None else ""


# --------------------------------------------------------------------------- #
# HTML dashboard
# --------------------------------------------------------------------------- #

CSS = """
  :root {
    color-scheme: light;
    --page: #f9f9f7; --surface: #fcfcfb;
    --ink: #0b0b0b; --ink-2: #52514e; --muted: #898781;
    --hairline: rgba(11,11,11,0.10); --grid: #e1e0d9;
    --good: #0ca30c; --good-text: #006300; --warn: #fab219;
    --stage-1: #86b6ef; --stage-2: #5598e7; --stage-3: #2a78d6;
    --stage-4: #1c5cab; --stage-5: #104281;
    --open-fill: #f0efec;
    --card-shadow: 0 1px 2px rgba(11,11,11,0.06), 0 2px 8px rgba(11,11,11,0.05);
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      color-scheme: dark;
      --page: #0d0d0d; --surface: #1a1a19;
      --ink: #ffffff; --ink-2: #c3c2b7; --muted: #898781;
      --hairline: rgba(255,255,255,0.10); --grid: #2c2c2a;
      --good-text: #0ca30c;
      --stage-1: #3987e5; --stage-2: #5598e7; --stage-3: #86b6ef;
      --stage-4: #9ec5f4; --stage-5: #b7d3f6;
      --open-fill: #232322; --card-shadow: none;
    }
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { overflow-x: hidden; }
  body {
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    background: var(--page); color: var(--ink);
    font-size: 14px; line-height: 1.45;
    padding: 20px clamp(12px, 3vw, 32px) 60px;
  }
  .sample-banner {
    background: var(--warn); color: #0b0b0b; font-weight: 600; font-size: 12px;
    letter-spacing: .04em; text-transform: uppercase;
    padding: 6px 14px; border-radius: 8px; display: inline-block; margin-bottom: 14px;
  }
  header h1 { font-size: 20px; font-weight: 700; letter-spacing: -0.01em; }
  header .sub { color: var(--ink-2); margin-top: 2px; margin-bottom: 18px; }
  .tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-bottom: 20px; }
  .tile { background: var(--surface); border: 1px solid var(--hairline); border-radius: 12px;
          padding: 12px 14px; box-shadow: var(--card-shadow); }
  .tile .v { font-size: 26px; font-weight: 700; letter-spacing: -0.02em; }
  .tile .v small { font-size: 15px; font-weight: 500; color: var(--muted); }
  .tile .l { color: var(--ink-2); font-size: 12px; margin-top: 1px; }
  .tile .d { font-size: 12px; margin-top: 3px; color: var(--muted); }
  .tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--grid); margin-bottom: 18px; overflow-x: auto; }
  .tab { appearance: none; background: none; border: none; cursor: pointer;
         font: inherit; font-weight: 600; color: var(--muted);
         padding: 8px 14px 10px; border-bottom: 2px solid transparent; white-space: nowrap; }
  .tab.active { color: var(--ink); border-bottom-color: var(--ink); }
  .panel { display: none; }
  .panel.active { display: block; }
  .chip { display: inline-flex; align-items: center; gap: 5px;
          font-size: 11px; font-weight: 600; color: var(--ink-2);
          background: var(--open-fill); border-radius: 20px; padding: 2px 9px; }
  .dot { width: 8px; height: 8px; border-radius: 50%; flex: none; }
  .chip.filled { color: var(--good-text); }
  .org-scroll { overflow-x: auto; padding-bottom: 8px; }
  .org { min-width: 860px; }
  .org-row { display: flex; justify-content: center; gap: 14px; }
  .org-connector { text-align: center; height: 18px; }
  .org-connector::before { content: ""; display: inline-block; width: 1px; height: 18px; background: var(--grid); }
  .seat { background: var(--surface); border: 1px solid var(--hairline); border-radius: 12px;
          box-shadow: var(--card-shadow); padding: 10px 12px; min-width: 150px; max-width: 200px; }
  .seat.open { background: var(--open-fill); border: 1px dashed var(--muted); box-shadow: none; }
  .seat.external { background: none; border: 1px dashed var(--grid); box-shadow: none; text-align: center; }
  .seat .role { font-weight: 650; font-size: 13px; letter-spacing: -0.01em; }
  .seat .who { color: var(--ink-2); font-size: 12px; margin-top: 2px; }
  .seat .who .fade { color: var(--muted); }
  .seat .meta { margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px; }
  .top-row { display: grid; grid-template-columns: 1fr auto 1fr; gap: 16px; align-items: start; }
  .ed-slot { justify-self: center; }
  .ed-slot .seat { min-width: 220px; max-width: 240px; padding: 14px 16px; }
  .ed-slot .seat .role { font-size: 16px; }
  .ed-slot .seat .who { font-size: 13px; }
  .ctx-group { justify-self: end; max-width: 330px; }
  .ctx-cards { justify-content: flex-end; }
  .ctx-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: .06em;
               color: var(--muted); margin-bottom: 5px; }
  .ctx-cards { display: flex; flex-wrap: wrap; gap: 6px; }
  .ctx-card .seat { background: none; border: 1px solid var(--grid); box-shadow: none;
                    padding: 6px 9px; min-width: 110px; max-width: 150px; }
  .ctx-card .role { font-size: 11px; }
  .ctx-card .who { font-size: 11px; margin-top: 1px; }
  .ctx-card .meta { display: none; }
  .org { position: relative; }
  .org-lines { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
  .branches { display: grid; justify-content: center; column-gap: 24px; align-items: start; margin-top: 4px; }
  .deputy-cell { grid-row: 1; padding-bottom: 14px; }
  .branch { grid-row: 2; display: flex; flex-direction: column; gap: 10px; align-items: stretch; min-width: 180px; }
  .branch > .seat.head { border-top: 3px solid var(--stage-3); }
  .branch-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .06em;
                  color: var(--muted); text-align: center; }
  .board { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 10px; align-items: flex-start; }
  .col { min-width: 230px; flex: 1; }
  .col-head { display: flex; align-items: center; gap: 7px; padding: 4px 4px 10px; font-weight: 650; font-size: 13px; }
  .col-head .n { color: var(--muted); font-weight: 600; }
  .card { background: var(--surface); border: 1px solid var(--hairline); border-radius: 12px;
          box-shadow: var(--card-shadow); padding: 11px 12px; margin-bottom: 10px; }
  .card .name { font-weight: 650; font-size: 13.5px; }
  .card .sub { color: var(--ink-2); font-size: 12px; margin-top: 1px; }
  .card .meta { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; }
  .card .note { margin-top: 8px; font-size: 12px; color: var(--ink-2);
                border-top: 1px solid var(--grid); padding-top: 7px; }
  .card .note b { color: var(--muted); font-weight: 600; font-size: 11px; }
  .more { font-size: 11px; color: var(--muted); margin-top: 4px; }
  .section-h { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .06em;
               color: var(--muted); margin: 22px 0 8px; }
  .seatlist { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 10px; }
  .wave-h { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .06em;
            color: var(--muted); margin: 18px 0 8px; }
  .wave-h:first-child { margin-top: 0; }
  .seatrow { background: var(--surface); border: 1px solid var(--hairline); border-radius: 12px;
             box-shadow: var(--card-shadow); padding: 11px 13px;
             display: flex; justify-content: space-between; gap: 10px; align-items: center; }
  .seatrow .r { font-weight: 650; font-size: 13px; }
  .seatrow .s { color: var(--ink-2); font-size: 12px; margin-top: 1px; }
  .empty { color: var(--muted); padding: 20px 4px; }
  footer { margin-top: 26px; color: var(--muted); font-size: 12px; }
"""

SCRIPT = """
  function drawOrgLines() {
    const svg = document.getElementById('org-lines');
    if (!svg) return;
    svg.innerHTML = '';
    const org = svg.parentElement;
    const ed = document.getElementById('ed-slot');
    const dep = document.getElementById('deputy-cell');
    if (!ed || !dep || !dep.offsetParent) return;
    const o = org.getBoundingClientRect(), e = ed.getBoundingClientRect(),
          d = dep.getBoundingClientRect();
    const x1 = e.left + e.width / 2 - o.left, y1 = e.bottom - o.top;
    const x2 = d.left + d.width / 2 - o.left, y2 = d.top - o.top;
    const midY = y1 + (y2 - y1) * 0.55;
    const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    p.setAttribute('d', `M ${x1} ${y1} V ${midY} H ${x2} V ${y2}`);
    p.setAttribute('fill', 'none');
    p.setAttribute('stroke', getComputedStyle(document.documentElement).getPropertyValue('--grid').trim() || '#e1e0d9');
    p.setAttribute('stroke-width', '1.5');
    svg.appendChild(p);
  }
  document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    document.getElementById(t.dataset.p).classList.add('active');
    drawOrgLines();
  }));
  window.addEventListener('load', drawOrgLines);
  window.addEventListener('resize', drawOrgLines);
"""


def chip(label, dot_var=None, cls=""):
    d = f'<span class="dot" style="background:var({dot_var})"></span>' if dot_var else ""
    return f'<span class="chip {cls}">{d}{label}</span>'


def seat_status_chip(seat, candidates):
    n = len(in_play(candidates, seat["id"]))
    filled_n = filled_positions(seat)
    hc = seat.get("headcount", 1)
    if seat["status"] == "filled" or filled_n >= hc and filled_n > 0:
        label = "On board" + (f" · {filled_n} of {hc}" if hc > 1 else "")
        return chip(label, "--good", "filled")
    parts = [STATUS_LABELS.get(seat["status"], seat["status"])]
    if filled_n:
        parts[0] = f"{filled_n} of {hc} on board · " + parts[0]
    if n:
        parts.append(f"{n} in play")
    return chip(" · ".join(parts), STAGE_DOT.get(seat["status"]))


def seat_card_html(seat, candidates, is_head=False, external=False):
    if external:
        return f'<div class="seat external"><div class="role">{esc(seat)}</div></div>'
    filled_n = filled_positions(seat)
    open_cls = "" if filled_n else " open"
    names = ", ".join(esc(n) for n in incumbents_of(seat))
    if names:
        # Filled boxes lead with the person's name; the role is the subline.
        auth = seat.get("hiring_authority")
        auth_note = ""
        if auth not in (None, "tbd", "schedule-c") and auth not in seat["title"].lower():
            auth_note = f' <span class="fade">· {esc(auth.upper() if auth == "ipa" else auth)}</span>'
        top, sub = names, esc(seat["title"]) + auth_note
    else:
        hc = seat.get("headcount", 1)
        sub = "Open" if hc == 1 else f"{hc} open seats"
        if seat.get("acting"):
            sub += f' · <span class="fade">{esc(seat["acting"])}</span>'
        top = esc(seat["title"])
    return (
        f'<div class="seat{open_cls}{" head" if is_head else ""}">'
        f'<div class="role">{top}</div>'
        f'<div class="who">{sub}</div>'
        f'<div class="meta">{seat_status_chip(seat, candidates)}</div>'
        f'</div>'
    )


def org_tab_html(seats, candidates):
    ed = next((s for s in seats if s["id"] == "ed"), None)
    context = [s for s in seats if s.get("context")]
    usia = [s for s in seats if not s.get("context") and s["id"] != "ed"]

    deputies = [s for s in usia if s.get("tier") == "deputy"]
    rest = [s for s in usia if s.get("tier") != "deputy"]
    teams_seen = list(dict.fromkeys(s.get("team", "") for s in rest))
    order = [t for t in BRANCH_ORDER if t in teams_seen] \
        + [t for t in teams_seen if t not in BRANCH_ORDER]
    branches = []
    for i, team in enumerate(order):
        group = [s for s in rest if s.get("team") == team]
        if not group:
            continue
        label = BRANCH_LABELS.get(team, team.replace("-", " ").title())
        cards = "".join(seat_card_html(s, candidates, is_head=bool(s.get("lead")))
                        for s in group)
        branches.append(
            f'<div class="branch" style="grid-column:{i + 1}">'
            f'<div class="branch-label">{esc(label)}</div>{cards}</div>'
        )
    # tier: deputy seats sit in their own row above the column labels, so every
    # label stays aligned; a connector line to the ED is drawn by script
    deputy_cells = ""
    for s in deputies:
        col = order.index(s["team"]) + 1 if s.get("team") in order else 1
        deputy_cells += (
            f'<div class="deputy-cell" id="deputy-cell" style="grid-column:{col}">'
            + seat_card_html(s, candidates, is_head=True) + "</div>"
        )

    ed_card = seat_card_html(ed, candidates) if ed else ""
    top_row = f'<div></div><div class="ed-slot" id="ed-slot">{ed_card}</div>'
    if context:
        cards = "".join(f'<div class="ctx-card">{seat_card_html(s, candidates)}</div>'
                        for s in context)
        top_row += (
            '<div class="ctx-group">'
            '<div class="ctx-label">Commerce leadership — same level, all report to the Secretary</div>'
            f'<div class="ctx-cards">{cards}</div></div>'
        )
    else:
        top_row += "<div></div>"

    return (
        '<div class="org-scroll"><div class="org">'
        '<svg class="org-lines" id="org-lines"></svg>'
        f'<div class="org-row">{seat_card_html("Secretary of Commerce", None, external=True)}</div>'
        '<div class="org-connector"></div>'
        f'<div class="org-row top-row">{top_row}</div>'
        f'<div class="branches" style="grid-template-columns:repeat({len(order)},auto)">'
        f'{deputy_cells}{"".join(branches)}</div>'
        '</div></div>'
    )


def note_html(rec, label=None):
    entry, more = latest_log(rec)
    if not entry:
        return ""
    tag = esc(label) if label else fmt_date(entry.get("date"), "short")
    out = f'<div class="note"><b>{tag}</b> — {esc(entry.get("note", ""))}</div>'
    if more:
        out += f'<div class="more">{more} earlier note{"s" if more > 1 else ""}</div>'
    return out


def candidate_card_html(c, seat_titles, source_names):
    chips = [chip("→ " + esc(seat_titles.get(t, t))) for t in c.get("target_seats", [])]
    if c.get("via"):
        chips.append(chip("via " + esc(source_names.get(c["via"], c["via"]))))
    elif c.get("origin"):
        chips.append(chip("via " + esc(c["origin"])))
    if c.get("clearance") and c["clearance"] != "unknown":
        chips.append(chip("clearance: " + esc(c["clearance"])))
    if c.get("conflicts"):
        chips.append(chip("conflicts: review"))
    sub = f'<div class="sub">{esc(c["current_role"])}</div>' if c.get("current_role") else ""
    return (
        f'<div class="card"><div class="name">{esc(c["name"])}</div>{sub}'
        f'<div class="meta">{"".join(chips)}</div>{note_html(c)}</div>'
    )


def pipeline_tab_html(candidates, seats, sources):
    seat_titles = {s["id"]: s["title"] for s in seats}
    source_names = {s["id"]: s["name"] for s in sources}
    cols = []
    for stage in ACTIVE_STAGES + ["stalled"]:
        group = [c for c in candidates if c.get("stage") == stage]
        if stage == "stalled" and not group:
            continue
        cards = "".join(candidate_card_html(c, seat_titles, source_names) for c in group)
        dot = (f'<span class="dot" style="background:var({STAGE_DOT[stage]})"></span>'
               if stage in STAGE_DOT else "")
        cols.append(
            f'<div class="col"><div class="col-head">{dot}'
            f'{STAGE_LABELS[stage]} <span class="n">{len(group)}</span></div>'
            f'{cards or "<div class=empty>—</div>"}</div>'
        )
    return f'<div class="board">{"".join(cols)}</div>'


def source_card_html(s, cand_names):
    chips = [chip(SOURCE_TYPE_LABELS.get(s["type"], s["type"]))]
    if s.get("for"):
        chips.append(chip("for: " + esc(s["for"])))
    if s["status"] == "called-waiting":
        if s.get("ball_in_court"):
            chips.append(chip("their move" if s["ball_in_court"] == "them" else "our move"))
        if s.get("last_contact"):
            chips.append(chip("last: " + fmt_date(s["last_contact"])))
    for p in s.get("produced", []) or []:
        chips.append(chip("→ " + esc(cand_names.get(p, p)), None, "filled"))
    note = note_html(s)
    if not note and s.get("why") and s["status"] == "to-call":
        note = f'<div class="note"><b>WHY</b> — {esc(s["why"])}</div>'
    contact = (f'<div class="sub">{esc(s["contact"])}</div>' if s.get("contact") else "")
    return (f'<div class="card"><div class="name">{esc(s["name"])}</div>{contact}'
            f'<div class="meta">{"".join(chips)}</div>{note}</div>')


def sourcing_tab_html(sources, candidates):
    if not sources:
        return '<div class="empty">No sources tracked yet.</div>'
    cand_names = {c["id"]: c["name"] for c in candidates}
    cols = []
    for status, label in SOURCE_COLUMNS:
        group = [s for s in sources if s["status"] == status]
        if status == "dry" and not group:
            continue
        cards = "".join(source_card_html(s, cand_names) for s in group)
        dot = (f'<span class="dot" style="background:var({STAGE_DOT[status]})"></span>'
               if status in STAGE_DOT else "")
        cols.append(
            f'<div class="col"><div class="col-head">{dot}{label} '
            f'<span class="n">{len(group)}</span></div>'
            f'{cards or "<div class=empty>—</div>"}</div>'
        )
    return f'<div class="board">{"".join(cols)}</div>'


def open_seats_tab_html(seats, candidates):
    open_seats = [s for s in seats
                  if not s.get("context") and filled_positions(s) < s.get("headcount", 1)]
    if not open_seats:
        return '<div class="empty">Every seat is filled.</div>'
    waves = sorted({s.get("wave", 99) for s in open_seats})
    out = []
    for w in waves:
        group = [s for s in open_seats if s.get("wave", 99) == w]
        title = f"Wave {w}" + (" — critical path" if w == 1 else "")
        rows = []
        for s in group:
            n = len(in_play(candidates, s["id"]))
            hc = s.get("headcount", 1)
            fn = filled_positions(s)
            name = esc(s["title"]) + (f" ×{hc}" if hc > 1 else "")
            bits = []
            if fn:
                bits.append(f"{fn} of {hc} on board")
            bits.append(f"{n} in play" if n else "no slate yet")
            if s.get("acting"):
                bits.append(esc(s["acting"]))
            rows.append(
                f'<div class="seatrow"><div><div class="r">{name}</div>'
                f'<div class="s">{" · ".join(bits)}</div></div>'
                f'{seat_status_chip(s, candidates)}</div>'
            )
        out.append(f'<div class="wave-h">{title}</div><div class="seatlist">{"".join(rows)}</div>')
    return "".join(out)


def dashboard_html(seats, candidates, sources):
    today = date.today()
    usia_seats = [s for s in seats if not s.get("context")]
    total = sum(s.get("headcount", 1) for s in usia_seats)
    filled = sum(filled_positions(s) for s in usia_seats)
    active = [c for c in candidates if c.get("stage") in ACTIVE_STAGES]
    waiting = len([c for c in active if c["stage"] == "waiting"])
    screening = len([c for c in active if c["stage"] == "screening"])
    worked = [s for s in sources if s["status"] != "to-call"]
    producing = len([s for s in sources if s["status"] == "produced"])
    to_call = [s for s in sources if s["status"] == "to-call"]
    tc_gov = len([s for s in to_call if s["type"] == "government"])
    tc_priv = len([s for s in to_call if s["type"] == "private"])
    tc_other = len(to_call) - tc_gov - tc_priv
    tc_bits = [b for b, n in (("%d gov" % tc_gov, tc_gov), ("%d private" % tc_priv, tc_priv),
                              ("%d other" % tc_other, tc_other)) if n]

    banner = ('<div class="sample-banner">Contains example records — replace with real data</div>'
              if has_example_records(candidates, sources) else "")
    updated = today.strftime("%B %-d, %Y")

    tiles = (
        f'<div class="tile"><div class="v">{filled}<small> / {total}</small></div>'
        f'<div class="l">Positions filled</div></div>'
        f'<div class="tile"><div class="v">{len(active)}</div><div class="l">Candidates in play</div>'
        f'<div class="d">{waiting} waiting · {screening} in screening</div></div>'
        f'<div class="tile"><div class="v">{len(worked)}</div><div class="l">Sources worked</div>'
        f'<div class="d">{producing} produced names</div></div>'
        f'<div class="tile"><div class="v">{len(to_call)}</div><div class="l">Still to call</div>'
        f'<div class="d">{" · ".join(tc_bits) if tc_bits else "&nbsp;"}</div></div>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Investment Accelerator — Buildout</title>
<style>{CSS}</style>
</head>
<body>
{banner}
<header>
  <h1>Investment Accelerator — Buildout</h1>
  <div class="sub">Current status · updated {updated}</div>
</header>
<div class="tiles">{tiles}</div>
<div class="tabs">
  <button class="tab active" data-p="org">Org Chart</button>
  <button class="tab" data-p="pipe">Candidate Pipeline</button>
  <button class="tab" data-p="src">Sourcing</button>
  <button class="tab" data-p="open">Open Seats</button>
</div>
<section class="panel active" id="org">{org_tab_html(seats, candidates)}</section>
<section class="panel" id="pipe">{pipeline_tab_html(candidates, seats, sources)}</section>
<section class="panel" id="src">{sourcing_tab_html(sources, candidates)}</section>
<section class="panel" id="open">{open_seats_tab_html(seats, candidates)}</section>
<footer>Generated {today.isoformat()} from org-data records · not hand-edited</footer>
<script>{SCRIPT}</script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# Markdown views (for reading in the repo on GitHub)
# --------------------------------------------------------------------------- #

def org_chart_md(seats, candidates):
    lines = [
        "<!-- GENERATED FILE — do not edit. Source: 02-organization/org-data/ ; "
        "regenerate with tools/generate_org_views.py -->",
        "",
        "# Org Chart — Buildout Status",
        "",
        f"Generated {date.today().isoformat()} from `org-data/`. Box color = seat "
        "status; `n in play` = active candidates targeting the seat. "
        "(The ED-facing version is `dashboard.html`.)",
        "",
        "```mermaid",
        "flowchart TD",
        '    secretary["Secretary of Commerce"]:::external',
    ]
    for s in seats:
        label = s["title"]
        extras = [STATUS_LABELS.get(s["status"], s["status"])]
        if s.get("headcount", 1) > 1:
            extras.append(f"{s['headcount']} seats")
        n = len(in_play(candidates, s["id"]))
        if n:
            extras.append(f"{n} in play")
        names = incumbents_of(s)
        if names:
            extras.append(", ".join(names))
        if s.get("acting"):
            extras.append(s["acting"])
        label += "<br/><i>" + " · ".join(extras) + "</i>"
        lines.append(f'    {node_id(s["id"])}["{label}"]:::{s["status"].replace("-", "_")}')
    lines.append("")
    for s in seats:
        arrow = "-.->" if s["reports_to"] == "secretary" else "-->"
        lines.append(f'    {node_id(s["reports_to"])} {arrow} {node_id(s["id"])}')
    lines.append("")
    lines.append("    classDef external fill:#ffffff,stroke:#666,stroke-dasharray: 4 3;")
    for status, (fill, stroke) in MERMAID_STYLES.items():
        lines.append(
            f"    classDef {status.replace('-', '_')} fill:{fill},stroke:{stroke},stroke-width:2px;"
        )
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def dashboard_md(seats, candidates, sources):
    today = date.today()
    active = [c for c in candidates if c.get("stage") in ACTIVE_STAGES]
    usia_seats = [s for s in seats if not s.get("context")]
    total = sum(s.get("headcount", 1) for s in usia_seats)
    filled = sum(filled_positions(s) for s in usia_seats)
    seat_titles = {s["id"]: s["title"] for s in seats}
    seats = usia_seats  # the wave table covers USIA hiring, not Commerce context

    md = [
        "<!-- GENERATED FILE — do not edit. Source: 02-organization/org-data/ ; "
        "regenerate with tools/generate_org_views.py -->",
        "",
        "# Hiring Dashboard (text view)",
        "",
        f"Generated {today.isoformat()}. **{filled} of {total} positions filled** · "
        f"**{len(active)} candidate{'s' if len(active) != 1 else ''} in play** · "
        f"**{len(sources)} sources tracked**. "
        "(The ED-facing version is `dashboard.html`.)",
        "",
        "## Seats by hiring wave",
        "",
        "| Wave | Seat | Team | Status | Authority | Funded | In play |",
        "|---|---|---|---|---|---|---|",
    ]
    for s in sorted(seats, key=lambda s: (s.get("wave", 99), s["title"])):
        n = len(in_play(candidates, s["id"]))
        hc = f" ×{s['headcount']}" if s.get("headcount", 1) > 1 else ""
        md.append(
            f"| {s.get('wave', '')} | {s['title']}{hc} | {s['team']} "
            f"| {STATUS_LABELS.get(s['status'], s['status'])} "
            f"| {s.get('hiring_authority', '')} | {fmt_yesno(s.get('funded'))} | {n or ''} |"
        )

    md += ["", "## Candidate pipeline", ""]
    if active:
        md += ["| Candidate | Stage | Target seat(s) | Owner | Clearance |",
               "|---|---|---|---|---|"]
        for stage in ACTIVE_STAGES:
            for c in [c for c in active if c["stage"] == stage]:
                targets = ", ".join(seat_titles.get(t, t) for t in c.get("target_seats", []))
                md.append(f"| {c['name']} | {stage} | {targets} "
                          f"| {c.get('owner', '')} | {c.get('clearance', '')} |")
    else:
        md.append("_No active candidates yet._")

    md += ["", "## Sourcing", ""]
    if sources:
        cand_names = {c["id"]: c["name"] for c in candidates}
        md += ["| Source | Type | Status | For | Produced | Last contact |",
               "|---|---|---|---|---|---|"]
        for status, _label in SOURCE_COLUMNS:
            for s in [s for s in sources if s["status"] == status]:
                produced = ", ".join(cand_names.get(p, p) for p in s.get("produced", []) or [])
                md.append(f"| {s['name']} | {s['type']} | {s['status']} | {s.get('for', '')} "
                          f"| {produced} | {fmt_date(s.get('last_contact'))} |")
    else:
        md.append("_No sources tracked yet._")

    md.append("")
    return "\n".join(md)


# --------------------------------------------------------------------------- #

def main():
    seats, candidates, sources = load()
    validate(seats, candidates, sources)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "dashboard.html").write_text(dashboard_html(seats, candidates, sources))
    (OUT / "org-chart.md").write_text(org_chart_md(seats, candidates))
    (OUT / "hiring-dashboard.md").write_text(dashboard_md(seats, candidates, sources))
    print(f"Wrote {OUT / 'dashboard.html'}  <- send this file to the ED")
    print(f"Wrote {OUT / 'org-chart.md'}")
    print(f"Wrote {OUT / 'hiring-dashboard.md'}")
    if warnings:
        print(f"{len(warnings)} warning(s) — see above.", file=sys.stderr)


if __name__ == "__main__":
    main()
