#!/usr/bin/env python3
"""Generate org views from 02-organization/org-data/*.yaml.

Reads seats.yaml and candidates.yaml, validates them, and writes:

    02-organization/generated/org-chart.md        visual org chart (Mermaid)
    02-organization/generated/hiring-dashboard.md seats x status, pipeline, actions

Generated files are never edited by hand: fix the data, re-run this script.

Usage:  python3 tools/generate_org_views.py
"""

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
    "sourced", "screened", "interviewing", "selected", "clearance-ethics",
    "eod", "hold", "declined", "withdrawn",
]
ACTIVE_STAGES = ["sourced", "screened", "interviewing", "selected", "clearance-ethics"]
HIRING_AUTHORITIES = ["detailee", "ipa", "sge", "excepted", "direct-hire", "schedule-c", "tbd"]

STATUS_LABELS = {
    "defined": "Defined", "approved": "Approved", "sourcing": "Sourcing",
    "interviewing": "Interviewing", "selected": "Selected",
    "clearance-ethics": "Clearance/Ethics", "filled": "Filled", "hold": "On hold",
}

# Mermaid class per status: fill, stroke (text stays default for readability)
STATUS_STYLES = {
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


def load():
    seats = yaml.safe_load((DATA / "seats.yaml").read_text())["seats"]
    candidates = yaml.safe_load((DATA / "candidates.yaml").read_text())["candidates"] or []
    return seats, candidates


def validate(seats, candidates):
    seat_ids = {s["id"] for s in seats}
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
        if c.get("stage") in ACTIVE_STAGES:
            for field in ("owner", "next_action", "next_action_date"):
                if not c.get(field):
                    warn(f"candidate {c['id']}: active but missing {field} (stale record)")


def in_play(candidates, seat_id):
    return [c for c in candidates
            if seat_id in c.get("target_seats", []) and c.get("stage") in ACTIVE_STAGES]


def node_id(seat_id):
    """Mermaid-safe node id (hyphens can break flowchart parsing)."""
    return seat_id.replace("-", "_")


def fmt_yesno(v):
    """YAML 1.1 reads bare yes/no as booleans; show them as words."""
    if v is True:
        return "yes"
    if v is False:
        return "no"
    return str(v) if v is not None else ""


def fmt_date(d):
    if isinstance(d, (date, datetime)):
        return d.strftime("%Y-%m-%d")
    return str(d) if d else ""


def as_date(d):
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    try:
        return date.fromisoformat(str(d))
    except (TypeError, ValueError):
        return None


def org_chart_md(seats, candidates):
    lines = [
        "<!-- GENERATED FILE — do not edit. Source: 02-organization/org-data/ ; "
        "regenerate with tools/generate_org_views.py -->",
        "",
        "# Org Chart — Buildout Status",
        "",
        f"Generated {date.today().isoformat()} from `org-data/seats.yaml` and "
        "`org-data/candidates.yaml`. Box color = seat status; `n in play` = active "
        "candidates targeting the seat.",
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
        if s.get("incumbent"):
            extras.append(s["incumbent"])
        label += "<br/><i>" + " · ".join(extras) + "</i>"
        lines.append(f'    {node_id(s["id"])}["{label}"]:::{s["status"].replace("-", "_")}')
    lines.append("")
    for s in seats:
        arrow = "-.->" if s["reports_to"] == "secretary" else "-->"
        lines.append(f'    {node_id(s["reports_to"])} {arrow} {node_id(s["id"])}')
    lines.append("")
    lines.append("    classDef external fill:#ffffff,stroke:#666,stroke-dasharray: 4 3;")
    for status, (fill, stroke) in STATUS_STYLES.items():
        lines.append(
            f"    classDef {status.replace('-', '_')} fill:{fill},stroke:{stroke},stroke-width:2px;"
        )
    lines.append("```")
    lines += [
        "",
        "| Status | Meaning |",
        "|---|---|",
        "| Defined | Seat exists on paper only |",
        "| Approved | Billet approved and funded; not yet recruiting |",
        "| Sourcing | Building the candidate slate |",
        "| Interviewing | Candidates in interviews |",
        "| Selected | Selection made; pre-clearance |",
        "| Clearance/Ethics | Selectee in clearance, ethics, or paperwork |",
        "| Filled | Incumbent on board |",
        "| On hold | Deliberately paused |",
        "",
    ]
    return "\n".join(lines)


def dashboard_md(seats, candidates):
    today = date.today()
    active = [c for c in candidates if c.get("stage") in ACTIVE_STAGES]
    filled = [s for s in seats if s["status"] == "filled"]
    positions = sum(s.get("headcount", 1) for s in seats)

    md = [
        "<!-- GENERATED FILE — do not edit. Source: 02-organization/org-data/ ; "
        "regenerate with tools/generate_org_views.py -->",
        "",
        "# Hiring Dashboard",
        "",
        f"Generated {today.isoformat()}. "
        f"**{len(filled)} of {len(seats)} seat types filled** "
        f"({positions} total positions at full headcount) · "
        f"**{len(active)} candidate{'s' if len(active) != 1 else ''} in play**.",
        "",
        "## Action list",
        "",
    ]

    actions = []
    for s in seats:
        if s.get("next_action"):
            actions.append((as_date(s.get("next_action_date")), s.get("action_owner", ""),
                            s["next_action"], f"seat: {s['title']}"))
    for c in active:
        if c.get("next_action"):
            actions.append((as_date(c.get("next_action_date")), c.get("owner", ""),
                            c["next_action"], f"candidate: {c['name']}"))
    if actions:
        actions.sort(key=lambda a: (a[0] is None, a[0] or today))
        md += ["| Due | Owner | Action | Re |", "|---|---|---|---|"]
        for due, owner, action, re in actions:
            flag = " ⚠️ overdue" if due and due < today else ""
            md.append(f"| {fmt_date(due)}{flag} | {owner} | {action} | {re} |")
    else:
        md.append("_No open actions — every active record needs a next action and date._")

    md += ["", "## Seats by hiring wave", ""]
    md += ["| Wave | Seat | Team | Status | Authority | Funded | In play |",
           "|---|---|---|---|---|---|---|"]
    for s in sorted(seats, key=lambda s: (s.get("wave", 99), s["title"])):
        n = len(in_play(candidates, s["id"]))
        hc = f" ×{s['headcount']}" if s.get("headcount", 1) > 1 else ""
        md.append(
            f"| {s.get('wave', '')} | {s['title']}{hc} | {s['team']} "
            f"| {STATUS_LABELS.get(s['status'], s['status'])} "
            f"| {s.get('hiring_authority', '')} | {fmt_yesno(s.get('funded'))} | {n or ''} |"
        )

    md += ["", "## Candidate pipeline", ""]
    seat_titles = {s["id"]: s["title"] for s in seats}
    if active:
        for stage in ACTIVE_STAGES:
            group = [c for c in active if c["stage"] == stage]
            if not group:
                continue
            md += [f"### {stage} ({len(group)})", "",
                   "| Candidate | Target seat(s) | Owner | Clearance | Next action | Due |",
                   "|---|---|---|---|---|---|"]
            for c in group:
                targets = ", ".join(seat_titles.get(t, t) for t in c.get("target_seats", []))
                md.append(
                    f"| {c['name']} | {targets} | {c.get('owner', '')} "
                    f"| {c.get('clearance', '')} | {c.get('next_action', '')} "
                    f"| {fmt_date(c.get('next_action_date'))} |"
                )
            md.append("")
    else:
        md.append("_No active candidates yet._")

    inactive = [c for c in candidates if c.get("stage") not in ACTIVE_STAGES]
    if inactive:
        by_stage = {}
        for c in inactive:
            by_stage.setdefault(c["stage"], []).append(c["name"])
        parts = [f"{stage}: {len(names)}" for stage, names in sorted(by_stage.items())]
        md += ["", f"_Inactive records — {'; '.join(parts)}._"]

    md.append("")
    return "\n".join(md)


def main():
    seats, candidates = load()
    validate(seats, candidates)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "org-chart.md").write_text(org_chart_md(seats, candidates))
    (OUT / "hiring-dashboard.md").write_text(dashboard_md(seats, candidates))
    print(f"Wrote {OUT / 'org-chart.md'}")
    print(f"Wrote {OUT / 'hiring-dashboard.md'}")
    if warnings:
        print(f"{len(warnings)} warning(s) — see above.", file=sys.stderr)


if __name__ == "__main__":
    main()
