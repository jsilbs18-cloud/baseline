# Deal One-Pager — Template & Design Rationale

## What's wrong with most one-pagers (and what this fixes)

Typical failure modes: no standard vocabulary (so pages can't be compared or
aggregated), status prose instead of a decision ask, no strategic rationale beyond
"big investment," and no way to tell how stale the page is. This template fixes those
with four rules:

1. **Standardized header fields** (tier, stage, owner, date) so every page rolls up
   into a pipeline view automatically.
2. **The decision ask is a named section, near the top.** If the reader is the
   Secretary, the page's job is to get a decision.
3. **Strategic rationale answers "why us, why now, what if we don't."** Not sector
   boilerplate.
4. **Generated, not hand-formatted.** The page renders from the deal record
   (`deal-record-schema.yaml`) so it is never out of date relative to the system.

Hard limit: one page. Anything longer is a memo, and memos have their own template.

---

## Template

```
[CUI MARKING BLOCK — apply per your marking guide in the CUI environment]

DEAL: <Codename / Company — Project name>                    TIER: <1/2/3>
Owner: <deal lead>        Stage: <lifecycle stage>           Updated: <date>
Score: <NN/100>           Next milestone: <what, by when>

── DECISION NEEDED ──────────────────────────────────────────────
<One sentence: what decision, from whom, by when. If none: "None — on track;
next gate <date>.">

── SNAPSHOT ─────────────────────────────────────────────────────
Investor(s):        <company/consortium, HQ, credibility note>
Investment:         <$X.XB capex over Y years>
Location(s):        <site(s), state(s); site status>
Jobs:               <construction / permanent>
Sector:             <priority sector>       First production: <date>

── STRATEGIC RATIONALE ──────────────────────────────────────────
Priority alignment: <which national priority / directive this serves>
Dependency addressed: <the specific foreign dependency, chokepoint, or
                       capability gap — quantified where possible>
If we don't act:    <what happens — investment goes abroad, dependency
                     persists, competitor nation captures it>

── FEDERAL PACKAGE ──────────────────────────────────────────────
| Instrument | Agency | Amount/Terms | Status |
|---|---|---|---|
| <e.g., loan guarantee> | <DOE LPO> | <$X.XB> | <term sheet / conditional / committed> |
| <e.g., ITC> | <Treasury> | <est. value> | <eligibility confirmed> |
Leverage: <$X private per federal $>   State/local: <incentives, status>

── STRUCTURE & TERMS ────────────────────────────────────────────
<2–3 lines: deal structure, any government position (equity, rights,
milestone conditions), key negotiated terms>

── STATUS & NEXT 30 DAYS ────────────────────────────────────────
• <done/in-flight item>
• <next action, owner, date>

── RISKS ────────────────────────────────────────────────────────
| Risk | Severity | Mitigation |
|---|---|---|
| <top 3 only> | H/M/L | <one line each> |

── INTERAGENCY / POCs ───────────────────────────────────────────
<Agency: name — role>   <Company: name — role>   <State: name — role>
```

---

## Field discipline (what makes aggregation work)

- **Tier** and **Stage** use only the controlled vocabulary from
  `05-frameworks/strategic-importance-scoring.md` and
  `03-deal-process/deal-lifecycle-and-cadence.md`.
- **Score** is the current framework score — re-scored at each stage gate.
- **Updated** is machine-stamped at generation time, never typed.
- **Decision needed** is either a real ask or the explicit "none" line. Blank is
  not allowed — blank is how decisions get lost.
- Dollar figures carry their basis: committed vs. estimated vs. company-claimed.

## Variants

- **Screening one-pager** (Stage 2): header + Snapshot + Strategic rationale +
  a "what would make this real" list. No package section yet.
- **Secretary briefing version:** identical content, decision section first,
  10.5pt, no internal POCs.
- **Announcement-ready version:** strips pre-decisional content; produced only
  after clearance.

## Illustrative example (fictional, for format only)

```
DEAL: NORTHSTAR — Example Alloys U.S. gallium refinery          TIER: 1
Owner: J. Smith          Stage: 4-Structure          Updated: 2026-07-24
Score: 82/100            Next milestone: package memo to ED, Aug 8

── DECISION NEEDED ──
ED endorsement of package option B (loan guarantee + offtake floor) by Aug 15
to hold investor's board timeline.

── SNAPSHOT ──
Investor: Example Alloys (US) w/ allied co-investor; $2.1B capex over 3 yrs;
Site: <state>, brownfield, site control complete; Jobs: 1,800 constr / 600 perm;
Sector: Critical minerals; First production: 2029.

── STRATEGIC RATIONALE ──
Priority alignment: critical minerals independence directive.
Dependency addressed: ~98% of refined gallium currently imported from a single
foreign supplier; project covers ~40% of US demand.
If we don't act: investor proceeds with Gulf-region siting; dependency persists.
...
```

(Example is invented; real content lives only in the CUI environment.)
