#!/usr/bin/env python3
"""Generate the counterpart map from 06-toolkit/entities.yaml.

The counterpart map is the institution-view companion to the instrument-view
toolkit (06-toolkit/federal-funding-and-authorities-map.md): one row per
federal capital-formation entity — who runs it, where it sits, firepower,
track record, mandate/can'ts, wants, and the USIA angle.

Outputs:
    06-toolkit/generated/counterpart-map.html   screen version (Matrix + Cards tabs)
    06-toolkit/generated/print-matrix.html      one-page landscape matrix (print/PDF)
    06-toolkit/generated/print-cards.html       counterpart cards (print/PDF)
    06-toolkit/generated/counterpart-map.md     GitHub-readable version

Generated files are never edited by hand: fix entities.yaml, re-run.

Usage:  python3 tools/generate_counterpart_map.py
"""

import html
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "06-toolkit" / "entities.yaml"
OUT = ROOT / "06-toolkit" / "generated"

GROUPS = [
    ("commerce", "Inside Commerce"),
    ("dod", "Defense"),
    ("doe", "Energy"),
    ("independent", "Independent Agencies"),
    ("other", "Other Departments"),
    ("usia", "USIA Itself"),
]
MATRIX_COLS = [
    ("runs", "Runs it"), ("firepower", "Firepower"), ("done", "Has done"),
    ("must_cant", "Must / can't"), ("wants", "Wants"), ("usia", "USIA angle"),
]

warnings = []


def warn(msg):
    warnings.append(msg)
    print(f"WARNING: {msg}", file=sys.stderr)


def esc(v):
    return html.escape(str(v)) if v is not None else ""


def load():
    doc = yaml.safe_load(DATA.read_text())
    entities = doc["entities"]
    group_keys = {g for g, _ in GROUPS}
    for e in entities:
        if e.get("group") not in group_keys:
            warn(f"entity {e['key']}: unknown group {e.get('group')!r}")
        for col, _label in MATRIX_COLS:
            if not (e.get("matrix") or {}).get(col):
                warn(f"entity {e['key']}: matrix.{col} missing")
        p = e.get("principal") or {}
        if p.get("status") in ("unverified",):
            warn(f"entity {e['key']}: principal unverified — flagged on output")
    return doc.get("as_of", str(date.today())), entities


CSS_BASE = """
  :root {
    color-scheme: light;
    --page: #f9f9f7; --surface: #fcfcfb;
    --ink: #0b0b0b; --ink-2: #52514e; --muted: #898781;
    --hairline: rgba(11,11,11,0.10); --grid: #e1e0d9;
    --accent: #2a78d6; --good-text: #006300; --warn-bg: #fdf0d2;
    --angle-bg: #e9f1fb;
    --card-shadow: 0 1px 2px rgba(11,11,11,0.06), 0 2px 8px rgba(11,11,11,0.05);
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      color-scheme: dark;
      --page: #0d0d0d; --surface: #1a1a19;
      --ink: #ffffff; --ink-2: #c3c2b7; --muted: #898781;
      --hairline: rgba(255,255,255,0.10); --grid: #2c2c2a;
      --accent: #86b6ef; --good-text: #0ca30c; --warn-bg: #3a3115;
      --angle-bg: #1d2a3a; --card-shadow: none;
    }
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
         background: var(--page); color: var(--ink); font-size: 14px; line-height: 1.45; }
"""

