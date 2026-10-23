"""Generate the Kamilisha Stage 4 baseline: synthetic "today" data for a fictional bank.

Four branches (two pilot, two comparison) over eight weeks, 24 Aug - 16 Oct 2026.
Every parameter below is a modelling assumption drawn from the Stage 1 practitioner
interview, not a measurement from any real bank. Seeded, so reruns give identical files.

Outputs (in the folder given, default current folder):
  data/baseline_requests.csv   one row per request handled
  data/baseline_survey.csv     staff confidence survey (1-5)
  data/baseline_audit.csv      audit queries on the three procedures, last four quarters
  baseline-summary.md          the KPI baseline table, computed from the files above
  baseline-chart.png           QA return rate and time to answer (needs matplotlib)

Usage: python generate_baseline.py [output_folder]
"""
import csv, math, os, random, statistics, sys
from datetime import date, timedelta

SEED = 2026
START = date(2026, 8, 24)            # Monday
WEEKS = 8
BRANCHES = [("Pilot 1", "Pilot"), ("Pilot 2", "Pilot"),
            ("Comparison 1", "Comparison"), ("Comparison 2", "Comparison")]

# ---- modelling assumptions (from the Stage 1 interview; see assumptions register) ----
PROC = {
    # weekly volume per branch, P(officer already sure), P(asks colleague | not sure),
    # P(colleague answer outdated), base QA return rate, extra return if outdated
    "Card replacement":         dict(vol=20, sure=0.30, ask=0.65, outdated=0.40, qa=0.03, qa_out=0.0),
    "Business account opening": dict(vol=6,  sure=0.25, ask=0.70, outdated=0.45, qa=0.08, qa_out=0.30),
    "Annual leave":             dict(vol=3,  sure=0.50, ask=0.60, outdated=0.30, qa=0.05, qa_out=0.40),
}
FORM_SKIP_IF_OUTDATED, FORM_SKIP_OTHERWISE = 0.80, 0.04   # card replacement only
QA_CATCHES_SKIPPED_FORM = 0.70
P_LOST_CARD_TRANSACTS = 0.05                              # if a skipped form is not caught
EXTRA_TRIP_IF_OUTDATED = 0.60                             # business account only
TIME_MEDIAN_MIN = {"Already knew": 0.5, "Intranet": 9.0, "Colleague": 3.0}
TIME_SPREAD = 0.45                                        # log-normal sigma
OBSERVED_SHARE = 0.20                                     # share of lookups timed by observation
WORKING_DAYS = 5


def poisson(rng, lam):
    """Knuth's method; fine for the small means used here."""
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def make_requests(rng):
    rows, rid = [], 0
    for branch, group in BRANCHES:
        for w in range(WEEKS):
            for proc, a in PROC.items():
                for _ in range(poisson(rng, a["vol"])):
                    rid += 1
                    day = START + timedelta(days=7 * w + rng.randrange(WORKING_DAYS))
                    if rng.random() < a["sure"]:
                        route = "Already knew"
                        outdated = rng.random() < a["outdated"] * 0.5   # habit can be stale too
                    elif rng.random() < a["ask"]:
                        route, outdated = "Colleague", rng.random() < a["outdated"]
                    else:
                        route, outdated = "Intranet", False
                    minutes = round(rng.lognormvariate(math.log(TIME_MEDIAN_MIN[route]), TIME_SPREAD), 1)
                    observed = rng.random() < OBSERVED_SHARE
                    form_on_file, fraud = "", ""
                    if proc == "Card replacement":
                        skipped = rng.random() < (FORM_SKIP_IF_OUTDATED if outdated else FORM_SKIP_OTHERWISE)
                        form_on_file = "No" if skipped else "Yes"
                        caught = skipped and rng.random() < QA_CATCHES_SKIPPED_FORM
                        returned = caught or rng.random() < a["qa"]
                        fraud = "Yes" if (skipped and not caught and rng.random() < P_LOST_CARD_TRANSACTS) else "No"
                    else:
                        returned = rng.random() < a["qa"] + (a["qa_out"] if outdated else 0)
                    extra_trip = ""
                    if proc == "Business account opening":
                        extra_trip = "Yes" if (outdated and rng.random() < EXTRA_TRIP_IF_OUTDATED) else "No"
                    rows.append(dict(
                        request_id=f"R{rid:05d}", date=day.isoformat(), week=w + 1, branch=branch, group=group,
                        procedure=proc, lookup_route=route, answer_outdated="Yes" if outdated else "No",
                        timed_observation="Yes" if observed else "No",
                        minutes_to_answer=minutes if observed else "",
                        qa_returned="Yes" if returned else "No",
                        blocking_form_on_file=form_on_file, card_transacted_after_loss=fraud,
                        extra_customer_trip=extra_trip))
    return rows


def make_survey(rng):
    rows = []
    for branch, group in BRANCHES:
        for i in range(10):
            score = min(5, max(1, round(rng.gauss(2.8, 0.9))))
            rows.append(dict(respondent=f"{branch[:1]}{branch[-1]}-{i+1:02d}", branch=branch, group=group,
                             confidence_current_procedure=score))
    return rows


def make_audit(rng):
    rows = []
    for q in ["2025-Q4", "2026-Q1", "2026-Q2", "2026-Q3"]:
        for branch, group in BRANCHES:
            for proc, lam in [("Card replacement", 0.8), ("Business account opening", 0.5), ("Annual leave", 0.1)]:
                rows.append(dict(quarter=q, branch=branch, group=group, procedure=proc,
                                 audit_queries=poisson(rng, lam)))
    return rows


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def pct(n, d): return f"{100 * n / d:.1f}%" if d else "n/a"


