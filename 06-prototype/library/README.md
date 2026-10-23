# Mfano Bank circular library (fictional)

Fifteen intranet-style PDFs for a fictional bank: twelve procedures and policies, with an old (Superseded) and a current (Live) version of the three demo procedures. Each PDF has a cover page, document control with a "what changed" box, a contents page, definitions, roles, the procedure with mandatory controls marked, exceptions, records, monitoring, related documents, appendices and FAQs.

| Area | Circular | Live version | Old version kept |
| --- | --- | --- | --- |
| Cards | CIR-CARD-07 Card replacement | v2, 1 Sep 2026 | v1 (no blocking form) |
| Cards | CIR-CARD-05 New card issuance | v3 | |
| Onboarding | CIR-ACC-10 Individual account opening and KYC | v4 | |
| Onboarding | CIR-ACC-12 Business account opening | v2, 15 Aug 2026 | v1 (licence for all) |
| Onboarding | CIR-ACC-15 Customer information update | v2 | |
| Digital channels | CIR-DIG-03 SIM banking enrolment | v2 | |
| Digital channels | CIR-DIG-04 Internet banking enrolment and PIN reset | v1 | |
| Lending | CIR-CRD-21 Loan origination checklist | v3 | |
| Lending | CIR-CRD-22 Collateral documentation | v2 | |
| Staff affairs | HR-POL-01 Staff code of conduct | v3 | |
| Staff affairs | HR-POL-03 Annual leave | v2, 1 Mar 2026 | v1 (14 days' notice) |
| Staff affairs | HR-POL-07 Salary advance and staff loans | v2 | |

| Path | What it is |
| --- | --- |
| `source/` | The text of each circular (one file per version), written by the procedure owner |
| `build_library.py` | Turns the sources into PDFs and writes the register |
| `pdf/` | The 15 PDFs, 92 pages in total |
| `register.csv` | The document register: version, status, effective date, owner, file and pages. Kamilisha uses it to know which version is Live |

To change a circular: edit its source file, run `python library/build_library.py`, then `python app/sync_index.py` to refresh Pinecone.

All content is fictional and does not describe any real bank's procedures.