CSS_SCREEN = CSS_BASE + """
  body { padding: 20px clamp(12px, 3vw, 32px) 60px; }
  header h1 { font-size: 20px; font-weight: 700; letter-spacing: -0.01em; }
  header .sub { color: var(--ink-2); margin-top: 2px; margin-bottom: 18px; }
  .tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--grid); margin-bottom: 18px; }
  .tab { appearance: none; background: none; border: none; cursor: pointer; font: inherit;
         font-weight: 600; color: var(--muted); padding: 8px 14px 10px;
         border-bottom: 2px solid transparent; white-space: nowrap; }
  .tab.active { color: var(--ink); border-bottom-color: var(--ink); }
  .panel { display: none; } .panel.active { display: block; }
  .m-scroll { overflow-x: auto; }
  table.matrix { border-collapse: collapse; width: 100%; min-width: 1000px; font-size: 12px; }
  .matrix th { text-align: left; font-size: 10px; text-transform: uppercase; letter-spacing: .05em;
               color: var(--muted); padding: 6px 8px; border-bottom: 1px solid var(--grid);
               position: sticky; top: 0; background: var(--page); }
  .matrix td { padding: 7px 8px; border-bottom: 1px solid var(--grid); vertical-align: top; }
  .matrix td.ent { font-weight: 650; min-width: 130px; }
  .matrix td.ent .r { font-weight: 400; color: var(--ink-2); font-size: 11px; }
  .matrix tr.group td { font-size: 10px; font-weight: 700; text-transform: uppercase;
                        letter-spacing: .06em; color: var(--muted); background: var(--surface);
                        padding: 5px 8px; border-bottom: 1px solid var(--grid); }
  .matrix td.angle { background: var(--angle-bg); }
  .flag { color: #a94442; font-weight: 600; font-size: 10px; }
  .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(430px, 1fr)); gap: 14px; }
  .card { background: var(--surface); border: 1px solid var(--hairline); border-radius: 12px;
          box-shadow: var(--card-shadow); padding: 14px 16px; break-inside: avoid; }
  .card h3 { font-size: 15px; letter-spacing: -0.01em; }
  .card .runs { color: var(--ink-2); font-size: 12.5px; margin: 2px 0 8px; }
  .card .sec { margin-top: 8px; }
  .card .sec b { display: block; font-size: 10px; text-transform: uppercase; letter-spacing: .05em;
                 color: var(--muted); margin-bottom: 2px; font-weight: 700; }
  .card .sec, .card li { font-size: 12.5px; color: var(--ink-2); }
  .card ul { padding-left: 16px; margin: 2px 0; }
  .card .angle { background: var(--angle-bg); border-radius: 8px; padding: 8px 10px; margin-top: 10px; }
  .card .angle b { color: var(--accent); }
  .card .risk { background: var(--warn-bg); border-radius: 8px; padding: 6px 10px; margin-top: 8px; font-size: 12px; }
  .card .srcs { margin-top: 8px; font-size: 10.5px; color: var(--muted); word-break: break-all; }
  .card .srcs a { color: var(--muted); }
  footer { margin-top: 24px; color: var(--muted); font-size: 12px; }
"""

CSS_PRINT_MATRIX = CSS_BASE + """
  @page { size: letter landscape; margin: 0.28in; }
  body { background: #fff; font-size: 7.6px; padding: 0; }
  h1 { font-size: 11px; margin-bottom: 0; }
  .sub { color: #52514e; font-size: 7px; margin-bottom: 4px; }
  table.matrix { border-collapse: collapse; width: 100%; }
  .matrix th { text-align: left; font-size: 6.5px; text-transform: uppercase; letter-spacing: .03em;
               color: #898781; padding: 1px 3px; border-bottom: 1px solid #c3c2b7; }
  .matrix td { padding: 2px 3px; border-bottom: 0.5px solid #e1e0d9; vertical-align: top; line-height: 1.22; }
  .matrix td.ent { font-weight: 650; }
  .matrix td.ent .r { font-weight: 400; color: #52514e; font-size: 6.8px; }
  .matrix tr.group td { font-size: 6.5px; font-weight: 700; text-transform: uppercase;
                        letter-spacing: .04em; color: #898781; background: #f4f4f1; padding: 1px 3px; }
  .matrix td.angle { background: #edf3fb; }
  .flag { color: #a94442; font-weight: 600; }
"""

CSS_PRINT_CARDS = CSS_BASE + """
  @page { size: letter; margin: 0.5in; }
  body { background: #fff; padding: 0; font-size: 10.5px; }
  h1 { font-size: 14px; margin-bottom: 6px; }
  .card { border: 1px solid #c3c2b7; border-radius: 8px; padding: 10px 12px;
          margin-bottom: 10px; break-inside: avoid; }
  .card h3 { font-size: 12px; }
  .card .runs { color: #52514e; font-size: 10px; margin: 1px 0 6px; }
  .card .sec { margin-top: 5px; font-size: 10px; color: #333; }
  .card .sec b { display: block; font-size: 7.5px; text-transform: uppercase; letter-spacing: .04em;
                 color: #898781; margin-bottom: 1px; font-weight: 700; }
  .card ul { padding-left: 14px; margin: 1px 0; } .card li { font-size: 10px; }
  .card .angle { background: #edf3fb; border-radius: 6px; padding: 5px 8px; margin-top: 6px; }
  .card .risk { background: #fdf0d2; border-radius: 6px; padding: 4px 8px; margin-top: 5px; }
  .card .srcs { display: none; }
  .flag { color: #a94442; font-weight: 600; }
"""


