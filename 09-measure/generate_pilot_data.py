"""Generate a SIMULATED 8-week Kamilisha pilot for a fictional bank.

Same four branches and request model as the Stage 4 baseline. In the two pilot branches, staff
use Kamilisha for a growing share of lookups; when they do, answers are current and quick. The
comparison branches carry on as before, with a small bank-wide improvement from the library
clean-up (which is why results are measured as a difference against the comparison branches).
Staff who answer from memory also update their habits as they see current answers and changed-on flags.
Pilot 2 adopts slowly until a week-4 adoption review finds the causes and acts on them.

Every parameter is a modelling assumption, not a measurement. Seeded, so reruns give identical files.
Usage: python generate_pilot_data.py [output_folder]
Outputs in data/: pilot_requests.csv, pilot_questions.csv, pilot_survey.csv, pilot_activity.csv
"""
import csv, math, os, random, sys
from datetime import date, timedelta

SEED = 2027
START = date(2026, 11, 2)            # pilot week 1 (simulated)
WEEKS = 8
BRANCHES = [("Pilot 1", "Pilot"), ("Pilot 2", "Pilot"),
            ("Comparison 1", "Comparison"), ("Comparison 2", "Comparison")]
OFFICERS = 6                         # per branch, handling the three focus procedures
STAFF_TRAINED = {"Pilot 1": 14, "Pilot 2": 13}

# ---- request model: the Stage 4 baseline assumptions ----
PROC = {
    "Card replacement":         dict(vol=20, sure=0.30, ask=0.65, outdated=0.40, qa=0.03, qa_out=0.0),
    "Business account opening": dict(vol=6,  sure=0.25, ask=0.70, outdated=0.45, qa=0.08, qa_out=0.30),
    "Annual leave":             dict(vol=3,  sure=0.50, ask=0.60, outdated=0.30, qa=0.05, qa_out=0.40),
}
FORM_SKIP_IF_OUTDATED, FORM_SKIP_OTHERWISE = 0.80, 0.04
QA_CATCHES_SKIPPED_FORM = 0.70
P_LOST_CARD_TRANSACTS = 0.05
EXTRA_TRIP_IF_OUTDATED = 0.60
TIME_MEDIAN_MIN = {"Already knew": 0.5, "Intranet": 9.0, "Colleague": 3.0, "Kamilisha": 1.2}
TIME_SPREAD = 0.45
OBSERVED_SHARE = 0.20

# ---- pilot assumptions ----
BANKWIDE_OUTDATED_CUT = 0.10         # library clean-up helps every branch a little
KAMILISHA_OUTDATED = 0.03            # outdated answers when Kamilisha is used (wrong-answer residual)
HABIT_CORRECTION = 0.8               # staff who "already know" are corrected by current answers and changed-on flags
ADOPTION = {                         # share of lookups made through Kamilisha, by week
    "Pilot 1": [0.30, 0.42, 0.50, 0.56, 0.60, 0.63, 0.65, 0.66],
    "Pilot 2": [0.18, 0.22, 0.25, 0.27, 0.38, 0.48, 0.55, 0.60],   # review in week 4, actions from week 5
}
NOT_IN_LIBRARY = [                    # questions staff asked that the library could not answer
    ("Foreign currency cheque deposit", 0.30), ("Fixed deposit account opening", 0.22),
    ("SWIFT transfer abroad", 0.18), ("Account closure", 0.16), ("Standing order set-up", 0.14),
]