def kpis(req, survey, audit, group=None):
    r = [x for x in req if group in (None, x["group"])]
    s = [x for x in survey if group in (None, x["group"])]
    a = [x for x in audit if group in (None, x["group"])]
    nb = len({x["branch"] for x in r})
    cards = [x for x in r if x["procedure"] == "Card replacement"]
    timed = [float(x["minutes_to_answer"]) for x in r
             if x["minutes_to_answer"] != "" and x["lookup_route"] != "Already knew"]
    officers_per_branch = 6
    return {
        "K1 Median minutes to an answer when a lookup was needed (timed sample)": f"{statistics.median(timed):.1f} (n={len(timed)})",
        "K2 Colleague questions per officer per day (three procedures)": f"{sum(x['lookup_route']=='Colleague' for x in r) / (nb*officers_per_branch*WEEKS*WORKING_DAYS):.2f}",
        "K3 QA return rate, all three procedures": pct(sum(x["qa_returned"] == "Yes" for x in r), len(r)),
        "K3a QA return rate, card replacement": pct(sum(x["qa_returned"] == "Yes" for x in cards), len(cards)),
        "K4 Blocking form on file, card replacement": pct(sum(x["blocking_form_on_file"] == "Yes" for x in cards), len(cards)),
        "K5 Audit queries per branch per quarter": f"{sum(int(x['audit_queries']) for x in a) / (nb*4):.2f}",
        "K6 Staff confidence (1-5)": f"{statistics.mean(int(x['confidence_current_procedure']) for x in s):.2f} (n={len(s)})",
        "Answers outdated (share of all requests)": pct(sum(x["answer_outdated"] == "Yes" for x in r), len(r)),
        "Extra customer trips, business accounts": pct(sum(x["extra_customer_trip"] == "Yes" for x in r if x["procedure"] == "Business account opening"),
                                                        sum(x["procedure"] == "Business account opening" for x in r)),
        "Lost cards that transacted (count)": str(sum(x["card_transacted_after_loss"] == "Yes" for x in cards)),
        "Requests handled": str(len(r)),
    }


def write_summary(path, req, survey, audit):
    allk, pk, ck = kpis(req, survey, audit), kpis(req, survey, audit, "Pilot"), kpis(req, survey, audit, "Comparison")
    lines = ["# Baseline summary", "",
             "Computed by `generate_baseline.py` from the files in `data/`. Synthetic data for a fictional bank: "
             "4 branches, 8 weeks (24 Aug - 16 Oct 2026). Do not edit by hand; rerun the script.", "",
             "| KPI | All branches | Pilot | Comparison |", "| --- | --- | --- | --- |"]
    for k in allk:
        lines.append(f"| {k} | {allk[k]} | {pk[k]} | {ck[k]} |")
    lines += ["", "Pilot and comparison branches start close on most KPIs; staff confidence starts lower in the pilot branches "
              "(small survey, 20 per group). Stage 9 compares the change in each group, not the level, so different "
              "starting points do not bias the result.", "",
              "Lost cards that transacted are too rare to measure in eight weeks; fraud benefits stay a forecast, not evidence."]
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return allk


def chart(path, req):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed: chart skipped"); return
    procs = list(PROC)
    rates = [100 * sum(x["qa_returned"] == "Yes" for x in req if x["procedure"] == p) /
             sum(x["procedure"] == p for x in req) for p in procs]
    routes = ["Already knew", "Colleague", "Intranet"]
    med = [statistics.median(float(x["minutes_to_answer"]) for x in req
                             if x["lookup_route"] == r and x["minutes_to_answer"] != "") for r in routes]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), dpi=150)
    for ax, labels, vals, title, unit, color in [
        (axes[0], procs, rates, "QA return rate by procedure", "%", "#c01048"),
        (axes[1], routes, med, "Median minutes to an answer, by route", " min", "#0e7490")]:
        bars = ax.barh(labels, vals, color=color, height=0.55)
        ax.invert_yaxis(); ax.set_title(title, loc="left", fontsize=13, fontweight="bold", color="#1f2a37")
        for s in ("top", "right", "bottom"): ax.spines[s].set_visible(False)
        ax.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
        for b, v in zip(bars, vals):
            ax.text(b.get_width() + max(vals) * 0.02, b.get_y() + b.get_height() / 2, f"{v:.1f}{unit}",
                    va="center", fontsize=11, color="#1f2a37")
        ax.set_xlim(0, max(vals) * 1.25)
    for i, r in enumerate(routes):
        rr = [x for x in req if x["lookup_route"] == r]
        share = 100 * sum(x["answer_outdated"] == "Yes" for x in rr) / len(rr)
        if share:
            axes[1].text(med[i] + max(med) * 0.02, i + 0.3, f"{share:.0f}% of answers outdated",
                         va="center", fontsize=10, color="#c01048")
    fig.suptitle("Kamilisha baseline (synthetic data, fictional bank, 8 weeks)", x=0.01, ha="left",
                 fontsize=10, color="#5b6675")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path, facecolor="white"); plt.close(fig)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    rng = random.Random(SEED)
    req, survey, audit = make_requests(rng), make_survey(rng), make_audit(rng)
    write_csv(os.path.join(out, "data", "baseline_requests.csv"), req)
    write_csv(os.path.join(out, "data", "baseline_survey.csv"), survey)
    write_csv(os.path.join(out, "data", "baseline_audit.csv"), audit)
    k = write_summary(os.path.join(out, "baseline-summary.md"), req, survey, audit)
    chart(os.path.join(out, "baseline-chart.png"), req)
    for name, val in k.items():
        print(f"{name}: {val}")
