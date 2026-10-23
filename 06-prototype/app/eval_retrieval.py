"""Retrieval test, two checks per question:
  answer found:  a section that answers the question is in the top 5 from search;
  control given: the mandatory-control section the answer depends on reaches Claude, first from
                 search alone, then after control completion (G-13). Strict: only that section counts.
Runs both searches side by side when a Pinecone key is set, so the difference is visible.
Run from the 06-prototype folder:  python app/eval_retrieval.py
Writes logs/retrieval_eval.csv.
"""
import csv, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kamilisha as k

# (question, language, sections that answer it: a hit on any of them counts)
CASES = [
    ("Customer lost their card, what do I do?", "en", ["CIR-CARD-07-v2-s5.2", "CIR-CARD-07-v2-s5.3", "CIR-CARD-07-v2-faqQ1"]),
    ("Can the customer sign the blocking form after I block the card?", "en", ["CIR-CARD-07-v2-s5.2", "CIR-CARD-07-v2-faqQ2"]),
    ("What is the card replacement fee?", "en", ["CIR-CARD-07-v2-s5.4", "CIR-CARD-07-v2-faqQ4"]),
    ("Can a relative collect a new card for the customer?", "en", ["CIR-CARD-05-v3-s5.6", "CIR-CARD-05-v3-faqQ2"]),
    ("Can I open an account with an expired passport?", "en", ["CIR-ACC-10-v4-s5.1", "CIR-ACC-10-v4-faqQ1"]),
    ("What documents does a sole proprietor need?", "en", ["CIR-ACC-12-v2-s5.2", "CIR-ACC-12-v2-appA", "CIR-ACC-12-v2-faqQ1"]),
    ("Can a customer change their phone number by calling the contact centre?", "en", ["CIR-ACC-15-v2-s5.4", "CIR-ACC-15-v2-faqQ1"]),
    ("The customer's SIM card is registered in his wife's name. Can I enrol him for SIM banking?", "en", ["CIR-DIG-03-v2-s5.2", "CIR-DIG-03-v2-faqQ1"]),
    ("Can I reset an internet banking password over the phone?", "en", ["CIR-DIG-04-v1-s5.5", "CIR-DIG-04-v1-faqQ1"]),
    ("What is the maximum debt service ratio for a loan?", "en", ["CIR-CRD-21-v3-s5.4", "CIR-CRD-21-v3-faqQ1"]),
    ("How old can a property valuation report be?", "en", ["CIR-CRD-22-v2-s5.2", "CIR-CRD-22-v2-faqQ1"]),
    ("How early must I apply for annual leave?", "en", ["HR-POL-03-v2-s5.2", "HR-POL-03-v2-faqQ1"]),
    ("Can I accept a gift from a customer?", "en", ["HR-POL-01-v3-s5.3", "HR-POL-01-v3-faqQ2"]),
    ("Mteja amepoteza kadi, nifanye nini?", "sw", ["CIR-CARD-07-v2-s5.2", "CIR-CARD-07-v2-s5.3", "CIR-CARD-07-v2-faqQ1"]),
    ("Je, nahitaji fomu ya kuzuia kadi kabla ya kuifunga?", "sw", ["CIR-CARD-07-v2-s5.2", "CIR-CARD-07-v2-faqQ2"]),
    ("Mfanyabiashara binafsi anahitaji nyaraka gani kufungua akaunti?", "sw", ["CIR-ACC-12-v2-s5.2", "CIR-ACC-12-v2-appA", "CIR-ACC-12-v2-faqQ1"]),
    ("Mteja anataka kubadilisha namba ya simu kwa kupiga simu, inaruhusiwa?", "sw", ["CIR-ACC-15-v2-s5.4", "CIR-ACC-15-v2-faqQ1"]),
    ("Mteja amesahau nenosiri la benki ya mtandaoni, nifanye nini?", "sw", ["CIR-DIG-04-v1-s5.5", "CIR-DIG-04-v1-faqQ1"]),
    ("Meneja wa tawi anaweza kuidhinisha mkopo hadi kiasi gani?", "sw", ["CIR-CRD-21-v3-s5.7", "CIR-CRD-21-v3-faqQ2"]),
    ("Ninapaswa kuomba likizo ya mwaka siku ngapi kabla?", "sw", ["HR-POL-03-v2-s5.2", "HR-POL-03-v2-faqQ1"]),
    ("Kiwango cha juu cha zawadi ninachoweza kupokea ni kiasi gani?", "sw", ["HR-POL-01-v3-s5.3", "HR-POL-01-v3-faqQ2"]),
]


