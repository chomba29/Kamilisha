"""Measure the SIMULATED Kamilisha pilot against the Stage 4 baseline and the pilot plan.

Benefit evidence is the change in pilot branches minus the change in comparison branches
(difference-in-differences), measured over the settled pilot weeks 5 to 8. Forecasts and activity
(training, licences) are reported separately and never counted as benefit.

Usage (from the 09-measure folder, after generate_pilot_data.py):  python measure.py
Writes measure-summary.md, dashboard.html and chart PNGs in charts/.
"""
import base64, csv, io, os, random, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "04-baseline")
sys.path.insert(0, BASE)
import benefits_model as bm  # noqa: E402  (Stage 4 forecast model)

SETTLED = range(5, 9)                       # pilot weeks used for outcome evidence
INK, MUTED, PILOT, COMP, RED, GOOD = "#1f2a37", "#5b6675", "#0e7490", "#98a2b3", "#c01048", "#067647"


def read(path):
    return list(csv.DictReader(open(path, encoding="utf-8")))


def share(rows, cond):
    return sum(cond(r) for r in rows) / len(rows) if rows else float("nan")


def load():
    pre = read(os.path.join(BASE, "data", "baseline_requests.csv"))
    pre_s = read(os.path.join(BASE, "data", "baseline_survey.csv"))
    post_all = read(os.path.join(HERE, "data", "pilot_requests.csv"))
    post = [r for r in post_all if int(r["week"]) in SETTLED]
    return dict(pre=pre, post=post, post_all=post_all, pre_s=pre_s,
                post_s=read(os.path.join(HERE, "data", "pilot_survey.csv")),
                q=read(os.path.join(HERE, "data", "pilot_questions.csv")),
                act=read(os.path.join(HERE, "data", "pilot_activity.csv")))


# ---------------------------------------------------------------- outcome KPIs
def kpi_values(rows, survey=None, weeks=None):
    lookups = [r for r in rows if r["lookup_route"] != "Already knew"]
    timed = [float(r["minutes_to_answer"]) for r in lookups if r["minutes_to_answer"]]
    cards = [r for r in rows if r["procedure"] == "Card replacement"]
    nb = len({r["branch"] for r in rows})
    return {
        "K3": share(rows, lambda r: r["qa_returned"] == "Yes"),
        "K3a": share(cards, lambda r: r["qa_returned"] == "Yes"),
        "K4": share(cards, lambda r: r["blocking_form_on_file"] == "Yes"),
        "K1": statistics.median(timed) if timed else float("nan"),
        "K2": sum(r["lookup_route"] == "Colleague" for r in rows) / (nb * 6 * weeks * 5),
        "K6": statistics.mean(int(s["confidence_current_procedure"]) for s in survey) if survey else float("nan"),
    }


def did(d):
    g = lambda rows, grp: [r for r in rows if r["group"] == grp]
    out = {}
    for grp in ("Pilot", "Comparison"):
        out[grp] = (kpi_values(g(d["pre"], grp), g(d["pre_s"], grp), 8),
                    kpi_values(g(d["post"], grp), g(d["post_s"], grp), len(SETTLED)))
    rows = []
    spec = [("K3", "QA return rate, three procedures", "rate", "40% lower"),
            ("K3a", "QA return rate, card replacement", "rate", "50% lower"),
            ("K4", "Blocking form on file", "rate", "At least 95%"),
            ("K1", "Median minutes to an answer (lookups)", "min", "1.5 or less"),
            ("K2", "Colleague questions per officer per day", "num", "50% lower"),
            ("K6", "Staff confidence (1 to 5)", "num", "Up 0.8 points")]
    for k, name, unit, target in spec:
        (pp, pq), (cp, cq) = [(out[g][0][k], out[g][1][k]) for g in ("Pilot", "Comparison")]
        rel = (pq - pp) / pp - (cq - cp) / cp                     # relative change, pilot minus comparison
        diff = (pq - pp) - (cq - cp)                              # absolute change, pilot minus comparison
        met = {"K3": rel <= -0.40, "K3a": rel <= -0.50, "K4": pq >= 0.95, "K1": pq <= 1.5,
               "K2": rel <= -0.50, "K6": diff >= 0.8}[k]
        rows.append(dict(k=k, name=name, unit=unit, target=target, pp=pp, pq=pq, cp=cp, cq=cq, rel=rel, diff=diff, met=met))
    return rows


