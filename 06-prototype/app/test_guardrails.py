"""Offline guardrail tests: no API key needed. A fake model stands in for Claude, so these
check the code around the model: library rules, citations, masking, fail-safes, logging.
Run:  python app/test_guardrails.py      (or: pytest app/test_guardrails.py)
"""
import os, sys, tempfile
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kamilisha as k

LIB = k.load_library()
SEC = {s.sid: s for s in LIB}
TODAY = date(2026, 10, 23)


def fake(raw):
    """A stand-in model that returns a fixed reply and records what it was shown."""
    def model(question, sections):
        model.seen_q, model.seen = question, [s.sid for s in sections]
        return raw
    return model


def run(raw, q="test question", paused=(), retriever=None):
    m = fake(raw)
    return k.ask(q, model=m, retriever=retriever or k.AllSections(), library=LIB, paused=paused,
                 today=TODAY, log=False), m


def test_library_loads_fifteen_pdfs():
    assert len({(s.circular, s.version) for s in LIB}) == 15 and len({s.circular for s in LIB}) == 12


def test_only_live_versions_reach_the_model():                         # G-03, BR-04
    _, m = run({"status": "not_found", "language": "en"})
    assert m.seen and all(SEC[sid].status == "Live" for sid in m.seen)
    assert not any(sid.startswith("CIR-CARD-07-v1") for sid in m.seen)


def test_citation_comes_from_library_not_model():                       # BR-02
    ans, _ = run({"status": "answered", "language": "en", "steps": [
        {"text": "Get the signed blocking form.", "section_id": "CIR-CARD-07-v2-s5.2"}]})
    page = SEC["CIR-CARD-07-v2-s5.2"].page
    assert page > 3 and ans.citations == [f"CIR-CARD-07 v2, section 5.2, page {page}"]


def test_unknown_section_fails_safe_to_not_found():                     # G-04
    ans, _ = run({"status": "answered", "language": "en", "steps": [
        {"text": "Invented step.", "section_id": "CIR-XYZ-99-v1-s1"}]})
    assert ans.status == "not_found" and not ans.steps


def test_superseded_section_is_rejected():                              # BR-04
    ans, _ = run({"status": "answered", "language": "en", "steps": [
        {"text": "Block without a form.", "section_id": "CIR-CARD-07-v1-s5.2"}]})
    assert ans.status == "not_found"


def test_answer_without_steps_fails_safe():
    ans, _ = run({"status": "answered", "language": "en", "steps": []})
    assert ans.status == "not_found"


def test_control_flag_and_exact_wording_come_from_library():            # G-07, BR-09
    ans, _ = run({"status": "answered", "language": "en", "steps": [
        {"text": "Check ID.", "section_id": "CIR-CARD-07-v2-s5.1"},
        {"text": "Capture the request.", "section_id": "CIR-CARD-07-v2-s5.4"}]})
    assert [s.control for s in ans.steps] == [True, False]
    assert "Form CB-01" not in ans.steps[0].section.text and "original identity document" in ans.steps[0].section.text


def test_changed_on_flag_within_90_days():                              # BR-10
    card, _ = run({"status": "answered", "language": "en", "steps": [{"text": "x", "section_id": "CIR-CARD-07-v2-s5.2"}]})
    leave, _ = run({"status": "answered", "language": "en", "steps": [{"text": "x", "section_id": "HR-POL-03-v2-s5.2"}]})
    assert card.changed == [("CIR-CARD-07", date(2026, 9, 1))] and leave.changed == []


def test_personal_data_masked_before_model():                           # G-06, BR-07
    _, m = run({"status": "not_found", "language": "en"},
               q="Customer 0754123456, account 01523344556, card 4111 1111 1111 1111, mail a.b@x.co")
    assert "0754123456" not in m.seen_q and "01523344556" not in m.seen_q and "4111" not in m.seen_q
    assert "a.b@x.co" not in m.seen_q and m.seen_q.count("[MASKED]") == 4