# The control section each question depends on (None: no control step involved)
CONTROL = {
    "Customer lost their card, what do I do?": "CIR-CARD-07-v2-s5.2",
    "Can the customer sign the blocking form after I block the card?": "CIR-CARD-07-v2-s5.2",
    "Can a relative collect a new card for the customer?": "CIR-CARD-05-v3-s5.6",
    "Can I open an account with an expired passport?": "CIR-ACC-10-v4-s5.1",
    "What documents does a sole proprietor need?": "CIR-ACC-12-v2-s5.2",
    "Can a customer change their phone number by calling the contact centre?": "CIR-ACC-15-v2-s5.4",
    "The customer's SIM card is registered in his wife's name. Can I enrol him for SIM banking?": "CIR-DIG-03-v2-s5.2",
    "Can I reset an internet banking password over the phone?": "CIR-DIG-04-v1-s5.5",
    "What is the maximum debt service ratio for a loan?": "CIR-CRD-21-v3-s5.4",
    "Mteja amepoteza kadi, nifanye nini?": "CIR-CARD-07-v2-s5.2",
    "Je, nahitaji fomu ya kuzuia kadi kabla ya kuifunga?": "CIR-CARD-07-v2-s5.2",
    "Mfanyabiashara binafsi anahitaji nyaraka gani kufungua akaunti?": "CIR-ACC-12-v2-s5.2",
    "Mteja anataka kubadilisha namba ya simu kwa kupiga simu, inaruhusiwa?": "CIR-ACC-15-v2-s5.4",
    "Mteja amesahau nenosiri la benki ya mtandaoni, nifanye nini?": "CIR-DIG-04-v1-s5.5",
    "Meneja wa tawi anaweza kuidhinisha mkopo hadi kiasi gani?": "CIR-CRD-21-v3-s5.7",
}


def evaluate(retriever, live):
    rows = []
    for q, lang, expected in CASES:
        retrieved, added = k.gather(q, live, retriever)
        hits = [s.sid for s, _ in retrieved]
        rank = next((n for n, h in enumerate(hits, 1) if h in expected), None)
        ctrl = CONTROL.get(q)
        rows.append(dict(retriever=retriever.name, language=lang, question=q, expected="; ".join(expected),
                         rank=rank or "", hit_at_5="Yes" if rank else "No",
                         control_section=ctrl or "",
                         control_in_top_5=("Yes" if ctrl in hits else "No") if ctrl else "",
                         control_given=("Yes" if ctrl in hits + [s.sid for s in added] else "No") if ctrl else "",
                         top_5="; ".join(hits), controls_added="; ".join(s.sid for s in added)))
    return rows


def main():
    k.load_dotenv()
    live = k.live_sections(k.load_library())
    retrievers = [k.KeywordRetriever()]
    if os.environ.get("PINECONE_API_KEY"):
        try:
            retrievers.append(k.PineconeRetriever())
        except Exception as e:
            print(f"Pinecone could not be reached ({type(e).__name__}); check the key and internet connection.")
    rows = []
    for r in retrievers:
        res = evaluate(r, live)
        rows += res
        print(r.name)
        for lang in ("en", "sw"):
            sub = [x for x in res if x["language"] == lang]
            ctl = [x for x in sub if x["control_section"]]
            print(f"  {lang}: answer found in top 5 {sum(x['hit_at_5'] == 'Yes' for x in sub)}/{len(sub)}"
                  f" | control in top 5 {sum(x['control_in_top_5'] == 'Yes' for x in ctl)}/{len(ctl)}"
                  f" | control given to Claude after completion {sum(x['control_given'] == 'Yes' for x in ctl)}/{len(ctl)}")
    os.makedirs(k.LOG_DIR, exist_ok=True)
    with open(os.path.join(k.LOG_DIR, "retrieval_eval.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    if len(retrievers) == 1:
        print("Add PINECONE_API_KEY to .env and run app/sync_index.py to compare with Pinecone.")


if __name__ == "__main__":
    main()
