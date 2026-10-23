# Data requirements

## 1. Procedure library (what the assistant reads)

Every circular is stored by section, with this metadata:

| Field | Example | Why it is needed |
| --- | --- | --- |
| Circular ID | CIR-CARD-07 | Citation (BR-02) |
| Title | Card replacement | Citation |
| Version | v2 | Citation; current-version rule (BR-04) |
| Status | Live or Superseded | Only Live is used (BR-04) |
| Effective date | 2026-09-01 | "Changed on" flag (BR-10) |
| Owner (role) | Cards and Payments | Feedback routing (BR-12) |
| Section and page | Section 3, page 4 | Citation |
| Control step flag | Yes / No | CONTROL marking (BR-09) |
| Language | English (source) | Swahili is generated at answer time, with the English source one click away |

**Recently changed** means an effective date within the last 90 days (proposed; confirmed with procedure owners).

## 2. Demo library (fictional)

| Circular | v1 (Superseded) | v2 (Live) | Effective date of v2 |
| --- | --- | --- | --- |
| CIR-CARD-07 Card replacement | Block on the system; no form needed | Signed card-blocking form first, then block | 1 Sep 2026 |
| CIR-ACC-12 Business account opening | Business licence for every business account | Sole proprietors may give a tax registration certificate instead | 15 Aug 2026 |
| HR-POL-03 Annual leave | 14 days' notice | 7 days' notice | 1 Mar 2026 |

## 3. Question log (what the assistant records)

| Field | Notes |
| --- | --- |
| Timestamp, branch, role | No staff names in reports; staff ID kept for access audit only |
| Language | English or Swahili |
| Question text | Customer names, account and card numbers masked before saving (BR-07) |
| Outcome | Answered, Not found, Declined |
| Circulars cited | ID, version, section |
| Feedback | "Wrong or unclear" pressed: yes or no |

## 4. Owners and access

| Data | Owner | Who can see it |
| --- | --- | --- |
| Circulars | Each procedure owner | All staff |
| Question log | Data Management Office | Data Management Office; training unit sees aggregated counts only |
| Feedback queue | Each procedure owner | That owner and the Data Management Office |

## 5. Known quality gaps to fix before go-live

| Gap | Effect if not fixed | Fix |
| --- | --- | --- |
| Old versions not marked Superseded | Assistant may quote the old rule | Library clean-up (Stage 2, P2) |
| Circulars without an effective date | "Changed on" flag cannot work | Owners add dates |
| Inconsistent section numbering | Citations point to the wrong place | Standard section template |
| Scanned PDFs without text | Content cannot be read | Re-issue as text documents |
| Control steps not labelled | CONTROL marking missing | Owners tag control steps |
