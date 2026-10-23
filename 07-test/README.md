# Stage 7 — Test

**Question:** Does Kamilisha do what the business asked for, safely, before it reaches the pilot branches?

## Summary

User acceptance testing (UAT) against the [BRD](../03-define/brd.md) pass marks, in three parts: an automatic run of 34 scenarios through the live pipeline, review of every answer by the procedure owner, and a hands-on session with branch staff. Business sign-off is kept separate from independent validation by the second line.

## Deliverables

| File | What it shows |
| --- | --- |
| [uat-plan.md](uat-plan.md) | Scope, approach, scenarios, pass marks, entry and exit criteria, roles, defect rules, how to run |
| [uat-scenarios.csv](uat-scenarios.csv) | 35 scenarios (34 automatic, 1 manual), each tied to requirements and user stories, with expected results |
| [run_uat.py](run_uat.py) | Runs the scenarios through Pinecone and Claude, checks them, and writes timestamped results and a summary |
| [defect-log.csv](defect-log.csv) | Defects with severity, root cause, fix and retest; DEF-001 found in Stage 6 |
| [sign-off.md](sign-off.md) | Results against pass marks, pilot conditions, sign-off table |
| `results/` | One results file and one summary per run |

## Scenario mix

| Normal | Swahili | Outdated version | Missing facts | Control bypass | Not in library | Personal data | Switch-off | Feedback | Dashboard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 11 | 5 | 3 | 1 | 5 | 4 | 3 | 1 | 1 | 1 (manual) |

## Status

**Passed on run 3 (23 October 2026): all pass marks met.**

| Group | Pass mark | Run 1 (after review) | Run 3 (after review) | Result |
| --- | --- | --- | --- | --- |
| Answer quality | 95% | 18/20 (90%) | 20/20 (100%) | Met |
| Safety | 100% | 13/13 | 13/13 | Met |
| Features | 100% | 1/1 | 1/1 | Met |
| Superseded versions cited | 0 | 0 | 0 | Met |

- **Run 1:** every automatic check passed, but reading the answers found the lost-card steps for capture, fee and supervisor authorisation missing (DEF-003, S2).
- **Fix:** procedure completion gives Claude every procedure step of the best-matching circular.
- **Run 2:** the fuller answers ran past the reply limit and failed safe to "not found" (DEF-007, S2). Limit raised; cut-off replies now named in the log.
- **Run 3:** 34/34 automatic, 20/20 after review. DEF-001, 003 and 007 closed.
- **Open, not blocking (S3):** too many CONTROL badges (DEF-002), unrelated sections added on weak matches (DEF-004), honest yes/no questions declined (DEF-005), 6 of 34 answers over 10 seconds (DEF-006).
- **Before go-live:** native-speaker review of the Swahili answers, hands-on session with the UAT-11 dashboard check, business sign-off, independent validation.

Results: [run 3 summary](results/uat-summary-20261023-1958.md) · [run 3 answers](results/uat-results-20261023-1958.csv) · [run 2](results/uat-summary-20261023-1950.md) · [run 1](results/uat-summary-20261023-1914.md)

## Key judgements

- **Automatic checks are necessary but not enough.** They test the objective parts (status, citations, controls, masking). Whether the wording is right is judged by the procedure owner.
- **Safety cases must all pass.** One missed workaround or exposed account number fails UAT, however good the rest.
- **The defect found in Stage 6 was retested here and closed** (DEF-001: UAT-01 and UAT-03).
- **Human review earned its place:** every automatic check passed in run 1, but reading the answers found a missing step that would have reached the pilot.
- **Retest the whole set after a fix.** The DEF-003 fix caused a new failure (DEF-007) in answers that had passed before.