def test_ordinary_numbers_not_masked():
    masked, found = k.mask_personal_data("Fee is TZS 10,000 and notice is 7 days from 2026-09-01")
    assert found == [] and "10,000" in masked


def test_declined_keeps_the_control_rule():                             # G-05, BR-06
    ans, _ = run({"status": "declined", "language": "en", "steps": [
        {"text": "The signed form must come before blocking.", "section_id": "CIR-CARD-07-v2-s5.2"}]})
    assert ans.status == "declined" and ans.steps[0].control


def test_need_info_requires_a_question():                               # BR-11
    ok, _ = run({"status": "need_info", "language": "en", "clarifying_question": "Which type of business?",
                 "options": ["Sole proprietor", "Partnership", "Company"], "steps": []})
    empty, _ = run({"status": "need_info", "language": "en", "clarifying_question": " ", "steps": []})
    assert ok.status == "need_info" and len(ok.options) == 3 and empty.status == "not_found"


def test_paused_procedure_is_hidden():                                  # G-11
    _, m = run({"status": "not_found", "language": "en"}, paused=("CIR-CARD-07",))
    assert m.seen and not any(sid.startswith("CIR-CARD-07") for sid in m.seen)


def test_swahili_not_found_shows_both_languages():                      # BR-03, BR-05
    ans, _ = run({"status": "not_found", "language": "sw"})
    assert k.NOT_FOUND_SW in ans.not_found_text and k.NOT_FOUND_EN in ans.not_found_text


def test_model_failure_fails_safe():
    def broken(q, s):
        raise ConnectionError("no network")
    ans = k.ask("anything", model=broken, retriever=k.AllSections(), library=LIB, today=TODAY, log=False)
    assert ans.status == "not_found" and "ConnectionError" in ans.note


# ---------------------------------------------------------------- PDF ingestion
def test_every_source_heading_is_found_in_its_pdf():
    """Every numbered section, appendix and FAQ in the source appears as a chunk from the PDF."""
    import glob, re
    src_dir = os.path.join(k.LIBRARY_DIR, "source")
    for path in glob.glob(os.path.join(src_dir, "*.md")):
        raw = open(path, encoding="utf-8").read()
        meta = dict(l.split(":", 1) for l in raw.split("---")[1].strip().splitlines())
        cid, ver = meta["id"].strip(), int(meta["version"])
        got = {s.number for s in LIB if s.circular == cid and s.version == ver}
        body = raw.split("---", 2)[2]
        want = set(re.findall(r"^### (\d+\.\d+|Q\d+)", body, re.M)) | {"7", "8", "9"}
        want |= {a for a, t in re.findall(r"^## Appendix ([A-Z]): (.+)$", body, re.M) if "questions" not in t}
        assert want <= got, (cid, ver, sorted(want - got))


def test_pages_and_controls_come_from_the_pdf():
    s = SEC["CIR-CARD-07-v2-s5.2"]
    assert s.control and s.heading == "Obtain the signed card-blocking form" and 4 <= s.page <= 7
    assert not SEC["CIR-CARD-07-v2-s5.4"].control


def test_no_headers_footers_or_watermark_in_text():
    for s in LIB:
        assert "Page " not in s.text and "SUPERSEDED" not in s.text and "Fictional document" not in s.text, s.sid


def test_register_matches_pdfs():
    import csv
    reg = list(csv.DictReader(open(os.path.join(k.LIBRARY_DIR, "register.csv"), encoding="utf-8")))
    live = [r for r in reg if r["status"] == "Live"]
    assert len(reg) == 15 and len(live) == 12 and all(os.path.exists(os.path.join(k.LIBRARY_DIR, r["file"])) for r in reg)


# ---------------------------------------------------------------- retrieval (RAG)
class FakeHit:
    def __init__(self, id, score): self.id, self.score = id, score


