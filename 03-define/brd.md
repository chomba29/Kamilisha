# Business requirements document (BRD): Kamilisha

**Version:** 1.0 draft for business-owner review · **Business owner:** Head of Branch Operations (fictional)

## 1. Purpose

Give branch staff the current procedure in seconds, in short steps they can follow at the counter, so that control steps are not skipped and two officers give a customer the same answer.

## 2. Scope

**Pilot:** card replacement, business account opening, annual leave; two branches; English and Swahili.
**Not in scope:** decisions or approvals, transactions, customer-facing use, customer personal data.

## 3. Stakeholders

| Role | Interest |
| --- | --- |
| Branch staff (teller to branch manager) | Fast, correct answers they can trust |
| Training unit | Visibility of what staff ask most |
| Procedure owners (Cards, Operations, HR) | Their circulars applied as written; feedback on unclear sections |
| Compliance and Risk | Controls preserved; no personal data exposure |
| Back office QA | Fewer returns |
| Data Management Office | Delivery, data quality, adoption |

## 4. Business requirements

All requirements are tool-neutral: they can be met by a licensed tool or a purpose-built assistant.

| ID | Requirement | Pain point | Priority |
| --- | --- | --- | --- |
| BR-01 | Answer a procedure question in short numbered steps | P6 | Must |
| BR-02 | Cite circular, section, page and version under every answer | P2, P6 | Must |
| BR-03 | Answer in plain English or Swahili, matching the question's language | P7 | Must |
| BR-04 | Use only circulars marked Live; never answer from a superseded version | P2 | Must |
| BR-05 | When the library has no answer, reply only: "Not found in the current circulars. Ask your supervisor." | P6 | Must |
| BR-06 | Decline questions on skipping or working around a control; restate the control; log it for the procedure owner | P4 | Must |
| BR-07 | Never ask for or store customer personal data; mask it in the log if typed | — | Must |
| BR-08 | Log every question with its outcome (answered, not found, declined) | P8 | Must |
| BR-09 | Mark control steps clearly in every answer | P4, P5 | Should |
| BR-10 | Flag steps changed recently with "changed on [date]" | P1 | Should |
| BR-11 | Ask for missing facts (such as entity type) before answering | P5 | Should |
| BR-12 | "Wrong or unclear" button that sends the question and answer to the procedure owner | P2, P7 | Should |
| BR-13 | Most-asked questions dashboard for the training unit, by procedure and branch | P8 | Should |

## 5. Non-functional requirements

| ID | Requirement |
| --- | --- |
| NFR-01 | Answer appears in under 10 seconds (proposed; confirmed against the Stage 4 baseline) |
| NFR-02 | Staff sign in with their bank login; no access outside the bank network |
| NFR-03 | A new or changed circular is reflected within one working day of going Live |
| NFR-04 | Question log kept per the bank's records-retention policy |
| NFR-05 | Customer personal data handled in line with Tanzania's Personal Data Protection Act, 2022 |

## 6. Acceptance thresholds for UAT (proposed, agreed at sign-off)

- Correct answer with correct citation in at least 95% of in-library test questions.
- 100% of not-found, control-bypass and personal-data test cases handled as specified.
- No answer drawn from a superseded version.

## 7. Assumptions, constraints, dependencies

- **Dependency:** the library fixes from Stage 2 (P1, P2) are in place before go-live.
- **Constraint:** the assistant advises only; system rules enforce controls (Stage 2, P4).
- **Assumption:** branch PCs can reach the tool; mobile use is out of scope for the pilot.

## 8. Sign-off

| Role | Decision | Date |
| --- | --- | --- |
| Business owner | Pending | |
| Compliance | Pending | |
| Data Management Office | Pending | |
