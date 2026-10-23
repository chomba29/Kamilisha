# Stage 3 — Define

**Question:** What exactly must the solution do, and how will we know it works?

## Summary

The AI scope from Stage 2 is turned into **13 business requirements**, **11 user stories** with Given/When/Then acceptance criteria, and a **prioritised backlog** of 17 items. Every requirement traces back to a Stage 1 pain point and forward to a planned user acceptance test.

Requirements are **tool-neutral**: the bank can meet them with a licensed tool such as Microsoft Copilot, or a purpose-built assistant.

## Deliverables

| File | What it shows |
| --- | --- |
| [use-case-intake.md](use-case-intake.md) | One-page case for the use case: owner, users, scope, why AI, risks, decision requested |
| [brd.md](brd.md) | Business requirements (BR-01 to BR-13), non-functional requirements, UAT thresholds, dependencies, sign-off |
| [user-journeys.md](user-journeys.md) | Three staff members, today and with Kamilisha |
| [user-stories.md](user-stories.md) | US-01 to US-11, each with Given/When/Then acceptance criteria |
| [backlog.csv](backlog.csv) | 6 enablers and 11 stories, ranked, with MoSCoW priority, size and dependencies (EN-04 and EN-05 added in Stage 5, EN-06 in Stage 6) |
| [traceability.csv](traceability.csv) | Pain point → requirement → story → acceptance criteria → planned UAT test |
| [data-requirements.md](data-requirements.md) | Library metadata, the fictional demo library, question-log fields, owners, access and quality gaps |

## Key decisions

- **Must-haves are the safety ones.** Current version only, honest "not found", declining control workarounds and keeping customer data out are all Must; the training dashboard is Should.
- **UAT pass mark is set now, before building:** at least 95% correct answers with correct citations, and 100% on not-found, control-bypass and personal-data cases.
- **Data quality comes first.** Five library gaps must be fixed before go-live, starting with marking old versions Superseded.

## Handover to Stage 4

Stage 4 measures today's baseline for the success measures (QA returns, time to a correct answer, audit queries) and confirms the proposed 10-second response target.