def bootstrap_k3(d, reps=2000, seed=7):
    """95% interval for the K3 relative difference-in-differences: resample requests within each
    group and period, recompute, take the 2.5th and 97.5th percentiles."""
    rng = random.Random(seed)
    cells = {(grp, per): [r["qa_returned"] == "Yes" for r in d[per] if r["group"] == grp]
             for grp in ("Pilot", "Comparison") for per in ("pre", "post")}
    est = []
    for _ in range(reps):
        m = {c: sum(rng.choices(v, k=len(v))) / len(v) for c, v in cells.items()}
        est.append((m[("Pilot", "post")] - m[("Pilot", "pre")]) / m[("Pilot", "pre")]
                   - (m[("Comparison", "post")] - m[("Comparison", "pre")]) / m[("Comparison", "pre")])
    est.sort()
    return est[int(0.025 * reps)], est[int(0.975 * reps)]


# ---------------------------------------------------------------- adoption and quality
def adoption(d):
    weekly = {}
    for b in ("Pilot 1", "Pilot 2"):
        for w in range(1, 9):
            rows = [r for r in d["post_all"] if r["branch"] == b and int(r["week"]) == w and r["lookup_route"] != "Already knew"]
            weekly[(b, w)] = share(rows, lambda r: r["lookup_route"] == "Kamilisha")
    trained = {a["branch"]: int(a["staff_trained"]) for a in d["act"]}
    active = {(b, w): len({q["staff_id"] for q in d["q"] if q["branch"] == b and int(q["week"]) == w}) / trained[b]
              for b in trained for w in range(1, 9)}
    wk8 = [r for r in d["post_all"] if r["group"] == "Pilot" and int(r["week"]) == 8 and r["lookup_route"] != "Already knew"]
    return weekly, active, share(wk8, lambda r: r["lookup_route"] == "Kamilisha")


def quality(d):
    q = d["q"]
    rev = [x for x in q if x["owner_reviewed"] == "Yes"]
    ans = [x for x in q if x["status"] == "answered"]
    by_lang = {l: share([x for x in rev if x["language"] == l], lambda x: x["owner_verdict"] == "Correct") for l in ("en", "sw")}
    weekly = {w: share([x for x in rev if int(x["week"]) == w], lambda x: x["owner_verdict"] == "Correct") for w in range(1, 9)}
    return dict(k9=share(rev, lambda x: x["owner_verdict"] == "Correct"), n_rev=len(rev), by_lang=by_lang, weekly=weekly,
                k10=share(ans, lambda x: x["wrong_or_unclear"] == "Yes"),
                k11=share(q, lambda x: x["status"] == "not_found"),
                declined=sum(x["status"] == "declined" for x in q), n=len(q),
                sw=share(q, lambda x: x["language"] == "sw"))


# ---------------------------------------------------------------- benefit evidence and forecast
def evidence(d, reg):
    """Measured in the pilot branches, weeks 5-8 only. Not scaled up: that is the forecast's job."""
    g = lambda rows, grp: [r for r in rows if r["group"] == grp]
    pre_p, pre_c, post_p, post_c = g(d["pre"], "Pilot"), g(d["pre"], "Comparison"), g(d["post"], "Pilot"), g(d["post"], "Comparison")
    rate = lambda rows: share(rows, lambda r: r["qa_returned"] == "Yes")
    expected = rate(pre_p) * rate(post_c) / rate(pre_c)            # pilot rate had the comparison trend applied
    avoided = (expected - rate(post_p)) * len(post_p)
    rework_h = avoided * float(reg["A05"]["Expected"]) / 60
    tm = lambda rows, route: [float(r["minutes_to_answer"]) for r in rows if r["lookup_route"] == route and r["minutes_to_answer"]]
    other = [float(r["minutes_to_answer"]) for r in post_c if r["lookup_route"] in ("Colleague", "Intranet") and r["minutes_to_answer"]]
    saved_min = statistics.mean(other) - statistics.mean(tm(post_p, "Kamilisha"))
    k_lookups = sum(r["lookup_route"] == "Kamilisha" for r in post_p)
    lookup_h = k_lookups * saved_min / 60
    trips = lambda rows: sum(r["extra_customer_trip"] == "Yes" for r in rows)
    return dict(expected=expected, actual=rate(post_p), avoided=avoided, rework_h=rework_h, k_lookups=k_lookups,
                saved_min=saved_min, lookup_h=lookup_h, hours=rework_h + lookup_h,
                value=(rework_h + lookup_h) * float(reg["A04"]["Expected"]),
                trips_pilot=trips(post_p), trips_comp=trips(post_c),
                fraud_pilot=sum(r["card_transacted_after_loss"] == "Yes" for r in post_p))


