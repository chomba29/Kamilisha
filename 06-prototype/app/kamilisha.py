"""Kamilisha engine: answers branch procedure questions from Live circulars only (RAG).

Retrieval-augmented generation: each question first retrieves the 5 closest Live circular
sections (Pinecone semantic search, or a local keyword search when no Pinecone key is set).
Control completion then adds every mandatory-control section of each circular retrieved, so a
control step never depends on search ranking (guardrail G-13), and procedure completion adds
every procedure step of the best-matching circular, so an answer is never missing a step such
as capturing the request or the fee (DEF-003). Claude answers from those sections only. The model writes the steps; everything that must be exact comes from the library, not the
model: citations, version, page, control flags, the circular's own wording on control
steps and the "changed on" flag. If the model cites anything outside the Live library,
the answer is replaced by "not found" (fail-safe).

Command line:  python kamilisha.py "Customer lost their card, what do I do?"
"""
import csv, json, math, os, re, sys
from dataclasses import dataclass, field
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRARY_DIR = os.path.join(ROOT, "library")
LOG_DIR = os.path.join(ROOT, "logs")
MODEL = os.environ.get("KAMILISHA_MODEL", "claude-sonnet-5-5")
RECENT_DAYS = 90                                     # "changed on" window (data requirements)
TOP_K = 5                                            # sections retrieved per question
INDEX_NAME = os.environ.get("KAMILISHA_INDEX", "kamilisha-circulars")
NAMESPACE = "live"
NOT_FOUND_EN = "Not found in the current circulars. Ask your supervisor."
NOT_FOUND_SW = "Haikupatikana katika nyaraka za sasa. Muulize msimamizi wako."


# ---------------------------------------------------------------- library (PDF ingestion)
@dataclass
class Section:
    sid: str            # e.g. CIR-CARD-07-v2-s5.2, CIR-CARD-07-v2-appA, CIR-CARD-07-v2-faqQ2
    circular: str       # e.g. CIR-CARD-07
    title: str
    version: int
    status: str
    effective: date
    owner: str
    number: str         # "5.2", "A" (appendix) or "Q2" (FAQ)
    heading: str
    page: int
    control: bool
    text: str

    @property
    def label(self):
        if self.number.startswith("Q"):
            return f"FAQ {self.number}"
        if self.number.isalpha():
            return f"Appendix {self.number}"
        return f"section {self.number}"

    @property
    def citation(self):
        return f"{self.circular} v{self.version}, {self.label}, page {self.page}"


HEADINGS = [                                           # how headings appear in the PDF text
    ("sec", re.compile(r"^(\d+\.\d+) ([A-Z].*)$")),     # 5.2 Obtain the signed card-blocking form
    ("sec", re.compile(r"^(\d+)\. ([A-Z][^.]*)$")),       # 6. Exceptions and escalation
    ("app", re.compile(r"^Appendix ([A-Z]): (.+)$")),     # Appendix A: Form CB-01 ...
    ("faq", re.compile(r"^(Q\d+)\. (.+)$")),             # Q2. Can the customer sign ...?
]
NOISE = re.compile(r"^(Internal · |Fictional document for a portfolio project|Mfano Bank \(fictional\) · |"
                   r"Page \d+ of \d+$|SUPERSEDED$)")
CONTROL_TAG = "[MANDATORY CONTROL]"


def _heading(line):
    for kind, rx in HEADINGS:
        m = rx.match(line)
        if m:
            return kind, m.group(1), m.group(2)
    return None


