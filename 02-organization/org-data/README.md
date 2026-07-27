# Org Data — seats, candidates, and generated views

This directory is the working tool for the buildout: the org chart and hiring
pipeline as structured data, with visual views generated from it. Same
docs-as-code pattern as the deal records (see `07-systems/codex-workspace-plan.md`).

## The model

- **`seats.yaml`** — one record per position. Seats are stable: they exist
  whether or not anyone fills them, and their `status` tracks the seat's
  progress from *defined* through *filled*. This file **is** the org chart.
- **`candidates.yaml`** — people flowing toward seats, joined via
  `target_seats`. Many-to-many: a candidate can be in play for two seats, a
  seat can carry five candidates. Most of these records will end in
  `declined`/`withdrawn` — that's the pipeline working, not failing.

Keep them separate. The org chart answers "what is the shape of the team and
where are the gaps"; the pipeline answers "who is in motion and what happens
next." Mixing them makes both questions harder.

## Daily workflow

1. Edit `seats.yaml` and/or `candidates.yaml`. Every **active candidate** must
   have an `owner`, a `stage`, and a `next_action` with a date — the generator
   warns on stale records.
2. Regenerate the views:

   ```
   python3 tools/generate_org_views.py
   ```

3. Commit both the data and the regenerated files together. The git log becomes
   the hiring history for free.

Generated outputs (never hand-edit; fix the data and re-run):

- `../generated/org-chart.md` — visual org chart, color-coded by seat status,
  with active-candidate counts per seat. Renders on GitHub via Mermaid.
- `../generated/hiring-dashboard.md` — the action list (what needs doing, by
  when, flagged when overdue), seats by hiring wave, and the candidate
  pipeline by stage.

## Conventions that keep this useful

- **Flip the seat, close the candidate.** When someone enters on duty: seat
  `status: filled` + `incumbent:` name; candidate `stage: eod`.
- **Check clearance and conflicts at screening**, not at selection — they are
  the post-offer timeline, and for SGE advisors conflicts can be disqualifying.
- **Statuses are vocabulary, not prose.** The controlled lists live in the
  header comments of each YAML file; the generator validates against them.

## Handling

`candidates.yaml` holds PII and pre-decisional personnel assessments. Keep the
repository access-controlled, and move candidate records into the approved
environment if information-handling rules require it. Seat structure is
public-information-derived and stays here.