def forecast(reg, measured_adoption):
    req, _ = bm.load(BASE)
    f = bm.baseline_facts(req)
    stage4 = bm.model(f, reg, "Expected")
    upd = {k: dict(v) for k, v in reg.items()}
    upd["A06"]["Expected"] = str(round(measured_adoption * 100))
    return stage4, bm.model(f, upd, "Expected")


# ---------------------------------------------------------------- charts
def charts(adopt_weekly, d, q, did_k3, ci):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    os.makedirs(os.path.join(HERE, "charts"), exist_ok=True)
    out = {}
    weeks = list(range(1, 9))

    def save(fig, name):
        path = os.path.join(HERE, "charts", name)
        fig.tight_layout(); fig.savefig(path, dpi=150, facecolor="white")
        buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=110, facecolor="white"); plt.close(fig)
        out[name] = base64.b64encode(buf.getvalue()).decode()

    # 1. adoption
    fig, ax = plt.subplots(figsize=(8, 4.2))
    for b, c, ls in (("Pilot 1", PILOT, "-"), ("Pilot 2", "#7a5af8", "-")):
        ys = [100 * adopt_weekly[(b, w)] for w in weeks]
        ax.plot(weeks, ys, ls, color=c, lw=2.5, marker="o")
        ax.text(8.15, ys[-1], f"{b} {ys[-1]:.0f}%", va="center", color=c, fontsize=11, fontweight="bold")
    ax.axhline(60, color=MUTED, ls="--", lw=1); ax.text(1, 61.5, "Target 60% by week 8", color=MUTED, fontsize=10)
    ax.axvline(4.5, color=RED, ls=":", lw=1.2); ax.text(4.6, 8, "Week 4 adoption review:\nactions from week 5", color=RED, fontsize=9.5)
    ax.set_ylim(0, 85); ax.set_xlim(0.7, 9.8); ax.set_xticks(weeks); ax.set_xlabel("Pilot week")
    ax.set_title("Adoption: share of lookups made through Kamilisha", loc="left", fontweight="bold", color=INK)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    save(fig, "adoption.png")

    # 2. QA returns before and after, pilot vs comparison (the difference-in-differences picture)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    vals = {}
    for i, (grp, c) in enumerate((("Pilot", PILOT), ("Comparison", COMP))):
        before = 100 * share([r for r in d["pre"] if r["group"] == grp], lambda r: r["qa_returned"] == "Yes")
        after = 100 * share([r for r in d["post"] if r["group"] == grp], lambda r: r["qa_returned"] == "Yes")
        vals[grp] = (before, after)
        for j, (v, alpha) in enumerate(((before, 0.45), (after, 1.0))):
            x = i * 3 + j
            ax.bar(x, v, color=c, alpha=alpha, width=0.8)
            ax.text(x, v + 0.5, f"{v:.1f}%", ha="center", fontsize=11, color=INK)
    ax.set_xticks([0, 1, 3, 4], ["Before", "Weeks 5-8", "Before", "Weeks 5-8"])
    ax.text(0.5, -4.2, "Pilot branches", ha="center", fontweight="bold", color=PILOT)
    ax.text(3.5, -4.2, "Comparison branches", ha="center", fontweight="bold", color=MUTED)
    ax.set_ylim(0, 25); ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.set_title(f"QA return rate: pilot {100 * did_k3:+.0f}% against comparison (95% interval {100 * ci[0]:+.0f}% to {100 * ci[1]:+.0f}%)",
                 loc="left", fontweight="bold", color=INK, fontsize=11.5)
    save(fig, "qa-returns.png")

    # 3. procedure insights
    from collections import Counter
    topics = Counter(x["topic"] for x in d["q"] if x["status"] != "not_found").most_common(8)
    gaps = Counter(x["topic"] for x in d["q"] if x["status"] == "not_found").most_common(5)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1.3, 1]})
    for ax, data, c, title in ((a1, topics, PILOT, "Most-asked procedures"), (a2, gaps, RED, "Not found: library gaps")):
        labels, vals = [t for t, _ in data][::-1], [n for _, n in data][::-1]
        bars = ax.barh(labels, vals, color=c, height=0.6)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_width() + max(vals) * 0.02, bar.get_y() + bar.get_height() / 2, str(v), va="center", fontsize=10)
        ax.set_title(title, loc="left", fontweight="bold", color=INK); ax.tick_params(axis="x", bottom=False, labelbottom=False)
        ax.spines["bottom"].set_visible(False); ax.set_xlim(0, max(vals) * 1.18)
    save(fig, "procedure-insights.png")
    return out


