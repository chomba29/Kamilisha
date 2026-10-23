# Pilot plan

## Design

| | |
| --- | --- |
| Branches | 2 pilot branches use Kamilisha; 2 comparison branches carry on as today (same as the Stage 4 baseline) |
| Length | 8 weeks |
| Procedures | All 12 Live circulars in the library; card replacement, business account opening and annual leave are the focus |
| Users | All staff in the pilot branches (about 6 officers each handle the focus procedures) |
| Measure | Change in pilot branches minus change in comparison branches, on the [Stage 4 KPIs](../04-baseline/kpi-definitions.md) |

## Before go-live (entry conditions)

- [x] DEF-003 fixed and the full UAT set rerun (run 3: all pass marks met)
- [ ] [UAT sign-off](../07-test/sign-off.md) by the business owner
- [ ] Swahili answers checked by a native-speaking reviewer
- [ ] Independent validation by the second line complete
- [ ] IT security approval for the outside services, or bank-hosted replacements (risk R12)
- [ ] Library clean-up done for the pilot circulars (Stage 2, P1 and P2)
- [ ] Blocking-form hard stop live, or the counter checklist in place (Stage 2, P4)
- [ ] Champions named and trained; all pilot staff trained
- [ ] Switch-off drill done (G-11)

## Timeline

| Week | Focus | Check-in |
| --- | --- | --- |
| -2 to 0 | Announce, train, champions ready | Entry conditions met |
| 1 to 2 | Go-live and early support | Daily: errors, "Wrong or unclear", switch-off readiness |
| 3 to 4 | Settle in; fix library gaps from "Not found" | Week 4 adoption review |
| 5 to 8 | Measure | Weekly KPIs |
| 8 | Results and decision | Pilot review meeting |

## Go, adjust or stop at week 8

| Decision | When |
| --- | --- |
| **Go** (extend to more branches) | Adoption (K7) at least 60%; answer quality (K9) at least 95%; QA return rate (K3) down at least 40% against comparison branches; no S1 incident open |
| **Adjust** (extend the pilot 4 weeks) | Quality met but adoption or QA improvement below target, with a clear reason and fix |
| **Stop** | Any unresolved S1 incident, quality below 90%, or adoption below 30% (the level where the benefits case does not pay back) |

## Stop at any time

An S1 incident (wrong answer on a control step, or customer data exposed) switches the affected procedure off within one hour, as in [oversight and escalation](../05-guardrails/oversight-and-escalation.md).
