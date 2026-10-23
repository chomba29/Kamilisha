"""Build the fictional Mfano Bank circular library as intranet-style PDFs.

Reads every source file in library/source/ and writes:
  library/pdf/<ID>-v<version>.pdf   one PDF per circular version
  library/register.csv              the document register (version, status, dates, owner, pages)

Each PDF has a cover page, a document control page (version history and "what changed"),
a contents page, the body, standard sections 7-9 and appendices, with "Page X of Y" footers.
Superseded versions carry a SUPERSEDED watermark. Needs reportlab.
Run from the 06-prototype folder:  python library/build_library.py
"""
import csv, os, re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table,
                                TableStyle, KeepTogether)
from reportlab.platypus.tableofcontents import TableOfContents

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, "source"), os.path.join(HERE, "pdf")
INK, MUTED, BRAND, RED = colors.HexColor("#1f2a37"), colors.HexColor("#5b6675"), colors.HexColor("#0e5e6f"), colors.HexColor("#b42318")

S = {
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10.5, leading=15, textColor=INK, spaceAfter=7),
    "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=10.5, leading=15, textColor=INK,
                             leftIndent=14, bulletIndent=2, spaceAfter=4),
    "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=BRAND,
                         spaceBefore=14, spaceAfter=8, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=INK,
                         spaceBefore=10, spaceAfter=5, keepWithNext=1),
    "small": ParagraphStyle("small", fontName="Helvetica", fontSize=9, leading=12, textColor=MUTED),
    "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=9.5, leading=12.5, textColor=INK),
    "box": ParagraphStyle("box", fontName="Helvetica", fontSize=10.5, leading=15, textColor=INK),
}

STANDARD_SECTIONS = {
    7: ("Records and retention", "{retention} Records are kept in the branch file room or the document management "
        "system and destroyed only under the bank's records retention schedule. Records that are part of an open "
        "complaint, dispute, audit or investigation are kept until it is closed."),
    8: ("Monitoring and quality assurance", "Back office quality assurance reviews a sample of files every month "
        "against this {kind} and reports exceptions to the branch manager and to {owner}. Repeated exceptions at a "
        "branch are reported to the Head of Branch Operations. Internal audit may review compliance with this "
        "{kind} at any time."),
}


def parse_source(path):
    raw = open(path, encoding="utf-8").read()
    _, front, body = raw.split("---", 2)
    meta = {}
    for line in front.strip().splitlines():
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    entries = re.split(r";\s*(?=\d+\s*\|)", meta["history"])          # a ";" inside a change note is kept
    meta["history"] = [[c.strip() for c in h.split("|")] for h in entries]
    meta["related"] = [r.strip() for r in meta.get("related", "").split(";") if r.strip()]
    return meta, body.strip()


def inline(text):
    text = escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


class Doc(BaseDocTemplate):
    def __init__(self, path, meta, **kw):
        super().__init__(path, pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm, topMargin=24 * mm,
                         bottomMargin=22 * mm, title=f"{meta['id']} {meta['title']} v{meta['version']}",
                         author="Mfano Bank (fictional)", **kw)
        self.meta = meta
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.addPageTemplates([PageTemplate(id="p", frames=[frame])])

    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name in ("h1", "h2"):
            text = f.getPlainText()
            key = f"h{id(f)}"
            self.canv.bookmarkPage(key)
            self.notify("TOCEntry", (0 if f.style.name == "h1" else 1, text, self.page, key))


def numbered_canvas(meta):
    kind = "Staff policy" if meta["id"].startswith("HR-") else "Circular"

    class NumberedCanvas(rl_canvas.Canvas):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self._saved = []

        def showPage(self):
            self._saved.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._saved)
            for state in self._saved:
                self.__dict__.update(state)
                self.decorate(total)
                super().showPage()
            super().save()

        def decorate(self, total):
            w, h = A4
            self.setFont("Helvetica", 8)
            self.setFillColor(MUTED)
            self.drawString(22 * mm, h - 14 * mm, f"Internal · {kind} {meta['id']} · {meta['title']}")
            self.drawRightString(w - 22 * mm, h - 14 * mm, "Fictional document for a portfolio project")
            self.drawString(22 * mm, 12 * mm, f"Mfano Bank (fictional) · {meta['id']} v{meta['version']} · {meta['status']}")
            self.drawRightString(w - 22 * mm, 12 * mm, f"Page {self._pageNumber} of {total}")
            if meta["status"] != "Live":
                self.saveState()
                self.setFont("Helvetica-Bold", 64)
                self.setFillColor(colors.Color(0.7, 0.14, 0.09, alpha=0.12))
                self.translate(w / 2, h / 2)
                self.rotate(45)
                self.drawCentredString(0, 0, "SUPERSEDED")
                self.restoreState()
    return NumberedCanvas


