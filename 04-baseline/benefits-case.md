# Benefits case

Computed by `benefits_model.py` from the baseline data and the [assumptions register](assumptions-register.csv). Do not edit by hand; change an assumption and rerun. Amounts in Tanzanian shillings (TZS), fictional bank, network-wide, for the three pilot procedures only.

## 1. Evidence: what the baseline measured

These are observations (synthetic for this portfolio), not forecasts.

| Measure | Baseline (4 branches, 8 weeks) |
| --- | --- |
| Requests handled | 880 |
| Requests needing a lookup | 603 (69%) |
| Mean minutes per lookup (timed sample, n=112) | 6.1 |
| QA returns | 164 |
| QA returns caused by outdated answers (excess over the current-answer rate) | 96 |
| Extra customer trips, business accounts | 36 |
| Lost cards that transacted | 2 (too rare to measure in 8 weeks) |

## 2. Forecast: expected benefits per year after rollout

Most of the benefit is **staff time released**, not cash saved. It is shown in hours first; TZS is for comparison only.

| | Cautious | Expected | Optimistic |
| --- | --- | --- | --- |
| Staff hours saved on lookups | 1,935 | 4,812 | 7,044 |
| Staff hours saved on QA rework | 1,123 | 5,392 | 10,784 |
| **Total hours released** | **3,058** | **10,204** | **17,828** |
| Equivalent full-time staff | 1.5 | 5.1 | 8.9 |
| Value of time at staff cost (TZS) | 46M | 153M | 267M |
| Customer trips avoided (not valued) | 844 | 2,700 | 4,050 |

## 3. Costs (TZS)

| | Cautious | Expected | Optimistic |
| --- | --- | --- | --- |
| Year one: clean-up, build or licence, running, training, support | 174M | 108M | 69M |
| Each later year: running and support | 70M | 40M | 22M |

## 4. Net view (TZS)

| | Cautious | Expected | Optimistic |
| --- | --- | --- | --- |
| Year one | -129M | 45M | 198M |
| Each later year | -24M | 113M | 245M |

In the expected case the value of time released (153M) covers year-one costs (108M).

**Which assumption matters most?** Each row moves one assumption to its cautious value and keeps the rest at expected.

| Assumption moved to cautious | Cautious value | Year-one net (TZS) |
| --- | --- | --- |
| A06 Share of lookups made through Kamilisha once rolled out | 30% | -32M |
| A08 Cut in outdated answers among Kamilisha users | 50% | 15M |
| C02 Build or licence in year one | 90M | 15M |
| A05 Staff time to rework one QA return (branch and back office) | 30 minutes | 18M |
| C03 Running cost per year (hosting and licences) | 40M | 30M |
| C05 Ongoing support and library upkeep | 1 full-time staff | 30M |
| A07 Minutes to an answer with Kamilisha | 2 minutes | 31M |

A06 is the biggest driver: at its cautious value year one does not pay back. The pilot must prove it before rollout.

## 5. Not counted, on purpose

- **Fraud loss avoided:** credited to the system hard stop for the blocking form (Stage 2, P4), not to Kamilisha (A10 = 0%). Counting it twice would overstate the case.
- **Other procedures:** only three procedures are modelled. Adding more raises benefits with little extra cost; treated as upside, not forecast.
- **Audit queries:** too slow to move in a pilot; tracked for two quarters after rollout.

## 6. How the benefit will be evidenced

Stage 9 measures the change in pilot branches against the change in comparison branches over the same weeks. Only that difference is reported as benefit evidence. Forecasts, training attendance and licence counts are reported separately and never as benefit.