def parse_pdf(path, meta):
    """Split one circular PDF into sections, keeping the page where each section starts.
    The cover, document control and contents pages are skipped."""
    from pypdf import PdfReader
    pages = [p.extract_text() or "" for p in PdfReader(path).pages]
    start = next(i for i, t in enumerate(pages) if t.lstrip().startswith("Contents")) + 1
    sections, cur = [], None
    for pno in range(start, len(pages)):
        lines = [l.strip() for l in pages[pno].splitlines()]
        i = 0
        while i < len(lines):
            line = lines[i]
            i += 1
            if not line or NOISE.match(line):
                continue
            h = _heading(line)
            if h:
                kind, num, head = h
                # a heading that wraps onto a second line (long FAQ or control tag)
                while i < len(lines) and ((kind == "faq" and not head.endswith("?")) or
                                          ("[MANDATORY" in head and not head.endswith("]"))):
                    head += " " + lines[i]; i += 1
                cur = dict(num=num, head=head, page=pno + 1, lines=[])
                sections.append(cur)
            elif cur is not None:
                item = re.sub(r"^[^\w(\"']+", "", line)             # drop bullet and checkbox marks
                cur["lines"].append(("• " + item) if item != line else item)
    out = []
    for c in sections:
        text = " ".join(l for l in c["lines"] if l)
        if not text:
            continue                                   # e.g. "5. Procedure" with only subsections
        control = CONTROL_TAG in c["head"]
        num = c["num"]
        key = f"faq{num}" if num.startswith("Q") else (f"app{num}" if num.isalpha() else f"s{num}")
        out.append(Section(
            sid=f"{meta['id']}-v{meta['version']}-{key}", circular=meta["id"], title=meta["title"],
            version=int(meta["version"]), status=meta["status"],
            effective=date.fromisoformat(meta["effective_date"]), owner=meta["owner"], number=num,
            heading=c["head"].replace(CONTROL_TAG, "").strip(), page=c["page"], control=control,
            text=" ".join(text.split())))
    return out


_CACHE = {}


def load_library(folder=LIBRARY_DIR):
    """Read the document register and every circular PDF it lists. Returns all sections,
    Live and Superseded. Cached until a file changes."""
    reg_path = os.path.join(folder, "register.csv")
    register = list(csv.DictReader(open(reg_path, encoding="utf-8")))
    stamp = tuple(os.path.getmtime(os.path.join(folder, r["file"])) for r in register) + (os.path.getmtime(reg_path),)
    if _CACHE.get(folder, (None,))[0] != stamp:
        sections = []
        for meta in register:
            sections += parse_pdf(os.path.join(folder, meta["file"]), meta)
        _CACHE[folder] = (stamp, sections)
    return list(_CACHE[folder][1])


def live_sections(sections, paused=()):
    """G-03 and G-11: only Live circulars, minus any procedure switched off."""
    return [s for s in sections if s.status == "Live" and s.circular not in paused]


# ---------------------------------------------------------------- personal data (G-06)
PATTERNS = [
    ("email address", r"[\w.+-]+@[\w-]+\.[\w.]+"),
    ("national ID number", r"\b\d{8}-\d{5}-\d{5}-\d{2}\b"),
    ("card number", r"\b(?:\d[ -]?){13,19}\b"),
    ("phone number", r"(?:\+255|\b0)[67]\d{8}\b"),
    ("account number", r"\b\d{8,12}\b"),
]


def mask_personal_data(text):
    found = []
    for label, pat in PATTERNS:
        text, n = re.subn(pat, "[MASKED]", text)
        if n:
            found.append(label)
    return text, found


# ---------------------------------------------------------------- retrieval (RAG)
def section_text(s):
    """The text that is embedded and searched for one section."""
    return f"{s.title} ({s.circular}). {s.label}: {s.heading}. {s.text}"


class AllSections:
    """Baseline with no retrieval: every Live section. Used in offline tests."""
    name = "all sections (no retrieval)"

    def search(self, question, live, k=TOP_K):
        return [(s, 1.0) for s in live]


class KeywordRetriever:
    """Local BM25 keyword search. Fallback when no Pinecone key is set; English words only."""
    name = "keyword search (BM25, local)"
    STOP = set("a an and are as at be before by can do does for from how i if in is it must of on or the to what when "
               "which who with without my your their they this that there".split())

    @classmethod
    def tokens(cls, text):
        return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in cls.STOP]

    def search(self, question, live, k=TOP_K, k1=1.5, b=0.75):
        docs = [self.tokens(section_text(s)) for s in live]
        if not docs:
            return []
        avg = sum(map(len, docs)) / len(docs)
        q = set(self.tokens(question))
        scored = []
        for s, d in zip(live, docs):
            score = 0.0
            for t in q:
                n = sum(t in x for x in docs)
                tf = d.count(t)
                if tf:
                    idf = math.log(1 + (len(docs) - n + 0.5) / (n + 0.5))
                    score += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(d) / avg))
            if score > 0:
                scored.append((s, round(score, 3)))
        return sorted(scored, key=lambda x: -x[1])[:k]


