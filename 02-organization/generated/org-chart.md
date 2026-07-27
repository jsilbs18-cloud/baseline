<!-- GENERATED FILE — do not edit. Source: 02-organization/org-data/ ; regenerate with tools/generate_org_views.py -->

# Org Chart — Buildout Status

Generated 2026-07-27 from `org-data/`. Box color = seat status; `n in play` = active candidates targeting the seat. (The ED-facing version is `dashboard.html`.)

```mermaid
flowchart TD
    secretary["Secretary of Commerce"]:::external
    commerce_cos["Chief of Staff, Commerce<br/><i>On board · Yvette</i>"]:::filled
    commerce_gc["General Counsel, Commerce<br/><i>On board · Cooper Goodfrey</i>"]:::filled
    commerce_chief_counsel["Chief Counsel of Commerce<br/><i>On board · David Shapiro</i>"]:::filled
    commerce_cfo["CFO, Commerce<br/><i>On board · Prashanth</i>"]:::filled
    ed["Executive Director<br/><i>On board · AMS</i>"]:::filled
    investment_team["Investment Team<br/><i>Interviewing · 5 seats · 5 in play · Jacob, Abhiram</i>"]:::interviewing
    minerals_loan["Critical Minerals (on loan — ITA)<br/><i>On board · Joshua Kroon</i>"]:::filled
    gc["General Counsel (USIA)<br/><i>Sourcing · 2 in play</i>"]:::sourcing
    legal_team["Legal Team<br/><i>On board · 2 seats · Tyler, Iac</i>"]:::filled
    legal_assoc["Senior Associate — Legal<br/><i>Not started · 2 seats</i>"]:::defined
    paralegal["Paralegal<br/><i>Not started</i>"]:::defined
    research_team["Research<br/><i>Sourcing · 2 seats · Matt</i>"]:::sourcing
    cos["Chief of Staff (USIA)<br/><i>Sourcing</i>"]:::sourcing
    advisors["Senior Advisors (SGE)<br/><i>On board · 2 seats · Aron, Jon Sobel</i>"]:::filled
    chips["CHIPS Program Office<br/><i>On board · Bill Frauenhoffer (+ team)</i>"]:::filled

    secretary -.-> commerce_cos
    secretary -.-> commerce_gc
    secretary -.-> commerce_chief_counsel
    secretary -.-> commerce_cfo
    secretary -.-> ed
    ed --> investment_team
    ed --> minerals_loan
    ed --> gc
    ed --> legal_team
    ed --> legal_assoc
    ed --> paralegal
    ed --> research_team
    ed --> cos
    ed --> advisors
    ed --> chips

    classDef external fill:#ffffff,stroke:#666,stroke-dasharray: 4 3;
    classDef defined fill:#ececec,stroke:#9e9e9e,stroke-width:2px;
    classDef approved fill:#e3ecf7,stroke:#5b84b1,stroke-width:2px;
    classDef sourcing fill:#d6e6f7,stroke:#2f6db3,stroke-width:2px;
    classDef interviewing fill:#fdf0d2,stroke:#c99a2c,stroke-width:2px;
    classDef selected fill:#fde3c8,stroke:#d97b29,stroke-width:2px;
    classDef clearance_ethics fill:#eadff2,stroke:#7d5ba6,stroke-width:2px;
    classDef filled fill:#d8efd8,stroke:#2e7d32,stroke-width:2px;
    classDef hold fill:#f2d9d9,stroke:#a94442,stroke-width:2px;
```
