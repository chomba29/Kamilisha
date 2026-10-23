# AI use-case record

The entry for the bank's register of approved AI use cases, with lessons learned for future use cases.

## Register entry

| Field | Entry |
| --- | --- |
| ID | UC-001 |
| Name | Kamilisha: branch procedure assistant |
| Business owner | Head of Branch Operations (fictional) |
| Delivery owner | Data Management Office |
| Purpose | Current procedure steps in plain English or Swahili, cited to the Live circular |
| Users | Branch staff; training unit (aggregated reports) |
| Risk level | Medium: staff-facing, advisory, no customer data, no decisions |
| Guardrails | 13 rules ([Stage 5](../05-guardrails/intended-use.md)) |
| Testing | UAT: [Stage 7](../07-test/) |
| Independent validation | Required before go-live; second line |
| Status | Simulated pilot complete; decision **adjust**: extend 4 weeks and add 2 pilot branches |
| KPIs | [Stage 4 definitions](../04-baseline/kpi-definitions.md); [pilot results](measure-summary.md) |
| Review date | End of the pilot extension |

## Decision log

| Date | Decision | By |
| --- | --- | --- |
| Stage 2 | AI limited to finding and reading procedures (P6, P7); six other pain points fixed without AI | Business owner |
| Stage 6 | Control completion added after live testing found a missing control step (DEF-001) | Data Management Office |
| Stage 7 | Procedure completion added after answer review found missing steps (DEF-003) | Data Management Office |
| Stage 7 | Reply limit raised after the retest found full answers cut off (DEF-007); full set rerun, all pass marks met | Data Management Office |
| Week 4 | Pilot 2 adoption actions, including stopping screenshot sharing | Branch manager |
| Week 8 | Adjust: quality and adoption met; QA reduction not yet established | Business owner |

## Lessons learned

1. **Triage first.** Six of eight problems needed no AI. Most of the value in the opportunities backlog is also non-AI.
2. **Search ranks by similarity, not importance.** A mandatory control step can fall outside the top results; completion rules must put controls in front of the model.
3. **Reading the answers catches what automatic checks miss.** UAT run 1 passed every automatic check, but review found a missing procedure step.
4. **Test what matters, strictly.** The first retrieval test passed any section from the right circular; it must check for the control section itself.
5. **Supervisors decide adoption.** Pilot 2 lagged until its supervisor stopped answering questions first.
6. **Look for unsafe workarounds.** Screenshots in a messaging group would have spread out-of-date answers.
7. **Comparison branches are essential.** Comparison branches also improved during the pilot; without them, the effect would have been overstated.
8. **Size the pilot for the effect you need to show.** Four weeks in two branches gave an interval from -61% to +18%: too wide to confirm a 40% reduction.
9. **Multilingual search is not optional in Tanzania.** Keyword search found 0 of 8 Swahili questions; semantic search found 7.
