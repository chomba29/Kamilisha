# Stage 1 — Discover

**Question:** What do branch staff look up, how do they find it today, and where does it go wrong?

## Key findings

1. **The information exists and is current; access is the problem.** Circulars run 20–50 pages, so staff ask a colleague instead of reading (P6, P7).
2. **Updates get missed.** Changes are announced by email only, so colleagues answer from an old version or from habit, *kwa mazoea* (P1, P2).
3. **Card replacement and account opening cause the most confusion,** because their requirements change most often (P4, P5).
4. **Skipped controls cost money.** A skipped card-blocking form is caught by QA, later by audit, or not at all, and the lost card transacts (P3, P4).
5. **Nobody can see where staff struggle,** so training is generic rather than targeted (P8).

## Deliverables

| File | What it shows |
| --- | --- |
| [procedure-inventory.csv](procedure-inventory.csv) | 12 procedures and policies across 5 areas, with owner, frequency, control risk, and the 3 chosen for the first demo |
| [pain-point-log.md](pain-point-log.md) | 8 pain points (P1–P8), each with its effect, the control at risk, frequency and severity |
| [discovery-notes.md](discovery-notes.md) | Interview method, findings, decisions agreed, and assumptions still to confirm |
| [Map 1 — Procedure lookup](process-maps/map-1-as-is-procedure-lookup.svg) | How staff find a procedure today, and where wrong answers enter |
| [Map 2 — Card replacement](process-maps/map-2-as-is-card-replacement.svg) | Four control steps, and the habit path that skips the blocking form |
| [Map 3 — Business account opening](process-maps/map-3-as-is-account-opening.svg) | The documents check where branches disagree |

Each map comes as `.svg` (view on GitHub), `.png` (slides and documents) and `.bpmn` (open and edit in [bpmn.io](https://demo.bpmn.io)). All three formats are generated from one definition in [build_maps.py](process-maps/build_maps.py), so they always match.

## Why these three procedures for the first demo

- **Card replacement:** high frequency, changes often, and a skipped step leads directly to fraud loss.
- **Business account opening:** high frequency, changes often, and inconsistent document lists cause repeat visits and QA returns.
- **Staff leave policy:** shows Kamilisha serves every staff member, not only customer-facing work.

## Method

Semi-structured practitioner interview, one question at a time. Process mapping in BPMN 2.0, with lanes per role and control steps marked. Each pain point logged with its effect and the control it puts at risk.

**Limit:** the evidence comes from one practitioner. Stage 7 user testing and the Stage 8 pilot test the findings with more users.

## Handover to Stage 2

P1–P8 go into the triage matrix, which decides for each one whether the right fix is a process change, a mandatory rule or checklist, a report, or AI.