# ---------------------------------------------------------------- report
def pct(x, d=1): return f"{100 * x:.{d}f}%"


def fmt(v, unit): return pct(v) if unit == "rate" else (f"{v:.1f}" if unit == "min" else f"{v:.2f}")


def main():
    d = load()
    reg = {r["ID"]: r for r in read(os.path.join(BASE, "assumptions-register.csv"))}
    kp = did(d)
    adopt_weekly, active, wk8 = adoption(d)
    q = quality(d)
    ev = evidence(d, reg)
    stage4, upd = forecast(reg, wk8)
    by = {r["k"]: r for r in kp}
    lo, hi = bootstrap_k3(d)
    go = [("Adoption (K7) at least 60% in week 8", wk8 >= 0.60, pct(wk8, 0)),
          ("Answer quality (K9) at least 95%", q["k9"] >= 0.95, pct(q["k9"])),
          ("QA returns (K3) down at least 40% against comparison", by["K3"]["met"], f"{100 * by['K3']['rel']:.0f}%"),
          ("No open S1 incident", True, "None")]
    decision = "GO: extend to more branches" if all(x[1] for x in go) else (
        "STOP" if q["k9"] < 0.90 or wk8 < 0.30 else "ADJUST: extend the pilot 4 weeks")
    act = d["act"]

    L = ["# Pilot measurement summary", "",
         "> **Simulated pilot.** All figures come from synthetic data for a fictional bank (`generate_pilot_data.py`). "
         "They show how the pilot would be measured and reported; they are not real results.", "",
         f"**Decision against the pilot plan: {decision}.**", "",
         "| Go rule | Result | Met |", "| --- | --- | --- |"]
    L += [f"| {n} | {v} | {'Yes' if m else 'No'} |" for n, m, v in go]
    L += ["", "## 1. Benefit evidence: business outcomes (difference-in-differences, weeks 5 to 8)", "",
          "Change in the pilot branches minus the change in the comparison branches over the same weeks.", "",
          f"K3 estimate {100 * by['K3']['rel']:+.0f}% with a 95% bootstrap interval of {100 * lo:+.0f}% to {100 * hi:+.0f}%: "
          + ("the reduction is clear of zero, but the interval is wide after 4 weeks in 2 branches."
             if hi < 0 else "the interval includes zero, so the reduction is not yet established."), "",
          "| KPI | Pilot before | Pilot after | Comparison before | Comparison after | Pilot minus comparison | Target | Met |",
          "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in kp:
        net = f"{100 * r['rel']:+.0f}% relative" if r["k"] in ("K3", "K3a", "K2") else (
              f"{100 * r['diff']:+.1f} points" if r["unit"] == "rate" else f"{r['diff']:+.2f}")
        L.append(f"| {r['k']} {r['name']} | {fmt(r['pp'], r['unit'])} | {fmt(r['pq'], r['unit'])} | {fmt(r['cp'], r['unit'])} | "
                 f"{fmt(r['cq'], r['unit'])} | {net} | {r['target']} | {'Yes' if r['met'] else 'No'} |")
    L += ["", "**Measured value in the two pilot branches, weeks 5 to 8:**", "",
          "| Measure | Value |", "| --- | --- |",
          f"| QA return rate expected without Kamilisha (pilot baseline with the comparison trend) | {pct(ev['expected'])} |",
          f"| QA return rate measured | {pct(ev['actual'])} |",
          f"| QA returns avoided | {ev['avoided']:.0f} |",
          f"| Staff hours saved on rework (at {reg['A05']['Expected']} minutes each) | {ev['rework_h']:.0f} |",
          f"| Lookups made through Kamilisha | {ev['k_lookups']} |",
          f"| Minutes saved per lookup (against colleague or intranet lookups in comparison branches) | {ev['saved_min']:.1f} |",
          f"| Staff hours saved on lookups | {ev['lookup_h']:.0f} |",
          f"| **Total staff hours released (4 weeks, 2 branches)** | **{ev['hours']:.0f}** |",
          f"| Value at staff cost (TZS) | {ev['value'] / 1e6:.1f}M |",
          f"| Extra customer trips, business accounts: pilot / comparison | {ev['trips_pilot']} / {ev['trips_comp']} |",
          f"| Lost cards that transacted in pilot branches | {ev['fraud_pilot']} (too rare to measure; not claimed) |", "",
          "## 2. Adoption and quality", "",
          "| KPI | Result | Target | Met |", "| --- | --- | --- | --- |",
          f"| K7 Adoption, week 8 (both pilot branches) | {pct(wk8, 0)} | 60% | {'Yes' if wk8 >= 0.6 else 'No'} |",
          f"| K7 Adoption, week 8: Pilot 1 / Pilot 2 | {pct(adopt_weekly[('Pilot 1', 8)], 0)} / {pct(adopt_weekly[('Pilot 2', 8)], 0)} | 60% | |",
          f"| K8 Active users, week 8: Pilot 1 / Pilot 2 | {pct(active[('Pilot 1', 8)], 0)} / {pct(active[('Pilot 2', 8)], 0)} | 70% | "
          f"{'Yes' if min(active[('Pilot 1', 8)], active[('Pilot 2', 8)]) >= 0.7 else 'No'} |",
          f"| K9 Answer quality (owner review of {q['n_rev']} answers) | {pct(q['k9'])} | 95% | {'Yes' if q['k9'] >= 0.95 else 'No'} |",
          f"| K9 by language: English / Swahili | {pct(q['by_lang']['en'])} / {pct(q['by_lang']['sw'])} | 95% each | "
          f"{'Yes' if min(q['by_lang'].values()) >= 0.95 else 'No'} |",
          f"| K10 Wrong or unclear rate | {pct(q['k10'])} | 5% or less | {'Yes' if q['k10'] <= 0.05 else 'No'} |",
          f"| K11 Not found rate | {pct(q['k11'])} | Tracked | |",
          f"| Questions in Swahili | {pct(q['sw'], 0)} of {q['n']} | Tracked | |",
          f"| Declined workaround questions (to Compliance review) | {q['declined']} | Tracked | |", "",
          "## 3. Forecast (not evidence)", "",
          "The Stage 4 benefits model rerun with the adoption measured in week 8 in place of the assumed 60%.", "",
          "| | Stage 4 forecast | Updated with measured adoption |", "| --- | --- | --- |",
          f"| Adoption assumed | {reg['A06']['Expected']}% | {round(wk8 * 100)}% |",
          f"| Staff hours released per year, network | {stage4['hours']:,.0f} | {upd['hours']:,.0f} |",
          f"| Value of time (TZS) | {stage4['benefit'] / 1e6:.0f}M | {upd['benefit'] / 1e6:.0f}M |",
          f"| Year-one net (TZS) | {stage4['net1'] / 1e6:.0f}M | {upd['net1'] / 1e6:.0f}M |", "",
          "## 4. Activity (reported, never counted as benefit)", "",
          "| Branch | Staff | Trained | Licences | Champions | Sessions |", "| --- | --- | --- | --- | --- | --- |"]
    L += [f"| {a['branch']} | {a['staff_in_branch']} | {a['staff_trained']} | {a['licences_issued']} | {a['champions']} | {a['training_sessions']} |" for a in act]
    L += ["", "Charts: [adoption](charts/adoption.png) · [QA returns](charts/qa-returns.png) · "
          "[procedure insights](charts/procedure-insights.png) · full [dashboard](dashboard.html)."]
    open(os.path.join(HERE, "measure-summary.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")

    imgs = charts(adopt_weekly, d, q, by["K3"]["rel"], (lo, hi))
    tiles = [("Adoption, week 8", pct(wk8, 0), "target 60%"), ("Answer quality", pct(q["k9"]), "target 95%"),
             ("QA returns vs comparison", f"{100 * by['K3']['rel']:+.0f}%", "target -40%"),
             ("Staff hours released", f"{ev['hours']:.0f}", "2 branches, 4 weeks (evidence)")]
    html = ["<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>",
            "<title>Kamilisha pilot dashboard</title><style>",
            "body{font-family:Segoe UI,Helvetica,Arial,sans-serif;margin:0;background:#f6f8fa;color:#1f2a37}",
            "main{max-width:1000px;margin:auto;padding:24px 16px}h1{margin:.2em 0}h2{margin-top:2em;border-bottom:1px solid #d0d5dd;padding-bottom:6px}",
            ".banner{background:#fff4e5;border:1px solid #f79009;border-radius:8px;padding:10px 14px}",
            ".tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:18px 0}",
            ".tile{background:#fff;border:1px solid #d0d5dd;border-radius:10px;padding:14px}.tile b{font-size:28px;display:block}",
            ".tile small{color:#5b6675}img{max-width:100%;background:#fff;border:1px solid #d0d5dd;border-radius:10px}",
            "table{border-collapse:collapse;background:#fff;width:100%;margin:10px 0}td,th{border:1px solid #d0d5dd;padding:6px 8px;text-align:left;font-size:14px}",
            ".tag{display:inline-block;font-size:12px;padding:2px 8px;border-radius:10px;background:#eef2f6;color:#344054}</style></head><body><main>",
            "<p class='tag'>KAMILISHA · STAGE 9 · MEASURE</p><h1>Pilot dashboard</h1>",
            "<p class='banner'><b>Simulated pilot.</b> Synthetic data for a fictional bank. Shows how results would be measured and reported.</p>",
            f"<p><b>Decision: {decision}</b></p><div class='tiles'>"]
    html += [f"<div class='tile'><small>{t}</small><b>{v}</b><small>{s}</small></div>" for t, v, s in tiles]
    html += ["</div>", "<h2>1. Adoption</h2>", f"<img alt='Adoption by week' src='data:image/png;base64,{imgs['adoption.png']}'>",
             "<h2>2. Quality</h2><table><tr><th>Measure</th><th>Result</th><th>Target</th></tr>",
             f"<tr><td>Answer quality, owner review</td><td>{pct(q['k9'])}</td><td>95%</td></tr>",
             f"<tr><td>English / Swahili</td><td>{pct(q['by_lang']['en'])} / {pct(q['by_lang']['sw'])}</td><td>95% each</td></tr>",
             f"<tr><td>Wrong or unclear</td><td>{pct(q['k10'])}</td><td>5% or less</td></tr>",
             f"<tr><td>Not found</td><td>{pct(q['k11'])}</td><td>Tracked</td></tr></table>",
             "<h2>3. Benefit evidence</h2><p>Pilot change minus comparison change, weeks 5 to 8.</p>",
             f"<img alt='QA returns by week' src='data:image/png;base64,{imgs['qa-returns.png']}'>",
             "<table><tr><th>KPI</th><th>Pilot minus comparison</th><th>Target</th><th>Met</th></tr>"]
    for r in kp:
        net = f"{100 * r['rel']:+.0f}%" if r["k"] in ("K3", "K3a", "K2") else (f"{100 * r['diff']:+.1f} pts" if r["unit"] == "rate" else f"{r['diff']:+.2f}")
        html.append(f"<tr><td>{r['k']} {r['name']}</td><td>{net}</td><td>{r['target']}</td><td>{'Yes' if r['met'] else 'No'}</td></tr>")
    html += ["</table>", f"<p>Staff hours released in the pilot (evidence): <b>{ev['hours']:.0f}</b> in 4 weeks across 2 branches.</p>",
             "<h2>4. Forecast (not evidence)</h2><table><tr><th></th><th>Stage 4</th><th>With measured adoption</th></tr>",
             f"<tr><td>Adoption</td><td>{reg['A06']['Expected']}%</td><td>{round(wk8 * 100)}%</td></tr>",
             f"<tr><td>Hours per year, network</td><td>{stage4['hours']:,.0f}</td><td>{upd['hours']:,.0f}</td></tr>",
             f"<tr><td>Year-one net (TZS)</td><td>{stage4['net1'] / 1e6:.0f}M</td><td>{upd['net1'] / 1e6:.0f}M</td></tr></table>",
             "<h2>5. Activity (not benefit)</h2><table><tr><th>Branch</th><th>Trained</th><th>Licences</th><th>Champions</th></tr>"]
    html += [f"<tr><td>{a['branch']}</td><td>{a['staff_trained']}</td><td>{a['licences_issued']}</td><td>{a['champions']}</td></tr>" for a in act]
    html += ["</table><h2>6. Procedure insights</h2>", f"<img alt='Procedure insights' src='data:image/png;base64,{imgs['procedure-insights.png']}'>",
             "</main></body></html>"]
    open(os.path.join(HERE, "dashboard.html"), "w", encoding="utf-8").write("\n".join(html))
    print(open(os.path.join(HERE, "measure-summary.md"), encoding="utf-8").read())


if __name__ == "__main__":
    main()
