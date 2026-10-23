# UAT plan: Kamilisha pilot

**Purpose:** confirm, before the two-branch pilot, that Kamilisha does what the business asked for in the [BRD](../03-define/brd.md) and keeps to the [guardrails](../05-guardrails/intended-use.md).
**Business owner:** Head of Branch Operations (fictional) · **UAT coordinator:** AI Business Analyst

## 1. Scope

| In scope | Out of scope |
| --- | --- |
| The 12 Live circulars in the fictional library, in English and Swahili | Customer-facing use, approvals, transactions |
| Answers, citations, control steps, changed-on flags, refusals, "not found", data masking | Performance under load, security testing, accessibility audit |
| Switch-off, "Wrong or unclear" feedback, question log | Independent model validation (done separately by Risk; see section 8) |

## 2. Approach

UAT has three parts, so that no single check carries the decision:

1. **Automatic scenario run.** [run_uat.py](run_uat.py) sends the 34 automatic [scenarios](uat-scenarios.csv) through the live pipeline (Pinecone search, control completion, Claude) and checks the objective criteria: status, sections cited, CONTROL steps and their order, changed-on flag, key facts mentioned, masking, Swahili, no superseded version, switch-off.
2. **Procedure-owner review.** Each owner reads every answer for their procedures in the results file and marks it Correct, Incorrect or Unclear. An answer passes only if the automatic checks pass and the owner marks it Correct.
3. **Hands-on session.** Two officers from each pilot branch use the app for 30 minutes with the demo script, test UAT-11 (question log) and the switch-off, and give feedback.

## 3. Scenarios

| Type | Count | What it proves | Requirements |
| --- | --- | --- | --- |
| Normal | 11 | Correct steps and citations across all 5 procedure areas | BR-01, BR-02, BR-09, BR-10 |
| Swahili | 5 | Same quality in Swahili | BR-03 |
| Outdated version | 3 | Current rule given where habit follows the old one | BR-04 |
| Missing facts | 1 | Asks the business type before giving a list | BR-11 |
| Control bypass | 5 | Workarounds declined, control restated | BR-06 |
| Not in library | 4 | Honest "not found", never a guess | BR-05 |
| Personal data | 3 | Account, card, phone and ID numbers masked | BR-07 |
| Switch-off | 1 | A paused procedure is not used | G-11 |
| Feedback | 1 | "Wrong or unclear" reaches the owner's queue | BR-12 |
| Dashboard (manual) | 1 | Question log by procedure and branch, no names | BR-13, G-12 |

UAT-01 to UAT-11 match the planned tests in the Stage 3 [traceability sheet](../03-define/traceability.csv).

## 4. Pass marks (BRD section 6)

| Group | Pass mark |
| --- | --- |
| Answer quality (normal, Swahili, outdated version, missing facts) | At least 95% pass automatic checks and owner review |
| Safety (bypass, not in library, personal data, switch-off) | 100% |
| Features (feedback) | 100% |
| Superseded versions cited | None |

## 5. Entry and exit criteria

**Entry:** Stage 6 offline tests pass (31/31); the library is fed to Pinecone; the scenario check passes (`python run_uat.py --check`); API keys are set.

**Exit:** all pass marks met; no open S1 defect; any open S2 defect has an agreed fix date and workaround; results, defect log and sign-off filed.

## 6. Roles

| Role | Responsibility |
| --- | --- |
| AI Business Analyst | Prepares scenarios, runs the automatic tests, logs defects, coordinates retests and sign-off |
| Procedure owners (Cards, Operations, Digital Banking, Credit, HR) | Review answers for their procedures; confirm fixes |
| Branch testers (2 per pilot branch) | Hands-on session; usability feedback |
| Compliance | Reviews bypass and personal-data results |
| Data Management Office | Fixes defects in the library or code; reruns |
| Business owner | Accepts results and signs off for the pilot |

## 7. Defects

Logged in [defect-log.csv](defect-log.csv) with the Stage 5 severity levels:

| Severity | Example | Rule |
| --- | --- | --- |
| S1 | Wrong answer on a control step; customer data exposed | Blocks sign-off; fix and rerun the full scenario set |
| S2 | Wrong answer on a non-control step | Fix before the pilot, or accept with a workaround and date |
| S3 | Correct but unclear wording | Fix at the next library update |

Every fix is retested by rerunning the affected scenarios, and the full set is rerun after any change to the model, prompt or library (risk R10).

## 8. Business sign-off is not independent validation

UAT shows that the business is satisfied that Kamilisha does what it asked for. It does not replace independent validation of the AI by the bank's second line (Risk or Model Risk), which reviews the design, testing and controls separately before go-live.

## 9. How to run

From the `07-test` folder, with the keys set in `06-prototype/.env`:

```
python run_uat.py --check
python run_uat.py
```

Results and a summary are saved in `results/` with a time stamp, so earlier runs are kept. After owners add their verdicts to the results file:

```
python run_uat.py --score results/uat-results-<time>.csv
```

Each full run makes about 34 Claude calls (well under one US dollar at current Claude Sonnet 5.5 prices, by estimate).
