# UAT sign-off: Kamilisha pilot

**Status: all UAT pass marks met (run 3, 23 October 2026). Ready for business sign-off.**

## Results

Run 3: 23 October 2026, Pinecone search and Claude Sonnet 5.5, 34 automatic scenarios. Every answer reviewed by the BA on behalf of the procedure owners; Swahili wording to be confirmed by a native-speaking owner. Details: [run 3 summary](results/uat-summary-20261023-1958.md).

| Criterion | Pass mark | Result | Met? |
| --- | --- | --- | --- |
| Answer quality | At least 95% | 20/20 (100%) after review | Yes |
| Safety: control bypass, not in library, personal data, switch-off | 100% | 13/13 | Yes |
| Features: "Wrong or unclear" feedback | 100% | 1/1 | Yes |
| Superseded versions cited | None | 0 | Yes |
| Open S1 defects | None | None (DEF-001 closed) | Yes |
| Open S2 defects | None, or agreed fix date and workaround | None (DEF-003 and DEF-007 closed) | Yes |
| Open S3 defects | Fix agreed, not blocking | DEF-002, 004, 005, 006: fixes agreed for the pilot release | Yes |
| Hands-on session feedback | No blocking issues | Held at the champion session before go-live, with the UAT-11 dashboard check | Pilot entry condition |

## How the runs went

| Run | Time | Result | What it found |
| --- | --- | --- | --- |
| 1 | 19:14 | Answer quality 18/20 after review | Lost-card answers missing capture, fee and authorisation (DEF-003) |
| 2 | 19:50 | 31/34 automatic | The DEF-003 fix made full answers too long for the reply limit (DEF-007) |
| 3 | 19:58 | 34/34; 20/20 after review | Both fixed. Pass marks met |

## Conditions for the pilot

- Library clean-up from Stage 2 (P1, P2) complete for the pilot procedures.
- System hard stop for the blocking form (Stage 2, P4) in place, or the counter checklist as interim control.
- Independent validation by the second line completed (see the [UAT plan](uat-plan.md), section 8).
- Full scenario set rerun after any change to the model, prompt or library.

## Decision

| Role | Name | Decision | Date |
| --- | --- | --- | --- |
| Business owner: Head of Branch Operations (fictional) | | Accept / Accept with conditions / Reject | |
| Compliance | | | |
| Data Management Office | | | |
| AI Business Analyst (UAT coordinator) | | | |

Signatures are left blank: the bank and its people are fictional. Business sign-off confirms the business accepts Kamilisha for the pilot. It is not a substitute for independent validation.
