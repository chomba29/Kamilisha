# Kamilisha

**A staff assistant that gives bank branch staff the current procedure in short steps, in plain English or Swahili, with the source circular, section and version cited underneath.**

*Kamilisha* is Swahili for "complete it". This portfolio project is run end to end the way an AI Business Analyst & Adoption team would deliver it: discovery first, AI only where a simpler fix won't do, and adoption measured against a baseline.

## The problem

Every branch circular, procedure and staff policy sits on the bank intranet, and it is kept up to date. The trouble is getting to it while a customer waits. Circulars run 20–50 pages, so staff ask a colleague instead. Changes are announced by email, and missed emails mean answers come from an old version or from habit (*kwa mazoea*).

The result is two officers giving the same customer different answers. When a control step is skipped, such as the signed card-blocking form, the error is caught by QA, months later by audit, or not at all: the lost card keeps transacting and the bank takes the loss.

## Who it is for

- **Branch staff**, from teller to branch manager: the answer in seconds, with the source to check.
- **Training unit**: a dashboard of what staff ask most, to target training where staff struggle.

## Results so far

- **Triage before AI:** of 8 pain points, only 2 needed AI; the other 6 get process fixes, system rules or reports ([Stage 2](02-triage/)).
- **Working prototype:** 12 fictional circulars (15 PDFs) fed to Pinecone; Claude answers only from the current versions, with citations ([Stage 6](06-prototype/)).
- **Swahili works:** semantic search found the right section for 7 of 8 Swahili questions, against 0 of 8 for keyword search.
- **A defect found and fixed:** live testing showed the blocking-form control could miss the top 5 search results; control completion now gets it to Claude every time (15 of 15).
- **UAT passed:** safety cases 13/13 (workarounds declined, data masked, honest "not found") and answer quality 20/20 against a 95% target. Reading the answers found missing steps that every automatic check had passed (DEF-003); the fix then cut off long answers (DEF-007); both were fixed and the full set retested ([Stage 7](07-test/)).
- **Simulated pilot measured honestly:** adoption 63% and answer quality 96.7% met their targets, but the QA-return reduction (-20% against comparison branches) was not yet clear of zero, so the decision is ADJUST: extend 4 weeks, not GO ([Stage 9](09-measure/)).

## How the project runs

| Stage | Question it answers | Status |
| --- | --- | --- |
| [1. Discover](01-discover/) | What do staff look up, how do they find it, and where does it go wrong? | Done |
| [2. Triage](02-triage/) | Which problems need a process fix, a rule, a report, or AI? | Done |
| [3. Define](03-define/) | What exactly must the solution do, and how will we know? | Done |
| [4. Baseline](04-baseline/) | How slow and error-prone is it today, in numbers? | Done |
| [5. Guardrails](05-guardrails/) | What must it never do, and who reviews what? | Done |
| [6. Prototype](06-prototype/) | Does a working version answer correctly, with citations? | Done |
| [7. Test](07-test/) | Does it pass user acceptance tests, including refusals? | Done: all pass marks met (run 3) |
| [8. Adopt](08-adopt/) | How do staff learn it, and who champions it? | Done |
| [9. Measure](09-measure/) | Is it used, is it right, and is the benefit real? | Done (simulated pilot) |

## Ground rules

- **Fictional bank, fictional circulars, synthetic data.** No real bank documents or customer data. Not affiliated with or endorsed by any bank.
- **Evidence** comes from a practitioner interview: nine years in branch banking across operations, credit, relationship management and acting branch leadership.
- **Benefit evidence is reported separately** from forecasts, training attendance and licence counts.

## Repository

```
01-discover/   procedure inventory, pain-point log, discovery notes, BPMN process maps
02-triage/     triage matrix, options note
03-define/     use-case intake, BRD, user journeys, user stories, backlog, traceability, data requirements
04-baseline/   KPI definitions, synthetic baseline data, benefits case, assumptions register
05-guardrails/ intended use, guardrail rules, oversight and escalation, risk register, AI factsheet
06-prototype/  fictional circular library, RAG assistant (Pinecone search + Claude), guardrail and retrieval tests, demo script
07-test/       UAT plan, 35 scenarios, UAT runner, defect log, sign-off
08-adopt/      change impact, stakeholders, comms, champions, training, Copilot prompt sheet, pilot plan, status report
09-measure/    simulated 8-week pilot, measurement against the baseline, dashboard, adoption review, opportunities backlog, use-case record
```

---

Author: Elizabeth Julius Chomba · Dar es Salaam, Tanzania · Earlier working title: *My Compliance Buddy*
