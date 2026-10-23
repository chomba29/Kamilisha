# Intended use and guardrails

## Intended use

Kamilisha helps branch staff find and follow the current procedure. It answers questions about procedures and staff policies in short steps, in plain English or Swahili, from the bank's Live circulars, and shows where each answer comes from.

**It is an adviser, not a decision-maker.** The staff member stays responsible for every action, and the bank's systems enforce mandatory controls.

| | Intended | Not intended |
| --- | --- | --- |
| Users | Branch staff, teller to branch manager; training unit (aggregated reports only) | Customers; anyone outside the bank network |
| Questions | How to carry out a procedure; what a staff policy says | Whether to approve a specific customer, loan or exception |
| Sources | Live circulars in the Kamilisha library | General knowledge, the internet, old versions, colleagues' habits |
| Data | Questions about procedures | Customer names, account or card numbers, ID details |

## Guardrail rules

| ID | Rule | Requirement | Tested by |
| --- | --- | --- | --- |
| G-01 | Staff-facing only; never shown to or used directly with customers | NFR-02 | UAT access test |
| G-02 | Advises only: never approves, decides or carries out a transaction, and never phrases an answer as an approval | BR-01 | UAT, all answers |
| G-03 | Answers only from Live circulars, with circular, section, page and version cited | BR-02, BR-04 | US-01, US-02 |
| G-04 | If the library has no answer, replies only "Not found in the current circulars. Ask your supervisor." and never fills the gap from general knowledge | BR-05 | US-07 |
| G-05 | Declines questions about skipping or working around a control, restates the control with its citation, and logs the question for the procedure owner | BR-06 | US-08 |
| G-06 | Never asks for or stores customer personal data; reminds the user and masks it in the log | BR-07, NFR-05 | US-09 |
| G-07 | Control steps always show the circular's exact wording beside the plain-language version | BR-09 | US-01, US-04 |
| G-08 | Swahili answers keep the English source one click away; if they differ, the English source applies | BR-03 | US-03 |
| G-09 | Every answer has a "Wrong or unclear" button | BR-12 | US-10 |
| G-10 | A circular appears in Kamilisha only after its owner approves it; a superseded version is removed the day it is replaced | BR-04, NFR-03 | Library change log |
| G-11 | The Data Management Office can switch off one procedure, or the whole service, within one hour; staff fall back to the intranet | New | Switch-off drill before go-live |
| G-12 | The question log is used to improve the library and training, never to rate individual staff; reports show branch and procedure, not names | New | Report review |
| G-13 | Control completion: when search returns any section of a procedure, every mandatory-control section of that procedure is also given to the model, so a control step never depends on search ranking | BR-09 | Retrieval test (control given 15/15), offline tests |

G-11 and G-12 are new requirements from this stage, added to the [Stage 3 backlog](../03-define/backlog.csv) as enablers EN-04 and EN-05. G-13 was added after live prototype testing in Stage 6 (enabler EN-06).
