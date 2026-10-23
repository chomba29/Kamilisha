# Options note: how should staff reach the right answer fast?

**Problems addressed:** P6 (slow to find the section) and P7 (long, English, jargon-heavy circulars). These are the only two problems triage sent to AI, so this note tests whether AI is really needed for them.

**Precondition for every option:** the library fixes from P1 and P2 (one live version, a "What changed" box, named owners). Without them, every option below returns out-of-date answers faster.

## Options compared

| | A. Leave as is | B. Better intranet search | C. Quick-reference one-pagers | D. AI assistant with citations |
| --- | --- | --- | --- | --- |
| What it is | Staff search the intranet or ask a colleague | Better titles, tags, synonyms and section links | A one-page summary of the top procedures | Answers in the staff member's own words, in short steps, citing circular, section and version |
| Fixes P6 (finding) | No | Partly: still needs the right keywords and returns long documents | For the few procedures covered | Yes |
| Fixes P7 (reading) | No | No | Partly, English only | Yes, plain English or Swahili |
| Up-to-date answers | Depends on habit | Yes, once the library is clean | Risk: a second document to keep current | Yes, once the library is clean, and the version is shown |
| Feeds training data (P8) | No | Search logs only | No | Yes, every question logged |
| Relative cost | None | Low | Low to start, rising upkeep | Highest |
| Main risk | Errors continue | Staff still give up and ask colleagues | One-pagers drift from the circulars | A wrong or invented answer; managed by guardrails (Stage 5) |

## Recommendation

**Do the cheap fixes now, then pilot option D.**

1. **Now (weeks 1–4):** library clean-up and "What changed" box with acknowledgement tracking (P1, P2; huddle briefings added if acknowledgement stays low), documents checklist (P5), counter checklist for card replacement (P4 interim), QA returns dashboard (P3). These help on day one and are needed by every option.
2. **Next:** system hard stop for the card-blocking form (P4).
3. **Then:** pilot the AI assistant (D) on the three demo procedures, in two branches, measured against the Stage 4 baseline.

Option B is kept as the fallback: when the assistant cannot find an answer, it says so and links to the intranet search.

## Build or use what the bank already has

Requirements in Stage 3 are written tool-neutral, so the bank can choose how to deliver them: through a licensed tool such as Microsoft Copilot, or a purpose-built assistant. Stage 6 prototypes a purpose-built assistant to show the requirements can be met; the build-or-buy decision belongs to the bank's AI portfolio team.

## Decision needed

Approval of the recommendation from the business owner (Head of Branch Operations, fictional) before Stage 3 starts.
