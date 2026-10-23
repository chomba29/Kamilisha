# Pilot measurement summary

> **Simulated pilot.** All figures come from synthetic data for a fictional bank (`generate_pilot_data.py`). They show how the pilot would be measured and reported; they are not real results.

**Decision against the pilot plan: ADJUST: extend the pilot 4 weeks.**

| Go rule | Result | Met |
| --- | --- | --- |
| Adoption (K7) at least 60% in week 8 | 63% | Yes |
| Answer quality (K9) at least 95% | 96.7% | Yes |
| QA returns (K3) down at least 40% against comparison | -20% | No |
| No open S1 incident | None | Yes |

## 1. Benefit evidence: business outcomes (difference-in-differences, weeks 5 to 8)

Change in the pilot branches minus the change in the comparison branches over the same weeks.

K3 estimate -20% with a 95% bootstrap interval of -61% to +18%: the interval includes zero, so the reduction is not yet established.

| KPI | Pilot before | Pilot after | Comparison before | Comparison after | Pilot minus comparison | Target | Met |
| --- | --- | --- | --- | --- | --- | --- | --- |
| K3 QA return rate, three procedures | 19.2% | 12.1% | 18.0% | 14.8% | -20% relative | 40% lower | No |
| K3a QA return rate, card replacement | 20.4% | 12.3% | 20.0% | 17.0% | -25% relative | 50% lower | No |
| K4 Blocking form on file | 75.7% | 86.0% | 76.6% | 81.0% | +5.9 points | At least 95% | No |
| K1 Median minutes to an answer (lookups) | 4.7 | 1.2 | 5.0 | 4.4 | -2.85 | 1.5 or less | Yes |
| K2 Colleague questions per officer per day | 0.44 | 0.20 | 0.42 | 0.37 | -42% relative | 50% lower | No |
| K6 Staff confidence (1 to 5) | 2.60 | 3.00 | 3.15 | 3.40 | +0.15 | Up 0.8 points | No |

**Measured value in the two pilot branches, weeks 5 to 8:**

| Measure | Value |
| --- | --- |
| QA return rate expected without Kamilisha (pilot baseline with the comparison trend) | 15.8% |
| QA return rate measured | 12.1% |
| QA returns avoided | 10 |
| Staff hours saved on rework (at 45 minutes each) | 7 |
| Lookups made through Kamilisha | 101 |
| Minutes saved per lookup (against colleague or intranet lookups in comparison branches) | 6.0 |
| Staff hours saved on lookups | 10 |
| **Total staff hours released (4 weeks, 2 branches)** | **17** |
| Value at staff cost (TZS) | 0.3M |
| Extra customer trips, business accounts: pilot / comparison | 6 / 6 |
| Lost cards that transacted in pilot branches | 1 (too rare to measure; not claimed) |

## 2. Adoption and quality

| KPI | Result | Target | Met |
| --- | --- | --- | --- |
| K7 Adoption, week 8 (both pilot branches) | 63% | 60% | Yes |
| K7 Adoption, week 8: Pilot 1 / Pilot 2 | 58% / 67% | 60% | |
| K8 Active users, week 8: Pilot 1 / Pilot 2 | 100% / 92% | 70% | Yes |
| K9 Answer quality (owner review of 61 answers) | 96.7% | 95% | Yes |
| K9 by language: English / Swahili | 94.6% / 100.0% | 95% each | No |
| K10 Wrong or unclear rate | 5.0% | 5% or less | Yes |
| K11 Not found rate | 14.3% | Tracked | |
| Questions in Swahili | 36% of 336 | Tracked | |
| Declined workaround questions (to Compliance review) | 5 | Tracked | |

## 3. Forecast (not evidence)

The Stage 4 benefits model rerun with the adoption measured in week 8 in place of the assumed 60%.

| | Stage 4 forecast | Updated with measured adoption |
| --- | --- | --- |
| Adoption assumed | 60% | 63% |
| Staff hours released per year, network | 10,204 | 10,714 |
| Value of time (TZS) | 153M | 161M |
| Year-one net (TZS) | 45M | 53M |

## 4. Activity (reported, never counted as benefit)

| Branch | Staff | Trained | Licences | Champions | Sessions |
| --- | --- | --- | --- | --- | --- |
| Pilot 1 | 16 | 14 | 16 | 2 | 2 |
| Pilot 2 | 15 | 13 | 15 | 2 | 2 |

Charts: [adoption](charts/adoption.png) · [QA returns](charts/qa-returns.png) · [procedure insights](charts/procedure-insights.png) · full [dashboard](dashboard.html).
