# Codex Workspace Plan (CUI Environment Buildout)

What to build once CUI-approved Codex access arrives, in what order, and the
information-handling rules that make it safe. The core idea: **docs-as-code**.
Deal truth lives in structured records; every document anyone reads (one-pagers,
dashboards, briefing books) is generated from those records. Nothing is hand-copied
between documents, so nothing drifts out of date.

## Information handling rules (first, because they gate everything)

1. **This scaffold repo stays unclassified.** Templates, frameworks, process — no
   deal specifics ever. Port it into the CUI environment; don't port CUI back.
2. **Deal content exists only in the CUI environment.** Records, one-pagers,
   memos, the precedent library, real toolkit capacity numbers and POCs.
3. **CUI markings are generated, not remembered.** The document generator stamps
   the marking block on every output per your marking guide — humans forget,
   templates don't.
4. **Access is role-scoped from day one.** Deal teams see their deals; leadership
   sees everything; the portfolio team sees closed deals. Easier to build in early
   than retrofit.
5. **No AI tool outside the approved boundary touches deal content.** (The reason
   this repo is built the way it is.)

## Target workspace layout (CUI environment)

```
accelerator/
  deals/
    <codename>.yaml          # one record per deal — THE source of truth
  generated/                 # never hand-edited; rebuilt by tooling
    one-pagers/<codename>.md (+ .docx/.pdf renditions)
    pipeline-dashboard.md
    briefing-book/<YYYY-MM>.md
    portfolio-report/<YYYY-Qq>.md
  playbooks/
    lifecycle/               # stage procedures (from 03-deal-process)
    toolkit/                 # living version of 06-toolkit with real capacity, POCs,
                             # stacking-compatibility matrix
  precedents/
    <codename>/              # closed-deal structures, term summaries, lessons
  org/
    org-chart.mmd            # org chart as mermaid — versioned like everything else
    roles/                   # role cards from 02-organization
  frameworks/                # scoring weights, tier thresholds (from 05-frameworks)
  tools/                     # the generator scripts Codex writes/maintains
```

## Build order

### Sprint 1 — Records & one-pagers (the 80% win)
- Implement the deal record schema (`04-templates/deal-record-schema.yaml`) with
  validation: controlled vocabularies enforced, required fields checked, dates
  machine-stamped.
- Generator: record → one-pager (markdown + Word/PDF rendition for the front
  office), CUI block stamped.
- Migrate every active deal into a record. This migration *is* the Phase 0
  pipeline cleanup — do them together.

### Sprint 2 — Pipeline dashboard
- Generator: all records → one pipeline view (deals by tier × stage, owner, next
  decision + date, aging flags vs. expected dwell times).
- This artifact runs the weekly pipeline meeting. When the meeting runs off the
  generated page, record hygiene enforces itself.

### Sprint 3 — Briefing book
- Generator: monthly Secretary briefing book — tiered pipeline summary, decision
  asks collected from every record's `decision_needed`, upcoming announcements,
  portfolio flags. Assembled in minutes, not staff-days.

### Sprint 4 — Toolkit & scoring integration
- Toolkit playbook as structured data: instrument, agency, capacity, POC, status,
  stacking-compatibility matrix. Package tables in one-pagers link to it.
- Scoring calculator: dimension scores in the record → weighted total, tier
  suggestion, and a diff view showing score changes at each re-scoring.

### Sprint 5 — Portfolio & precedents
- Monitor-stage records gain milestone schedules; generator produces the quarterly
  portfolio report and surfaces upcoming/missed milestones automatically.
- Precedent library: on every close, the handoff package is filed as a structured
  precedent (structure used, package composition, terms, lessons) — searchable when
  the next similar deal arrives.

## What Codex is for, day to day

- Writing and maintaining the generator/validation tooling (simple scripts — this
  is deliberately boring technology: YAML + scripts + markdown, no database or app
  to procure and accredit).
- Drafting from precedent: "start a package memo for <deal> using the nearest
  precedent structure."
- Consistency checks: records whose stage hasn't moved past dwell time, decisions
  past their `decision_by` date, packages relying on instruments flagged as
  capacity-constrained.
- Q&A over the corpus: "which active deals rely on DOE LPO?" — answered from
  records, with citations to them.

## Practices

- **Git discipline:** every record change is a commit; the log *is* the deal
  history. Stage changes reference the pipeline meeting date.
- **Generated files are never edited by hand.** If a one-pager is wrong, fix the
  record and regenerate. (Enforce with a header comment + CI check.)
- **Weekly regeneration at minimum**; before every pipeline meeting ideally.
- **A human owns every document.** Generation removes drudgery, not accountability —
  the deal lead still signs the one-pager's accuracy.

## Success test

By end of Phase 1: the Monday pipeline meeting runs off a dashboard nobody
hand-assembled, and producing the Secretary's monthly book takes under an hour.
That's the whole point of the system.
