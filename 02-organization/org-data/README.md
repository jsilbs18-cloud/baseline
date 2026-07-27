# Org Data — seats, candidates, sources, and generated views

This directory is the working tool for the buildout: the org chart, hiring
pipeline, and sourcing map as structured data, with visual views generated from
it. Same docs-as-code pattern as the deal records (see
`07-systems/codex-workspace-plan.md`).

## The model

- **`seats.yaml`** — one record per position. Seats are stable: they exist
  whether or not anyone fills them, and their `status` tracks the seat's
  progress from *defined* through *filled*. This file **is** the org chart.
- **`candidates.yaml`** — people flowing toward seats, joined via
  `target_seats`. Many-to-many: a candidate can be in play for two seats, a
  seat can carry five candidates. Most of these records will end in
  `declined`/`withdrawn` — that's the pipeline working, not failing.
- **`sources.yaml`** — where the ED fishes for talent: companies, government
  offices, individual people, groups. Each has its own status (*to-call →
  called-waiting → produced / dry*), dated notes on what they said, and links
  to the candidates it yielded (`produced`).

The supply chain reads: **sources → produce → candidates → fill → seats.**
Keep the three separate. The org chart answers "what is the shape of the team
and where are the gaps"; the pipeline answers "who is in motion"; sourcing
answers "where are we fishing and what has each hole produced." Mixing them
makes all three questions harder.

## Daily workflow

1. Edit the YAML files (or describe what changed in plain English to Claude,
   which updates them). Every **active candidate** needs an `owner`; dated
   `log` notes capture what happened — nothing forces a schedule.
2. Regenerate the views:

   ```
   python3 tools/generate_org_views.py
   ```

3. Commit both the data and the regenerated files together. The git log becomes
   the hiring history for free.
4. Send `../generated/dashboard.html` to the ED (AirDrop/text/email). It's one
   self-contained file — opens in Safari, works offline, nothing hosted.

Generated outputs (never hand-edit; fix the data and re-run):

- `../generated/dashboard.html` — **the ED-facing page**: four tabs (Org Chart,
  Candidate Pipeline, Sourcing, Open Seats), status tiles, light/dark, mobile-
  friendly.
- `../generated/org-chart.md` — org chart for reading in the repo, color-coded
  by seat status. Renders on GitHub via Mermaid.
- `../generated/hiring-dashboard.md` — text dashboard for the repo: seats by
  wave, pipeline, and sourcing tables.

## Conventions that keep this useful

- **Flip the seat, close the candidate.** When someone enters on duty: seat
  `status: filled` + `incumbent:` name; candidate `stage: eod`.
- **Check clearance and conflicts at screening**, not at selection — they are
  the post-offer timeline, and for SGE advisors conflicts can be disqualifying.
- **Statuses are vocabulary, not prose.** The controlled lists live in the
  header comments of each YAML file; the generator validates against them.

## Handling

`candidates.yaml` holds PII and pre-decisional personnel assessments;
`sources.yaml` holds sensitive relationship notes. Keep the repository
access-controlled, and move these records into the approved environment if
information-handling rules require it. Seat structure is
public-information-derived and stays here. The dashboard file travels
person-to-person (AirDrop/email), never gets hosted publicly.