def principal_line(e):
    p = e.get("principal") or {}
    line = esc(p.get("name", "?"))
    if p.get("title"):
        line += f" — {esc(p['title'])}"
    if p.get("status") == "acting":
        line += ' <span class="flag">(acting)</span>'
    elif p.get("status") == "vacant":
        line = '<span class="flag">Vacant</span>' + (f" — last: {line}" if p.get("name") else "")
    elif p.get("status") == "unverified":
        line += ' <span class="flag">(unverified)</span>'
    return line


def matrix_table(entities, as_of):
    # "runs" is folded into the Entity cell, so its header is skipped
    head = "<tr><th>Entity</th>" + "".join(f"<th>{lbl}</th>" for _c, lbl in MATRIX_COLS[1:]) + "</tr>"
    rows = []
    ncols = len(MATRIX_COLS)
    for gkey, glabel in GROUPS:
        group = [e for e in entities if e.get("group") == gkey]
        if not group:
            continue
        rows.append(f'<tr class="group"><td colspan="{ncols}">{glabel}</td></tr>')
        for e in group:
            m = e.get("matrix") or {}
            cells = [f'<td class="ent">{esc(e.get("short", e["name"]))}'
                     f'<div class="r">{m.get("runs", "")}</div></td>']
            for col, _lbl in MATRIX_COLS[1:]:
                cls = ' class="angle"' if col == "usia" else ""
                cells.append(f"<td{cls}>{m.get(col, '')}</td>")
            rows.append("<tr>" + "".join(cells) + "</tr>")
    return f'<table class="matrix">{head}{"".join(rows)}</table>'


def card_html(e):
    fp = "".join(
        f"<li><b style='display:inline;text-transform:none;font-size:inherit;color:inherit'>"
        f"{esc(f['instrument'])}</b> — {esc(f['what'])}"
        + (f" <i>({esc(f['capacity'])})</i>" if f.get("capacity") else "") + "</li>"
        for f in e.get("firepower", []))
    risk = (f'<div class="risk">⚠ {esc(e["reauth_or_risk"])}</div>'
            if e.get("reauth_or_risk") else "")
    wl = (f'<div class="sec"><b>Working level</b>{esc(e["working_level"])}</div>'
          if e.get("working_level") else "")
    srcs = ""
    if e.get("sources"):
        links = " · ".join(f'<a href="{esc(u)}">{esc(u.split("//")[-1].split("/")[0])}</a>'
                           for u in e["sources"][:4])
        srcs = f'<div class="srcs">{links}</div>'
    lowc = ""
    if e.get("low_confidence"):
        lowc = ('<div class="sec"><b>Not fully verified</b>'
                + "; ".join(esc(x) for x in e["low_confidence"]) + "</div>")
    return f"""<div class="card">
<h3>{esc(e["name"])}</h3>
<div class="runs">{principal_line(e)}</div>
<div class="sec"><b>Where it sits</b>{esc(e.get("situated", ""))}</div>
{wl}
<div class="sec"><b>Firepower</b><ul>{fp}</ul></div>
<div class="sec"><b>Track record</b>{esc(e.get("track_record", ""))}</div>
<div class="sec"><b>Mandate</b>{esc(e.get("mandate", ""))}</div>
<div class="sec"><b>Can't / constraints</b>{esc(e.get("cants", ""))}</div>
<div class="sec"><b>Wants</b>{esc(e.get("wants", ""))}</div>
{risk}
<div class="angle"><b>USIA angle</b> — {esc(e.get("usia_angle", ""))}</div>
{lowc}
{srcs}
</div>"""


