"""Kamilisha Stage 4 benefits model.

Reads the baseline data (data/baseline_requests.csv) and the assumptions register
(assumptions-register.csv) and writes benefits-case.md. Every forecast number traces to
a baseline measure or a named assumption, so Finance can replace any assumption and rerun.

Usage: python benefits_model.py [folder]   (folder holding the data and the register)
"""
import csv, os, statistics, sys

SCEN = ["Cautious", "Expected", "Optimistic"]
WEEKS_OBSERVED, BRANCHES_OBSERVED, HOURS_PER_DAY = 8, 4, 8


def load(folder):
    req = list(csv.DictReader(open(os.path.join(folder, "data", "baseline_requests.csv"), encoding="utf-8")))
    reg = {r["ID"]: r for r in csv.DictReader(open(os.path.join(folder, "assumptions-register.csv"), encoding="utf-8"))}
    return req, reg


def baseline_facts(req):
    """Measured at baseline (synthetic). Annualised per branch."""
    lookups = [x for x in req if x["lookup_route"] != "Already knew"]
    timed = [float(x["minutes_to_answer"]) for x in lookups if x["minutes_to_answer"]]
    # QA returns caused by outdated answers = returns among outdated answers minus the
    # returns those requests would have had anyway (each procedure's rate when the answer was current)
    excess = 0.0
    for p in {x["procedure"] for x in req}:
        rows = [x for x in req if x["procedure"] == p]
        cur = [x for x in rows if x["answer_outdated"] == "No"]
        out = [x for x in rows if x["answer_outdated"] == "Yes"]
        base_rate = sum(x["qa_returned"] == "Yes" for x in cur) / len(cur)
        excess += max(0.0, sum(x["qa_returned"] == "Yes" for x in out) - base_rate * len(out))
    acc = [x for x in req if x["procedure"] == "Business account opening"]
    per_branch_year = lambda n, weeks_per_year: n / BRANCHES_OBSERVED / WEEKS_OBSERVED * weeks_per_year
    return dict(requests=len(req), lookups=len(lookups), lookup_share=len(lookups) / len(req),
                mean_lookup_min=statistics.mean(timed), timed_n=len(timed),
                returns=sum(x["qa_returned"] == "Yes" for x in req), excess_returns=excess,
                extra_trips=sum(x["extra_customer_trip"] == "Yes" for x in acc),
                fraud_events=sum(x["card_transacted_after_loss"] == "Yes" for x in req),
                per_branch_year=per_branch_year)


def model(f, reg, s):
    a = lambda k: float(reg[k][s])
    weeks_per_year = a("A03") / 5
    scale = lambda n: f["per_branch_year"](n, weeks_per_year) * a("A01")      # network, per year
    adopt, cut = a("A06") / 100, a("A08") / 100
    rate = a("A04")
    lookups_year = scale(f["lookups"])
    time_hours = lookups_year * adopt * max(0.0, f["mean_lookup_min"] - a("A07")) / 60
    rework_hours = scale(f["excess_returns"]) * adopt * cut * a("A05") / 60
    trips_avoided = scale(f["extra_trips"]) * adopt * cut
    officers = a("A01") * a("A02")
    cost1 = (a("C01") * HOURS_PER_DAY * rate + a("C02") + a("C03") + a("C04") * officers * rate
             + a("C05") * a("A03") * HOURS_PER_DAY * rate)
    cost_run = a("C03") + a("C05") * a("A03") * HOURS_PER_DAY * rate
    benefit = (time_hours + rework_hours) * rate
    return dict(lookups_year=lookups_year, time_hours=time_hours, rework_hours=rework_hours,
                hours=time_hours + rework_hours, benefit=benefit, trips=trips_avoided,
                cost1=cost1, cost_run=cost_run, net1=benefit - cost1, net_run=benefit - cost_run,
                fte=(time_hours + rework_hours) / (a("A03") * HOURS_PER_DAY))


def sensitivity(f, reg):
    """Change one assumption to its cautious value, keep the rest at expected; report year-one net."""
    out = []
    for k in ["A06", "A08", "A05", "A07", "C02", "C03", "C05"]:
        trial = {kk: dict(v) for kk, v in reg.items()}
        trial[k]["Expected"] = reg[k]["Cautious"]
        out.append((k, reg[k]["Assumption"], reg[k]["Cautious"], reg[k]["Unit"], model(f, trial, "Expected")["net1"]))
    return sorted(out, key=lambda r: r[4])


def m(x): return f"{x / 1e6:,.0f}M"


