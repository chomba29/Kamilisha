# Stage 5 — Guardrails

**Question:** What must Kamilisha never do, who checks it, and what happens when it gets something wrong?

## Summary

- **13 guardrail rules**, each tied to a requirement and a test. The core: it advises but never decides, answers only from Live circulars with a citation, says "not found" rather than guess, declines workarounds, and keeps customer data out.
- **Oversight in layers:** the officer checks the cited section, procedure owners review a weekly sample, and the Data Management Office reports monthly to the business owner.
- **Three severity levels.** A wrong answer on a control step (S1) switches that procedure off within one hour until it is fixed and retested.
- **12 risks**, each with controls, an early-warning KPI and an owner. Four stay rated Medium after controls (R01, R04, R07, R08); low adoption (R07) is the one the pilot must watch most.

## Deliverables

| File | What it shows |
| --- | --- |
| [intended-use.md](intended-use.md) | What it is for and not for, and the 13 guardrail rules with their requirements and tests |
| [oversight-and-escalation.md](oversight-and-escalation.md) | Routine checks, severity levels, escalation flow and RACI |
| [risk-register.csv](risk-register.csv) | 12 risks with cause, effect, rating, controls, early warning, owner and residual rating |
| [ai-factsheet.md](ai-factsheet.md) | One-page summary for governance review |

## Key judgements

- **Controls belong in systems, not in the assistant.** The blocking form is enforced by a system hard stop; Kamilisha only reminds.
- **Show the exact wording where it matters.** Control steps always show the circular's own words beside the plain version, so a summary or translation error is visible.
- **No individual monitoring.** The question log improves the library and training; it is never used to rate staff. This protects adoption.
- **Two new requirements** from this stage (switch-off and no individual reporting) were added to the Stage 3 backlog.

## Handover to Stage 6

Stage 6 builds a working prototype on the fictional library and shows each guardrail working in a five-scenario demo.