def screen_html(entities, as_of):
    cards = ""
    for gkey, glabel in GROUPS:
        group = [e for e in entities if e.get("group") == gkey]
        if group:
            cards += "".join(card_html(e) for e in group)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>USIA Counterpart Map</title><style>{CSS_SCREEN}</style></head><body>
<header><h1>Counterpart Map — Federal Capital-Formation Entities</h1>
<div class="sub">Who runs what, firepower, mandates, and the USIA angle · as of {esc(as_of)} · public information</div></header>
<div class="tabs">
  <button class="tab active" data-p="matrix">One-Page Matrix</button>
  <button class="tab" data-p="cards">Counterpart Cards</button>
</div>
<section class="panel active" id="matrix"><div class="m-scroll">{matrix_table(entities, as_of)}</div></section>
<section class="panel" id="cards"><div class="cards">{cards}</div></section>
<footer>Generated {date.today().isoformat()} from 06-toolkit/entities.yaml · verify time-sensitive facts before relying on them</footer>
<script>
  document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    document.getElementById(t.dataset.p).classList.add('active');
  }}));
</script></body></html>"""


def print_matrix_html(entities, as_of):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>USIA Counterpart Map — Matrix</title>
<style>{CSS_PRINT_MATRIX}</style></head><body>
<h1>Counterpart Map — Federal Capital-Formation Entities</h1>
<div class="sub">As of {esc(as_of)} · public information · blue column = the USIA angle</div>
{matrix_table(entities, as_of)}
</body></html>"""


def print_cards_html(entities, as_of):
    cards = ""
    for gkey, _glabel in GROUPS:
        cards += "".join(card_html(e) for e in entities if e.get("group") == gkey)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>USIA Counterpart Cards</title>
<style>{CSS_PRINT_CARDS}</style></head><body>
<h1>Counterpart Cards · as of {esc(as_of)}</h1>
{cards}
</body></html>"""


def markdown_view(entities, as_of):
    md = [
        "<!-- GENERATED FILE — do not edit. Source: 06-toolkit/entities.yaml ; "
        "regenerate with tools/generate_counterpart_map.py -->",
        "",
        "# Counterpart Map — Federal Capital-Formation Entities",
        "",
        f"As of {as_of}. Institution view of the toolkit — who runs what, firepower, "
        "mandate, and the USIA angle. Instrument view: `federal-funding-and-authorities-map.md`.",
        "",
    ]
    for gkey, glabel in GROUPS:
        group = [e for e in entities if e.get("group") == gkey]
        if not group:
            continue
        md.append(f"## {glabel}")
        md.append("")
        for e in group:
            p = e.get("principal") or {}
            flag = f" ({p['status']})" if p.get("status") not in (None, "confirmed") else ""
            md.append(f"### {e['name']}")
            md.append("")
            md.append(f"- **Runs it:** {p.get('name', '?')} — {p.get('title', '')}{flag}")
            md.append(f"- **Where it sits:** {e.get('situated', '')}")
            for f in e.get("firepower", []):
                cap = f" ({f['capacity']})" if f.get("capacity") else ""
                md.append(f"- **{f['instrument']}** — {f['what']}{cap}")
            md.append(f"- **Track record:** {e.get('track_record', '')}")
            md.append(f"- **Mandate:** {e.get('mandate', '')}")
            md.append(f"- **Can't:** {e.get('cants', '')}")
            md.append(f"- **Wants:** {e.get('wants', '')}")
            if e.get("reauth_or_risk"):
                md.append(f"- **⚠ Watch:** {e['reauth_or_risk']}")
            md.append(f"- **USIA angle:** {e.get('usia_angle', '')}")
            md.append("")
    return "\n".join(md)


def main():
    as_of, entities = load()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "counterpart-map.html").write_text(screen_html(entities, as_of))
    (OUT / "print-matrix.html").write_text(print_matrix_html(entities, as_of))
    (OUT / "print-cards.html").write_text(print_cards_html(entities, as_of))
    (OUT / "counterpart-map.md").write_text(markdown_view(entities, as_of))
    print(f"Wrote {OUT}/counterpart-map.html, print-matrix.html, print-cards.html, counterpart-map.md")
    if warnings:
        print(f"{len(warnings)} warning(s) — see above.", file=sys.stderr)


if __name__ == "__main__":
    main()
