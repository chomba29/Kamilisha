# Use-case intake: Kamilisha

| Field | Entry |
| --- | --- |
| Use case | Staff assistant that answers branch procedure and staff policy questions from the current circulars |
| Business owner | Head of Branch Operations (fictional) |
| Requested by | Branch network, through the Data Management Office |
| Users | All branch staff, teller to branch manager; training unit (second user) |
| Problem | Staff cannot find or read the current procedure fast enough, so they answer from habit; skipped controls lead to QA returns, audit queries and fraud loss ([Stage 1](../01-discover/)) |
| Why AI | Triage sent only P6 (finding the section) and P7 (reading English jargon) to AI; the other six problems get process fixes, rules and reports ([Stage 2](../02-triage/)) |
| Preconditions | One version-controlled library with named owners (P1, P2) before go-live |
| In scope (pilot) | Three procedures: card replacement, business account opening, annual leave. Two branches. English and Swahili |
| Out of scope | Approving, deciding or executing any transaction; customer-facing use; customer personal data; procedures outside the library |
| Expected benefits | Fewer QA returns, shorter time to a correct answer, fewer audit queries. Baselines and targets set in Stage 4 |
| Main risks | Wrong or invented answer; outdated source; personal data typed in; staff over-trusting answers. Controls in Stage 5 |
| Data | Circulars with version metadata; question log without customer data ([data requirements](data-requirements.md)) |
| Decision requested | Approve requirements and pilot scope; proceed to baseline (Stage 4) |