class PineconeRetriever:
    """Semantic search in Pinecone with the hosted multilingual-e5-large model, so a Swahili
    question can find an English section. Only ids that are Live (and not paused) in the local
    library are kept, so a stale index can never bring back an old version."""
    name = "Pinecone semantic search (multilingual-e5-large)"

    def __init__(self, index=None):
        if index is None:
            from pinecone import Pinecone
            index = Pinecone(api_key=os.environ["PINECONE_API_KEY"]).Index(INDEX_NAME)
        self.index = index

    def search(self, question, live, k=TOP_K):
        by_id = {s.sid: s for s in live}
        res = self.index.search(namespace=NAMESPACE, inputs={"text": question}, top_k=k * 3, fields=["circular"])
        hits = [(by_id[h.id], round(h.score, 3)) for h in res.result.hits if h.id in by_id]
        return hits[:k]


def complete_controls(retrieved, live):
    """G-13 control completion: for every circular among the retrieved sections, add its
    mandatory-control sections that search did not return. Returns the sections added."""
    have = {s.sid for s, _ in retrieved}
    circulars = {s.circular for s, _ in retrieved}
    return [s for s in live if s.circular in circulars and s.control and s.sid not in have]


def complete_procedure(retrieved, live, have):
    """DEF-003 procedure completion: every procedure step (section 5.x) of the best-matching
    circular, so a "what do I do" answer can give the whole procedure. Returns sections not in have."""
    if not retrieved:
        return []
    top = retrieved[0][0].circular
    return [s for s in live if s.circular == top and s.number.startswith("5.") and s.sid not in have]


def gather(question, live, retriever):
    """Retrieve, then complete controls. Returns (retrieved with scores, controls added)."""
    retrieved = retriever.search(question, live)
    return retrieved, complete_controls(retrieved, live)


def get_retriever():
    """Pinecone when PINECONE_API_KEY is set; otherwise the local keyword search."""
    load_dotenv()
    if os.environ.get("PINECONE_API_KEY"):
        try:
            return PineconeRetriever()
        except Exception as e:                                   # fall back rather than fail
            print(f"Pinecone unavailable ({type(e).__name__}); using keyword search.", file=sys.stderr)
    return KeywordRetriever()


# ---------------------------------------------------------------- model call
SYSTEM = """You are Kamilisha, a staff-facing assistant for branch staff of Mfano Bank (a fictional bank).
You answer questions about bank procedures and staff policies using ONLY the circular sections given
in <library>. Rules:
1. Never use outside knowledge. If the sections do not answer the question, return status "not_found".
2. Write short, plain-language steps (at most 25 words each), in the order the circular requires.
   Answer in Swahili if the question is in Swahili, otherwise in English (field "language": "sw" or "en").
3. Every step must cite exactly one section_id it comes from. Use only section_ids from <library>.
4. If the user asks how to skip, delay, reorder or work around a step in a section marked control="yes",
   return status "declined" and put the relevant control rule(s) in "steps".
5. If the answer depends on a fact the user did not give (for example the type of business), return
   status "need_info" with one short "clarifying_question" and the choices in "options". Leave "steps" empty.
6. You advise only. Never approve, decide or say an exception is allowed.
7. Never ask for customer personal data. "[MASKED]" means data was removed; do not try to restore it.
8. When explaining how to carry out a procedure, include every section marked control="yes" that applies
   to the situation, in the circular's order. Cite the procedure section itself (for example 5.2), not an
   appendix or FAQ that repeats it.
9. When the user asks what to do or how to handle a case, give the complete procedure from start to finish,
   in the circular's order, including steps that are not controls, such as capturing the request, fees and
   authorisation. When the user asks one specific thing (a fee, a limit, a yes or no), answer only that.
10. Combine closely related sentences into one step. Use at most 10 steps.
For not_found and need_info, "steps" is empty. Leave unused text fields as empty strings."""

SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["answered", "not_found", "declined", "need_info"]},
        "language": {"type": "string", "enum": ["en", "sw"]},
        "clarifying_question": {"type": "string"},
        "options": {"type": "array", "items": {"type": "string"}},
        "steps": {"type": "array", "items": {
            "type": "object",
            "properties": {"text": {"type": "string"}, "section_id": {"type": "string"}},
            "required": ["text", "section_id"], "additionalProperties": False}},
    },
    "required": ["status", "language", "clarifying_question", "options", "steps"],
    "additionalProperties": False,
}


