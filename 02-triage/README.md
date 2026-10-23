# Stage 2 — Triage

**Question:** Which problems need a process fix, a rule, a report, or AI?

Each Stage 1 pain point was given the cheapest fix that solves its root cause. AI was allowed only where the simpler fixes fall short.

## Result

| ID | Pain point | Fix type | Fix in one line |
| --- | --- | --- | --- |
| P1 | Update emails are missed | Process fix | "What changed" box on every circular; backup plan if staff skip it (below) |
| P2 | No quick way to tell which version is current | Process fix | One version-controlled library with named owners |
| P3 | Errors are found late | Report | Weekly QA returns dashboard by procedure and branch |
| P4 | Card-blocking form skipped | Rule or checklist | System will not capture a replacement until the signed form is scanned |
| P5 | Documents list applied inconsistently | Rule or checklist | One-page documents checklist per entity type |
| P6 | Slow to find the right section | **AI** | Assistant answers in short steps, citing circular, section and version |
| P7 | Long, English, jargon-heavy circulars | **AI** | Same assistant answers in plain English or Swahili |
| P8 | Training unit cannot see where staff struggle | Report | Most-asked questions dashboard from the question log |

**Two of the eight problems need AI.** The other six are solved more cheaply and more reliably with process changes, system rules and reports, and the AI depends on two of them (P1, P2) being done first.

## P1 planned for two scenarios

Whether staff will read a "What changed" box is not yet known, so both outcomes are planned for.

| | Scenario A: staff read it | Scenario B: staff skip it |
| --- | --- | --- |
| Sign | Acknowledgement rate meets target within 30 days | Acknowledgement rate stays below target after 30 days |
| Fix | "What changed" box plus tick-to-acknowledge for control changes | Also push the change to the point of use: morning huddle briefing by the branch manager, and the assistant flags "changed on [date]" on any answer that uses it |
| Cost | Low | Low; the flag reuses the version data the assistant already holds |

The target rate is set with the business owner in Stage 4, once the baseline is known.

## Deliverables

| File | What it shows |
| --- | --- |
| [triage-matrix.csv](triage-matrix.csv) | All eight pain points with root cause, fix type, proposed fix, why not AI, owner, effort and impact |
| [options-note.md](options-note.md) | Four ways to fix P6 and P7 compared; recommendation and sequence |

## Key judgements

- **Controls go in the system, not the assistant.** A mandatory step like the blocking form (P4) must be enforced by a hard stop. An assistant can remind; it cannot enforce.
- **Fix the library before adding AI.** An assistant reading a messy library gives wrong answers faster (P1, P2).
- **Training data is a by-product.** The question log that serves the training unit (P8) comes free with the assistant.

## Handover to Stage 3

The AI scope is now fixed: answer procedure questions (P6) in plain English or Swahili (P7), cite the version (P2), flag recently changed steps (P1, Scenario B), and log every question (P8). Stage 3 turns this into a use-case intake, requirements and acceptance criteria.