def cover(meta):
    kind = "STAFF POLICY" if meta["id"].startswith("HR-") else "INTERNAL CIRCULAR"
    st = lambda size, bold=False, color=INK: ParagraphStyle("c", fontName="Helvetica-Bold" if bold else "Helvetica",
                                                           fontSize=size, leading=size * 1.3, textColor=color)
    rows = [["Reference", meta["id"]], ["Version", meta["version"]], ["Status", meta["status"]],
            ["Effective date", meta["effective_date"]], ["Owner", meta["owner"]],
            ["Approved by", meta["approved_by"]], ["Classification", "Internal"]]
    t = Table([[Paragraph(f"<b>{a}</b>", S["cell"]), Paragraph(escape(b), S["cell"])] for a, b in rows],
              colWidths=[45 * mm, 100 * mm])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#d0d5dd")),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    out = [Spacer(1, 30 * mm), Paragraph("MFANO BANK", st(26, True, BRAND)),
           Paragraph("A fictional bank for a portfolio project", st(10, color=MUTED)), Spacer(1, 25 * mm),
           Paragraph(kind, st(11, True, MUTED)), Paragraph(escape(meta["title"]), st(28, True)),
           Spacer(1, 10 * mm), t, Spacer(1, 20 * mm),
           Paragraph("This document is fictional. It does not describe the procedures of any real bank.", S["small"])]
    if meta["status"] != "Live":
        out.insert(5, Paragraph("SUPERSEDED: do not use. See the current version on the intranet.", st(12, True, RED)))
    return out + [PageBreak()]


def document_control(meta):
    hist = [[Paragraph("<b>Version</b>", S["cell"]), Paragraph("<b>Effective date</b>", S["cell"]),
             Paragraph("<b>Change</b>", S["cell"])]]
    hist += [[Paragraph(escape(v), S["cell"]), Paragraph(escape(d), S["cell"]), Paragraph(escape(c), S["cell"])]
             for v, d, c in meta["history"]]
    t = Table(hist, colWidths=[22 * mm, 32 * mm, 112 * mm], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f6")),
                           ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d0d5dd")),
                           ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    box = Table([[Paragraph(f"<b>What changed in version {meta['version']}:</b> {inline(meta['what_changed'])}",
                            S["box"])]], colWidths=[166 * mm])
    box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff8e6")),
                             ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#d9a400")),
                             ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                             ("LEFTPADDING", (0, 0), (-1, -1), 8)]))
    title = ParagraphStyle("dc", parent=S["h1"], spaceBefore=0)
    sub = ParagraphStyle("dch2", parent=S["h2"])          # not listed in the contents
    return [Paragraph("Document control", title), box, Spacer(1, 8 * mm),
            Paragraph("Version history", sub), t, Spacer(1, 6 * mm),
            Paragraph("Approval and distribution", sub),
            Paragraph(f"Approved by the {escape(meta['approved_by'])}. Owned by {escape(meta['owner'])}. "
                      "Distributed to all branches through the intranet. Printed copies are not controlled; "
                      "always check the intranet for the current version.", S["body"]),
            PageBreak()]


def contents():
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("t0", fontName="Helvetica-Bold", fontSize=10.5, leading=16, textColor=INK),
                       ParagraphStyle("t1", fontName="Helvetica", fontSize=10, leading=14, leftIndent=12, textColor=INK)]
    return [Paragraph("Contents", ParagraphStyle("ct", parent=S["h1"], spaceBefore=0)), toc, PageBreak()]


def body_flowables(meta, body):
    kind = "policy" if meta["id"].startswith("HR-") else "circular"
    flow, standard_added = [], False

    def add_standard():
        for n, (title, text) in STANDARD_SECTIONS.items():
            flow.append(Paragraph(f"{n}. {title}", S["h1"]))
            flow.append(Paragraph(inline(text.format(retention=meta["retention"], kind=kind, owner=meta["owner"])), S["body"]))
        flow.append(Paragraph("9. Related documents", S["h1"]))
        for r in meta["related"]:
            flow.append(Paragraph(inline(r), S["bullet"], bulletText="•"))

    for line in body.splitlines():
        line = line.rstrip()
        if not line:
            continue
        if line.startswith("## "):
            head = line[3:].strip()
            if head.startswith("Appendix") and not standard_added:
                add_standard(); standard_added = True
                flow.append(PageBreak())
            flow.append(Paragraph(inline(head), S["h1"]))
        elif line.startswith("### "):
            flow.append(Paragraph(inline(line[4:].strip()), S["h2"]))
        elif line.startswith("- [ ] "):
            flow.append(Paragraph(inline(line[6:]), S["bullet"], bulletText="[  ]"))
        elif line.startswith("- "):
            flow.append(Paragraph(inline(line[2:]), S["bullet"], bulletText="•"))
        else:
            flow.append(Paragraph(inline(line), S["body"]))
    if not standard_added:
        add_standard()
    return flow


def build_one(src_path):
    meta, body = parse_source(src_path)
    name = f"{meta['id']}-v{meta['version']}.pdf"
    path = os.path.join(OUT, name)
    doc = Doc(path, meta)
    story = cover(meta) + document_control(meta) + contents() + body_flowables(meta, body)
    doc.multiBuild(story, canvasmaker=numbered_canvas(meta))
    from pypdf import PdfReader
    pages = len(PdfReader(path).pages)
    return dict(id=meta["id"], title=meta["title"], version=meta["version"], status=meta["status"],
                effective_date=meta["effective_date"], owner=meta["owner"], file=f"pdf/{name}", pages=pages)


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = [build_one(os.path.join(SRC, f)) for f in sorted(os.listdir(SRC)) if f.endswith(".md")]
    with open(os.path.join(HERE, "register.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    for r in rows:
        print(f"{r['file']:28s} {r['status']:10s} {r['pages']:>3} pages")
    print(f"{len(rows)} PDFs, {sum(int(r['pages']) for r in rows)} pages in total")


if __name__ == "__main__":
    main()