def poisson(rng, lam):
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def requests(rng):
    rows, rid = [], 0
    for branch, group in BRANCHES:
        for w in range(WEEKS):
            for proc, a in PROC.items():
                for _ in range(poisson(rng, a["vol"])):
                    rid += 1
                    day = START + timedelta(days=7 * w + rng.randrange(5))
                    outdated_p = a["outdated"] * (1 - BANKWIDE_OUTDATED_CUT)
                    if rng.random() < a["sure"]:
                        habit = outdated_p * 0.5
                        if group == "Pilot":                 # seeing current answers corrects old habits
                            habit *= 1 - HABIT_CORRECTION * ADOPTION[branch][w]
                        route, outdated = "Already knew", rng.random() < habit
                    elif group == "Pilot" and rng.random() < ADOPTION[branch][w]:
                        route, outdated = "Kamilisha", rng.random() < KAMILISHA_OUTDATED
                    elif rng.random() < a["ask"]:
                        route, outdated = "Colleague", rng.random() < outdated_p
                    else:
                        route, outdated = "Intranet", False
                    minutes = round(rng.lognormvariate(math.log(TIME_MEDIAN_MIN[route]), TIME_SPREAD), 1)
                    observed = rng.random() < OBSERVED_SHARE
                    form, fraud, trip = "", "", ""
                    if proc == "Card replacement":
                        skipped = rng.random() < (FORM_SKIP_IF_OUTDATED if outdated else FORM_SKIP_OTHERWISE)
                        form = "No" if skipped else "Yes"
                        caught = skipped and rng.random() < QA_CATCHES_SKIPPED_FORM
                        returned = caught or rng.random() < a["qa"]
                        fraud = "Yes" if (skipped and not caught and rng.random() < P_LOST_CARD_TRANSACTS) else "No"
                    else:
                        returned = rng.random() < a["qa"] + (a["qa_out"] if outdated else 0)
                    if proc == "Business account opening":
                        trip = "Yes" if (outdated and rng.random() < EXTRA_TRIP_IF_OUTDATED) else "No"
                    rows.append(dict(request_id=f"P{rid:05d}", date=day.isoformat(), week=w + 1, branch=branch,
                                     group=group, procedure=proc, lookup_route=route,
                                     answer_outdated="Yes" if outdated else "No",
                                     timed_observation="Yes" if observed else "No",
                                     minutes_to_answer=minutes if observed else "",
                                     qa_returned="Yes" if returned else "No", blocking_form_on_file=form,
                                     card_transacted_after_loss=fraud, extra_customer_trip=trip))
    return rows


def questions(rng, reqs):
    """The Kamilisha question log: one row per question, including questions outside the three
    focus procedures and outside the library."""
    out, qid = [], 0
    other = ["New card issuance", "Individual account opening", "Customer information update",
             "SIM banking enrolment", "Internet banking reset", "Loan origination", "Collateral",
             "Salary advance", "Code of conduct"]
    for branch in ("Pilot 1", "Pilot 2"):
        for w in range(1, WEEKS + 1):
            focus = [r for r in reqs if r["branch"] == branch and r["week"] == w and r["lookup_route"] == "Kamilisha"]
            extra = poisson(rng, 12 * ADOPTION[branch][w - 1] / 0.6)          # other procedures
            gaps = poisson(rng, 3)                                          # not in the library
            items = [(r["procedure"], "focus") for r in focus] + [(rng.choice(other), "other") for _ in range(extra)]
            items += [(rng.choices([n for n, _ in NOT_IN_LIBRARY], [p for _, p in NOT_IN_LIBRARY])[0], "gap")
                      for _ in range(gaps)]
            for topic, kind in items:
                qid += 1
                if kind == "gap":
                    status = "not_found"
                elif rng.random() < 0.04:
                    status = "declined"
                elif topic == "Business account opening" and rng.random() < 0.15:
                    status = "need_info"
                else:
                    status = "answered"
                lang = "sw" if rng.random() < 0.38 else "en"
                sampled = status == "answered" and rng.random() < 0.25          # owners review a sample
                correct = rng.random() < (0.965 if lang == "en" else 0.955)
                out.append(dict(question_id=f"Q{qid:05d}", week=w, branch=branch, topic=topic, language=lang,
                                status=status, wrong_or_unclear="Yes" if status == "answered" and rng.random() < 0.035 else "No",
                                owner_reviewed="Yes" if sampled else "No",
                                owner_verdict=("Correct" if correct else "Incorrect") if sampled else "",
                                staff_id=f"{branch[-1]}{rng.randint(1, STAFF_TRAINED[branch]):02d}"))
    return out


def survey(rng):
    """Staff confidence (1-5) at the end of the pilot. Baseline means: Pilot 2.60, Comparison 3.15."""
    rows = []
    for branch, group in BRANCHES:
        mean = 3.6 if group == "Pilot" else 3.25
        for i in range(10):
            rows.append(dict(respondent=f"{branch[:1]}{branch[-1]}-{i + 1:02d}", branch=branch, group=group,
                             confidence_current_procedure=min(5, max(1, round(rng.gauss(mean, 0.8))))))
    return rows


def activity():
    """Activity measures: reported, never counted as benefit."""
    return [dict(branch=b, staff_in_branch=n + 2, staff_trained=n, licences_issued=n + 2,
                 champions=2, training_sessions=2) for b, n in STAFF_TRAINED.items()]


def write(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    rng = random.Random(SEED)
    reqs = requests(rng)
    qs = questions(rng, reqs)
    write(os.path.join(out, "data", "pilot_requests.csv"), reqs)
    write(os.path.join(out, "data", "pilot_questions.csv"), qs)
    write(os.path.join(out, "data", "pilot_survey.csv"), survey(rng))
    write(os.path.join(out, "data", "pilot_activity.csv"), activity())
    print(f"{len(reqs)} requests, {len(qs)} Kamilisha questions written to {os.path.join(out, 'data')}")