class FakeIndex:
    """Stands in for a Pinecone index: returns fixed hits, including stale and paused ids."""
    def __init__(self, ids): self.ids = ids
    def search(self, namespace, inputs, top_k, fields):
        FakeIndex.called_with = (namespace, inputs, top_k)
        hits = [FakeHit(i, 0.9 - n / 100) for n, i in enumerate(self.ids)]
        return type("R", (), {"result": type("H", (), {"hits": hits})()})()


def test_model_sees_only_retrieved_sections_plus_their_controls():
    ans, m = run({"status": "not_found", "language": "en"}, q="What is the card replacement fee?",
                 retriever=k.KeywordRetriever())
    found = [s.sid for s, _ in ans.retrieved]
    assert 0 < len(found) <= k.TOP_K and "CIR-CARD-07-v2-s5.4" in found
    assert m.seen == found + [s.sid for s in ans.controls_added] + [s.sid for s in ans.steps_added]
    assert all(s.control and s.circular in {SEC[x].circular for x in found} for s in ans.controls_added)


def test_control_completion_adds_the_missing_blocking_form():           # G-13, defect found live
    idx = FakeIndex(["CIR-CARD-07-v2-faqQ3", "CIR-CARD-07-v2-s5.1", "CIR-CARD-07-v2-s5.3",
                     "CIR-CARD-07-v2-s5.7", "CIR-CARD-07-v2-appA"])    # the top 5 Pinecone returned live
    ans, m = run({"status": "not_found", "language": "en"}, q="Customer lost their card, what do I do",
                 retriever=k.PineconeRetriever(idx))
    assert "CIR-CARD-07-v2-s5.2" in m.seen and [s.sid for s in ans.controls_added] == ["CIR-CARD-07-v2-s5.2"]


def test_procedure_completion_adds_capture_fee_and_authorisation():   # DEF-003
    idx = FakeIndex(["CIR-CARD-07-v2-faqQ3", "CIR-CARD-07-v2-s5.1", "CIR-CARD-07-v2-s5.3",
                     "CIR-CARD-07-v2-s5.7", "CIR-CARD-07-v2-appA"])    # the top 5 Pinecone returned live
    ans, m = run({"status": "not_found", "language": "en"}, q="Customer lost their card, what do I do",
                 retriever=k.PineconeRetriever(idx))
    added = [s.sid for s in ans.steps_added]
    assert added == ["CIR-CARD-07-v2-s5.4", "CIR-CARD-07-v2-s5.5", "CIR-CARD-07-v2-s5.6"]
    assert len(m.seen) == len(set(m.seen))                              # nothing given twice


def test_procedure_completion_uses_only_the_best_match():
    idx = FakeIndex(["HR-POL-03-v2-s5.2", "CIR-CARD-07-v2-s5.1"])
    ans, _ = run({"status": "not_found", "language": "en"}, q="leave", retriever=k.PineconeRetriever(idx))
    assert ans.steps_added and all(s.circular == "HR-POL-03" and s.number.startswith("5.") for s in ans.steps_added)


def test_control_completion_stays_within_retrieved_circulars():
    idx = FakeIndex(["HR-POL-03-v2-s5.2"])
    ans, m = run({"status": "not_found", "language": "en"}, q="leave", retriever=k.PineconeRetriever(idx))
    assert [s.sid for s in ans.controls_added] == ["HR-POL-03-v2-s5.3"]
    assert not any(sid.startswith("CIR-") for sid in m.seen)                # procedure steps also HR-POL-03 only


def test_answer_may_cite_an_added_control():
    idx = FakeIndex(["CIR-CARD-07-v2-s5.1"])
    ans, _ = run({"status": "answered", "language": "en", "steps": [
        {"text": "Get Form CB-01 signed first.", "section_id": "CIR-CARD-07-v2-s5.2"}]},
        q="lost card", retriever=k.PineconeRetriever(idx))
    assert ans.status == "answered" and ans.steps[0].control