def library_block(sections):
    return "<library>\n" + "\n".join(
        f'<section id="{s.sid}" circular="{s.circular}" title="{s.title}" version="{s.version}" '
        f'part="{s.label}" control="{"yes" if s.control else "no"}">{s.heading}. {s.text}</section>' for s in sections
    ) + "\n</library>"


def load_dotenv(path=os.path.join(ROOT, ".env")):
    """Minimal .env reader so the key never has to be typed into code or chat."""
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class AnswerTooLong(Exception):
    """Claude's reply hit max_tokens and was cut off, so it is not valid JSON. Fails safe to not_found."""


def claude_model(question, sections):
    """Call Claude with structured JSON output. Returns the parsed dict."""
    import anthropic
    load_dotenv()
    client = anthropic.Anthropic()          # reads ANTHROPIC_API_KEY from the environment
    resp = client.messages.create(
        model=MODEL, max_tokens=4000, system=SYSTEM,          # full procedures in Swahili need room (UAT run 2)
        messages=[{"role": "user", "content": f"{library_block(sections)}\n\n<question>{question}</question>"}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
    )
    if resp.stop_reason == "max_tokens":
        raise AnswerTooLong("reply cut off at max_tokens")
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text)


# ---------------------------------------------------------------- answer
@dataclass
class Step:
    text: str
    section: Section

    @property
    def control(self):
        return self.section.control


@dataclass
class Answer:
    question: str                 # as logged (masked)
    status: str                   # answered | not_found | declined | need_info
    language: str
    steps: list = field(default_factory=list)
    clarifying_question: str = ""
    options: list = field(default_factory=list)
    masked: list = field(default_factory=list)
    changed: list = field(default_factory=list)      # (citation, effective date) within RECENT_DAYS
    retrieved: list = field(default_factory=list)    # (Section, score) found by search
    controls_added: list = field(default_factory=list)  # Section: added by control completion (G-13)
    steps_added: list = field(default_factory=list)     # Section: added by procedure completion (DEF-003)
    retriever: str = ""
    note: str = ""

    @property
    def citations(self):
        seen = []
        for st in self.steps:
            if st.section.citation not in seen:
                seen.append(st.section.citation)
        return seen

    @property
    def answer_text(self):
        """What the staff member was told, for the log."""
        if self.status == "not_found":
            return self.not_found_text
        if self.status == "need_info":
            return self.clarifying_question + (" Options: " + "; ".join(self.options) if self.options else "")
        return " | ".join(f"{i}. {st.text}" + (" [CONTROL]" if st.control else "")
                          for i, st in enumerate(self.steps, 1))

    @property
    def not_found_text(self):
        return NOT_FOUND_EN if self.language == "en" else f"{NOT_FOUND_SW}\n({NOT_FOUND_EN})"


def build_answer(raw, question, live, masked, today):
    """Validate the model output against the Live library. Fail safe to not_found."""
    by_id = {s.sid: s for s in live}
    status, lang = raw.get("status"), raw.get("language", "en")
    if lang not in ("en", "sw"):
        lang = "en"
    ans = Answer(question=question, status=status, language=lang, masked=masked)
    if status == "need_info":
        q = (raw.get("clarifying_question") or "").strip()
        if not q:
            ans.status = "not_found"
        ans.clarifying_question, ans.options = q, [o for o in raw.get("options", []) if o.strip()]
        return ans
    if status in ("answered", "declined"):
        steps = raw.get("steps") or []
        if not steps or any(st.get("section_id") not in by_id for st in steps):
            ans.status, ans.note = "not_found", "Model cited a section outside the Live library; answer withheld."
            return ans
        ans.steps = [Step(st["text"].strip(), by_id[st["section_id"]]) for st in steps]
        for st in ans.steps:
            age = (today - st.section.effective).days
            if 0 <= age <= RECENT_DAYS and (st.section.circular, st.section.effective) not in ans.changed:
                ans.changed.append((st.section.circular, st.section.effective))
        return ans
    ans.status = "not_found"
    return ans


