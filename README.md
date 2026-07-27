# U.S. Investment Accelerator — Organizational Operating System

This repository is the planning scaffold for building out the Investment Accelerator's
organization, deal process, and analytical frameworks over the next two years. It is
designed to be reviewed with the Executive Director, refined, and then ported into the
CUI-approved development environment where deal-specific content will live.

## What this answers

The materials here are organized around five questions the ED needs answered:

1. **What are we for?** — Mandate, mission, decision rights → `01-strategy/`
2. **How should the team be shaped?** — Org design, roles, hiring waves → `02-organization/`
3. **How do deals move?** — Lifecycle, stage gates, cadence, artifacts → `03-deal-process/`
4. **How do we decide what matters?** — Strategic importance scoring, origination analysis → `05-frameworks/`
5. **What tools can we bring to a deal?** — Cross-government funding and authorities map → `06-toolkit/`

Plus two supporting pieces:

- `04-templates/` — The improved deal one-pager, decision memo, and a structured
  deal-record schema so documents can be generated from data rather than hand-edited.
- `07-systems/` — The plan for what to actually build in Codex once access arrives
  (docs-as-code pipeline, dashboards, briefing books).

## Repository map

```
01-strategy/
  mandate-and-mission.md          Mission, scope, decision rights, open questions for the ED
  two-year-roadmap.md             Phased buildout: foundation → scale → institutionalize
02-organization/
  org-design.md                   Three org models with charts; recommended hybrid
  roles-and-hiring.md             Role cards and hiring waves
  org-data/
    seats.yaml                    The org chart as data — one record per seat
    candidates.yaml               The hiring pipeline as data — candidates → seats
  generated/                      Never hand-edited; rebuilt by tools/
    org-chart.md                  Visual org chart (Mermaid), color-coded by status
    hiring-dashboard.md           Action list, seats by wave, pipeline by stage
03-deal-process/
  deal-lifecycle-and-cadence.md   Stage gates, required artifacts, meeting rhythm, RACI
04-templates/
  deal-one-pager-template.md      The upgraded one-pager (with design rationale)
  decision-memo-template.md       Short-form memo for ED/Secretary decisions
  deal-record-schema.yaml         Structured data model behind the one-pager
05-frameworks/
  strategic-importance-scoring.md Weighted scoring + tiering for prioritization
  origination-analysis.md         Channels, funnel metrics, sector screening method
06-toolkit/
  federal-funding-and-authorities-map.md  Catalog of federal tools by instrument type
07-systems/
  codex-workspace-plan.md         What to build in the CUI environment and how
tools/
  generate_org_views.py           Rebuilds 02-organization/generated/ from org-data/
```

## Information handling

Everything in this repository is **structure and template only** — built from public
information (EO 14255 and publicly announced programs). It contains no deal-specific,
pre-decisional, or CUI content, and none should be added here. Deal data, real
one-pagers, and pipeline records belong exclusively in the CUI-approved environment.
The templates include CUI marking blocks as placeholders so that discipline is built
in from day one.

## How to use this

1. Read `01-strategy/mandate-and-mission.md` first and resolve the open questions with the ED.
2. Pressure-test the org design and roadmap against actual headcount and hiring authorities.
3. Pilot the new one-pager format on 2–3 live deals (in the CUI environment).
4. When Codex access arrives, follow `07-systems/codex-workspace-plan.md` to stand up
   the working environment.