def write(folder, f, res, sens):
    E = res["Expected"]
    L = []
    L += ["# Benefits case", "",
          "Computed by `benefits_model.py` from the baseline data and the [assumptions register](assumptions-register.csv). "
          "Do not edit by hand; change an assumption and rerun. Amounts in Tanzanian shillings (TZS), fictional bank, "
          "network-wide, for the three pilot procedures only.", "",
          "## 1. Evidence: what the baseline measured", "",
          "These are observations (synthetic for this portfolio), not forecasts.", "",
          "| Measure | Baseline (4 branches, 8 weeks) |", "| --- | --- |",
          f"| Requests handled | {f['requests']} |",
          f"| Requests needing a lookup | {f['lookups']} ({100 * f['lookup_share']:.0f}%) |",
          f"| Mean minutes per lookup (timed sample, n={f['timed_n']}) | {f['mean_lookup_min']:.1f} |",
          f"| QA returns | {f['returns']} |",
          f"| QA returns caused by outdated answers (excess over the current-answer rate) | {f['excess_returns']:.0f} |",
          f"| Extra customer trips, business accounts | {f['extra_trips']} |",
          f"| Lost cards that transacted | {f['fraud_events']} (too rare to measure in 8 weeks) |", "",
          "## 2. Forecast: expected benefits per year after rollout", "",
          "Most of the benefit is **staff time released**, not cash saved. It is shown in hours first; TZS is for comparison only.", "",
          "| | " + " | ".join(SCEN) + " |", "| --- | --- | --- | --- |",
          "| Staff hours saved on lookups | " + " | ".join(f"{res[s]['time_hours']:,.0f}" for s in SCEN) + " |",
          "| Staff hours saved on QA rework | " + " | ".join(f"{res[s]['rework_hours']:,.0f}" for s in SCEN) + " |",
          "| **Total hours released** | " + " | ".join(f"**{res[s]['hours']:,.0f}**" for s in SCEN) + " |",
          "| Equivalent full-time staff | " + " | ".join(f"{res[s]['fte']:.1f}" for s in SCEN) + " |",
          "| Value of time at staff cost (TZS) | " + " | ".join(m(res[s]['benefit']) for s in SCEN) + " |",
          "| Customer trips avoided (not valued) | " + " | ".join(f"{res[s]['trips']:,.0f}" for s in SCEN) + " |", "",
          "## 3. Costs (TZS)", "",
          "| | " + " | ".join(SCEN) + " |", "| --- | --- | --- | --- |",
          "| Year one: clean-up, build or licence, running, training, support | " + " | ".join(m(res[s]['cost1']) for s in SCEN) + " |",
          "| Each later year: running and support | " + " | ".join(m(res[s]['cost_run']) for s in SCEN) + " |", "",
          "## 4. Net view (TZS)", "",
          "| | " + " | ".join(SCEN) + " |", "| --- | --- | --- | --- |",
          "| Year one | " + " | ".join(m(res[s]['net1']) for s in SCEN) + " |",
          "| Each later year | " + " | ".join(m(res[s]['net_run']) for s in SCEN) + " |", "",
          f"In the expected case the value of time released ({m(E['benefit'])}) "
          + ("covers" if E['net1'] >= 0 else "does not cover") + f" year-one costs ({m(E['cost1'])}).", "",
          "**Which assumption matters most?** Each row moves one assumption to its cautious value and keeps the rest at expected.", "",
          "| Assumption moved to cautious | Cautious value | Year-one net (TZS) |", "| --- | --- | --- |"]
    show = lambda v, u: m(float(v)) if u == "TZS" else (f"{v}%" if u == "%" else f"{v} {u}")
    L += [f"| {k} {name} | {show(val, unit)} | {m(net)} |" for k, name, val, unit, net in sens]
    L += ["", f"{sens[0][0]} is the biggest driver: at its cautious value year one "
          + ("does not pay back" if sens[0][4] < 0 else "still pays back") + ". The pilot must prove it before rollout.", "",
          "## 5. Not counted, on purpose", "",
          "- **Fraud loss avoided:** credited to the system hard stop for the blocking form (Stage 2, P4), not to Kamilisha (A10 = 0%). Counting it twice would overstate the case.",
          "- **Other procedures:** only three procedures are modelled. Adding more raises benefits with little extra cost; treated as upside, not forecast.",
          "- **Audit queries:** too slow to move in a pilot; tracked for two quarters after rollout.", "",
          "## 6. How the benefit will be evidenced", "",
          "Stage 9 measures the change in pilot branches against the change in comparison branches over the same weeks. "
          "Only that difference is reported as benefit evidence. Forecasts, training attendance and licence counts are "
          "reported separately and never as benefit."]
    open(os.path.join(folder, "benefits-case.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    req, reg = load(folder)
    f = baseline_facts(req)
    res = {s: model(f, reg, s) for s in SCEN}
    sens = sensitivity(f, reg)
    write(folder, f, res, sens)
    for s in SCEN:
        r = res[s]
        print(f"{s}: hours {r['hours']:,.0f}, benefit {m(r['benefit'])}, cost1 {m(r['cost1'])}, net1 {m(r['net1'])}, net later {m(r['net_run'])}")