def ask(question, branch="Pilot 1", role="Customer service officer", model=None, retriever=None,
        library=None, paused=(), today=None, log=True):
    """Full pipeline: mask -> retrieve top Live sections -> model -> validate -> log."""
    today = today or date.today()
    model = model or claude_model
    retriever = retriever or get_retriever()
    sections = library if library is not None else load_library()
    live = live_sections(sections, paused)
    q_masked, found = mask_personal_data(question)
    note = ""
    try:
        retrieved, added = gather(q_masked, live, retriever)
    except Exception as e:                            # search failure: fail safe
        retrieved, added, note = [], [], f"Search error: {type(e).__name__}"
    steps = complete_procedure(retrieved, live, {s.sid for s, _ in retrieved} | {s.sid for s in added})
    candidates = [s for s, _ in retrieved] + added + steps
    if not candidates:
        raw = {"status": "not_found", "language": "en"}
    else:
        try:
            raw = model(q_masked, candidates)
        except Exception as e:                        # model or network failure: fail safe
            raw = {"status": "not_found", "language": "en"}
            note = f"Service error: {type(e).__name__}"
    ans = build_answer(raw, q_masked, candidates, found, today)
    ans.retrieved, ans.controls_added, ans.steps_added, ans.retriever = retrieved, added, steps, retriever.name
    ans.note = ans.note or note
    if log:
        write_log(ans, branch, role)
    return ans


# ---------------------------------------------------------------- logging (BR-08, G-12)
LOG_FIELDS = ["timestamp", "branch", "role", "language", "question_masked", "status", "answer",
              "circulars_cited", "sections_retrieved", "controls_added", "steps_added", "retriever",
              "personal_data_masked", "note"]


def write_log(ans, branch, role, folder=LOG_DIR):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "question_log.csv")
    if os.path.exists(path):                          # log written by an older version: keep it aside
        with open(path, encoding="utf-8") as f:
            header = f.readline().strip().split(",")
        if header != LOG_FIELDS:
            os.replace(path, os.path.join(folder, f"question_log_before_{datetime.now():%Y%m%d_%H%M%S}.csv"))
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LOG_FIELDS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerow(dict(timestamp=datetime.now().isoformat(timespec="seconds"), branch=branch, role=role,
                        language=ans.language, question_masked=ans.question, status=ans.status,
                        answer=ans.answer_text, circulars_cited="; ".join(ans.citations),
                        sections_retrieved="; ".join(f"{sec.sid} ({sc})" for sec, sc in ans.retrieved),
                        controls_added="; ".join(s.sid for s in ans.controls_added),
                        steps_added="; ".join(s.sid for s in ans.steps_added), retriever=ans.retriever, personal_data_masked=", ".join(ans.masked), note=ans.note))


def write_feedback(ans, branch, folder=LOG_DIR):
    """BR-12: 'Wrong or unclear' goes to each cited procedure owner's queue."""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "feedback_log.csv")
    new = not os.path.exists(path)
    owners = sorted({st.section.owner for st in ans.steps}) or ["Data Management Office"]
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["timestamp", "branch", "owner_queue", "question_masked",
                                          "status", "circulars_cited", "answer"], lineterminator="\n")
        if new:
            w.writeheader()
        for o in owners:
            w.writerow(dict(timestamp=datetime.now().isoformat(timespec="seconds"), branch=branch, owner_queue=o,
                            question_masked=ans.question, status=ans.status,
                            circulars_cited="; ".join(ans.citations),
                            answer=" | ".join(st.text for st in ans.steps) or ans.clarifying_question))


# ---------------------------------------------------------------- plain-text rendering (CLI)
def render_text(ans):
    out = []
    if ans.masked:
        out.append(f"Reminder: do not enter customer details. Removed: {', '.join(ans.masked)}.")
    if ans.status == "not_found":
        out.append(ans.not_found_text)
    elif ans.status == "need_info":
        out.append(ans.clarifying_question)
        out += [f"  - {o}" for o in ans.options]
    else:
        if ans.status == "declined":
            out.append("I can't help with skipping or changing a control. The current rule is:")
        for i, st in enumerate(ans.steps, 1):
            out.append(f"{i}. {st.text}" + ("   [CONTROL]" if st.control else ""))
            if st.control:
                out.append(f"     Circular wording: \"{st.section.text}\"")
        for circ, eff in ans.changed:
            out.append(f"Changed on {eff.day} {eff.strftime('%b %Y')}: {circ}")
        out.append("Source: " + "; ".join(ans.citations))
    return "\n".join(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: python kamilisha.py "your question"')
    print(render_text(ask(" ".join(sys.argv[1:]))))