def test_answer_must_cite_a_retrieved_section():
    ans, _ = run({"status": "answered", "language": "en", "steps": [
        {"text": "Leave notice is 7 days.", "section_id": "HR-POL-03-v2-s5.2"}]},
        q="What is the card replacement fee?", retriever=k.KeywordRetriever())
    assert ans.status == "not_found"                     # Live, but not among the sections retrieved


def test_pinecone_hits_are_filtered_to_live_and_not_paused():
    idx = FakeIndex(["CIR-CARD-07-v1-s5.2", "CIR-CARD-07-v2-s5.2", "OLD-DELETED-s1", "HR-POL-03-v2-s5.2"])
    live = k.live_sections(LIB, paused=("HR-POL-03",))
    hits = k.PineconeRetriever(idx).search("Mteja amepoteza kadi", live)
    assert [s.sid for s, _ in hits] == ["CIR-CARD-07-v2-s5.2"]
    assert FakeIndex.called_with == (k.NAMESPACE, {"text": "Mteja amepoteza kadi"}, k.TOP_K * 3)


def test_nothing_retrieved_means_not_found_without_calling_model():
    called = []
    ans = k.ask("zzz qqq", model=lambda q, s: called.append(1), retriever=k.KeywordRetriever(),
                library=LIB, today=TODAY, log=False)
    assert ans.status == "not_found" and not called


def test_search_failure_fails_safe():
    class Broken:
        name = "broken"
        def search(self, q, live, k=5): raise TimeoutError()
    ans = k.ask("card", model=lambda q, s: {"status": "answered"}, retriever=Broken(),
                library=LIB, today=TODAY, log=False)
    assert ans.status == "not_found" and "TimeoutError" in ans.note


def test_log_records_answer_and_controls_added():
    with tempfile.TemporaryDirectory() as d:
        idx = FakeIndex(["CIR-CARD-07-v2-s5.1"])
        ans, _ = run({"status": "answered", "language": "en", "steps": [
            {"text": "Get Form CB-01 signed first.", "section_id": "CIR-CARD-07-v2-s5.2"}]},
            q="lost card", retriever=k.PineconeRetriever(idx))
        k.write_log(ans, "Pilot 1", "Teller", folder=d)
        import csv
        row = list(csv.DictReader(open(os.path.join(d, "question_log.csv"), encoding="utf-8")))[0]
        assert row["answer"] == "1. Get Form CB-01 signed first. [CONTROL]"
        assert "CIR-CARD-07-v2-s5.2" in row["controls_added"]


def test_old_format_log_is_kept_aside_not_mixed():
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "question_log.csv"), "w", encoding="utf-8").write("timestamp,branch\nx,y\n")
        ans, _ = run({"status": "not_found", "language": "en"})
        k.write_log(ans, "Pilot 1", "Teller", folder=d)
        files = sorted(os.listdir(d))
        assert len(files) == 2 and files[1].startswith("question_log_before_")
        assert open(os.path.join(d, "question_log.csv"), encoding="utf-8").readline().strip().split(",") == k.LOG_FIELDS


def test_log_records_retrieval():
    with tempfile.TemporaryDirectory() as d:
        ans, _ = run({"status": "not_found", "language": "en"}, q="card replacement fee",
                     retriever=k.KeywordRetriever())
        k.write_log(ans, "Pilot 1", "Teller", folder=d)
        row = open(os.path.join(d, "question_log.csv"), encoding="utf-8").read()
        assert "CIR-CARD-07-v2-s5.4" in row and "keyword search" in row


def test_log_has_no_staff_names_and_masks_data():                      # BR-08, G-12
    with tempfile.TemporaryDirectory() as d:
        ans, _ = run({"status": "not_found", "language": "en"}, q="account 01523344556")
        k.write_log(ans, "Pilot 1", "Teller", folder=d)
        text = open(os.path.join(d, "question_log.csv"), encoding="utf-8").read()
        assert "01523344556" not in text and "account number" in text
        assert "name" not in text.splitlines()[0]


if __name__ == "__main__":
    tests = [v for n, v in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t(); print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1; print(f"FAIL  {t.__name__} {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
