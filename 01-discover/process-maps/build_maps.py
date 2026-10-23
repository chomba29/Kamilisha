"""Build Kamilisha Stage 1 as-is process maps as BPMN 2.0 (+ SVG + PNG).

One definition per map drives all three outputs, so the .bpmn file opened in
bpmn.io and the picture on GitHub always show the same process.
Usage: python build_maps.py <output_dir>
"""
import sys, os
from xml.sax.saxutils import escape

# ---------------- layout constants ----------------
X0, Y0 = 40, 150          # pool top-left
POOL_BAND, LANE_BAND = 34, 34
COL_W, LANE_H = 190, 160
TASK_W, TASK_H = 156, 74
GW, EV = 54, 38
FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"
INK, MUTED, LINE, LANE_FILL = "#1f2a37", "#5b6675", "#475467", "#f6f8fa"
CTRL, CTRL_FILL, PAIN = "#b54708", "#fffaeb", "#c01048"

def esc(s): return escape(s, {'"': "&quot;"})

def tbg(x, y, text, size=12.5, anchor="middle", weight="400", fill="#1f2a37"):
    w = len(text) * size * (0.6 if weight != "400" else 0.56) + 8
    rx = x - w / 2 if anchor == "middle" else (x - 4 if anchor == "start" else x - w + 4)
    return (f'<rect x="{rx:.0f}" y="{y-size:.0f}" width="{w:.0f}" height="{size+6:.0f}" fill="#ffffff" fill-opacity="0.92"/>'
            f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{fill}">{esc(text)}</text>')

def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= width: cur = (cur + " " + w).strip()
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

class Map:
    def __init__(self, key, title, subtitle, lanes, ncols):
        self.key, self.title, self.subtitle, self.lanes, self.ncols = key, title, subtitle, lanes, ncols
        self.nodes, self.flows, self.notes = {}, [], []

    # geometry -------------------------------------------------
    def lane_top(self, i): return Y0 + i * LANE_H
    def cx(self, col): return X0 + POOL_BAND + LANE_BAND + 30 + col * COL_W + COL_W / 2
    def cy(self, lane): return self.lane_top(lane) + LANE_H / 2
    @property
    def pool_w(self): return POOL_BAND + LANE_BAND + 60 + self.ncols * COL_W
    @property
    def pool_h(self): return len(self.lanes) * LANE_H

    def node(self, nid, kind, lane, col, label, control=False, pains=(), dy=0):
        w, h = {"task": (TASK_W, TASK_H), "gateway": (GW, GW), "start": (EV, EV), "end": (EV, EV)}[kind]
        x, y = self.cx(col), self.cy(lane) + dy
        self.nodes[nid] = dict(id=nid, kind=kind, lane=lane, col=col, label=label, control=control,
                               pains=list(pains), x=x - w / 2, y=y - h / 2, w=w, h=h, mx=x, my=y)

    def port(self, n, side):
        return {"right": (n["x"] + n["w"], n["my"]), "left": (n["x"], n["my"]),
                "top": (n["mx"], n["y"]), "bottom": (n["mx"], n["y"] + n["h"])}[side]

    def flow(self, src, tgt, label="", exit=None, enter=None, via=None, lpos=None):
        a, b = self.nodes[src], self.nodes[tgt]
        if exit is None and enter is None and via is None:
            if a["lane"] == b["lane"]: exit, enter = "right", "left"
            else: exit, enter = "right", ("top" if b["lane"] > a["lane"] else "bottom")
        exit = exit or "right"; enter = enter or "left"
        p1, p2 = self.port(a, exit), self.port(b, enter)
        pts = [p1]
        if via:
            for vx, vy in via:
                pts.append((pts[-1][0] if vx is None else vx, pts[-1][1] if vy is None else vy))
            last = pts[-1]
            if enter in ("left", "right") and last[1] != p2[1]: pts.append((last[0], p2[1]))
            if enter in ("top", "bottom") and last[0] != p2[0]: pts.append((p2[0], last[1]))
        else:
            h1, h2 = exit in ("left", "right"), enter in ("left", "right")
            if h1 and h2 and p1[1] != p2[1]:
                mx = (p1[0] + p2[0]) / 2; pts += [(mx, p1[1]), (mx, p2[1])]
            elif h1 and not h2: pts.append((p2[0], p1[1]))
            elif not h1 and h2: pts.append((p1[0], p2[1]))
        pts.append(p2)
        self.flows.append(dict(id=f"Flow_{src}_{tgt}", src=src, tgt=tgt, label=label, pts=pts, lpos=lpos))

    def note(self, nid, text, x, y, w, attach=None, color=MUTED):
        lines = wrap(text, int(w / 6.9))
        self.notes.append(dict(id=nid, text=text, x=x, y=y, w=w, h=len(lines) * 17 + 14,
                               lines=lines, attach=attach, color=color))

    # ---------------- SVG ----------------
    def svg(self):
        W = X0 + self.pool_w + 40
        H = Y0 + self.pool_h + 190
        o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
             f'font-family="{FONT}" role="img" aria-label="{esc(self.title)}">',
             f'<title>{esc(self.title)}</title>',
             '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
             f'<path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/></marker>'
             '<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
             f'<path d="M0,0 L10,5 L0,10 z" fill="{PAIN}"/></marker></defs>',
             f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
             f'<text x="{X0}" y="44" font-size="14" font-weight="700" fill="#0e7490" letter-spacing="1">KAMILISHA · STAGE 1 · DISCOVER</text>',
             f'<text x="{X0}" y="84" font-size="30" font-weight="700" fill="{INK}">{esc(self.title)}</text>',
             f'<text x="{X0}" y="116" font-size="16" fill="{MUTED}">{esc(self.subtitle)}</text>']
        # pool and lanes
        px, py = X0, Y0
        o.append(f'<rect x="{px}" y="{py}" width="{self.pool_w}" height="{self.pool_h}" fill="#fff" stroke="{LINE}" stroke-width="1.5"/>')
        o.append(f'<line x1="{px+POOL_BAND}" y1="{py}" x2="{px+POOL_BAND}" y2="{py+self.pool_h}" stroke="{LINE}" stroke-width="1.5"/>')
        o.append(f'<text transform="translate({px+22},{py+self.pool_h/2}) rotate(-90)" text-anchor="middle" font-size="14" font-weight="700" fill="{INK}">Fictional bank · branch</text>')
        for i, name in enumerate(self.lanes):
            ly = self.lane_top(i)
            o.append(f'<rect x="{px+POOL_BAND}" y="{ly}" width="{self.pool_w-POOL_BAND}" height="{LANE_H}" fill="{LANE_FILL if i%2==0 else "#fff"}" stroke="{LINE}" stroke-width="1"/>')
            o.append(f'<line x1="{px+POOL_BAND+LANE_BAND}" y1="{ly}" x2="{px+POOL_BAND+LANE_BAND}" y2="{ly+LANE_H}" stroke="{LINE}" stroke-width="1"/>')
            o.append(f'<text transform="translate({px+POOL_BAND+22},{ly+LANE_H/2}) rotate(-90)" text-anchor="middle" font-size="13.5" font-weight="600" fill="{INK}">{esc(name)}</text>')
        # flows
        for f in self.flows:
            d = " ".join(("M" if i == 0 else "L") + f"{x:.0f},{y:.0f}" for i, (x, y) in enumerate(f["pts"]))
            if f.get("risk"):
                o.append(f'<path d="{d}" fill="none" stroke="{PAIN}" stroke-width="2.2" stroke-dasharray="7,5" marker-end="url(#arrR)"/>')
            else:
                o.append(f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.6" marker-end="url(#arr)"/>')
            if f["label"]:
                (x1, y1), (x2, y2) = f["pts"][0], f["pts"][1]
                if f["lpos"]: lx, ly, anc = f["lpos"]
                elif y1 == y2: lx, ly, anc = (x1 + 8, y1 - 8, "start")
                else: lx, ly, anc = (x1 + 8, y1 + (16 if y2 > y1 else -8), "start")
                for k, line in enumerate(f["label"].split("\n")):
                    o.append(tbg(lx, ly + k * 15, line, 12.5, anc, "600", PAIN if f.get("risk") else INK))
        # nodes
        for n in self.nodes.values():
            x, y, w, h, mx, my = n["x"], n["y"], n["w"], n["h"], n["mx"], n["my"]
            if n["kind"] == "task":
                stroke, fill, sw = (CTRL, CTRL_FILL, 2.6) if n["control"] else (LINE, "#fff", 1.6)
                o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
                lines = wrap(n["label"], 21)
                for k, line in enumerate(lines):
                    ty = my - (len(lines) - 1) * 8 + k * 16 + 5
                    o.append(f'<text x="{mx}" y="{ty:.0f}" text-anchor="middle" font-size="13" fill="{INK}">{esc(line)}</text>')
                if n["control"]:
                    o.append(f'<rect x="{x+6}" y="{y-10}" width="66" height="18" rx="9" fill="{CTRL}"/>'
                             f'<text x="{x+39}" y="{y+3}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#fff" letter-spacing="0.5">CONTROL</text>')
            elif n["kind"] == "gateway":
                pts = f"{mx},{y} {x+w},{my} {mx},{y+h} {x},{my}"
                stroke, fill = (CTRL, CTRL_FILL) if n["control"] else (LINE, "#fff")
                o.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{2.6 if n["control"] else 1.6}"/>')
                o.append(f'<path d="M{mx-9},{my-9} L{mx+9},{my+9} M{mx+9},{my-9} L{mx-9},{my+9}" stroke="{stroke}" stroke-width="3"/>')
                for k, line in enumerate(wrap(n["label"], 22)):
                    o.append(tbg(mx, y + h + 18 + k * 15, line))
                if n["control"]:
                    o.append(f'<rect x="{mx-33}" y="{y-22}" width="66" height="18" rx="9" fill="{CTRL}"/>'
                             f'<text x="{mx}" y="{y-9}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#fff" letter-spacing="0.5">CONTROL</text>')
            else:
                end = n["kind"] == "end"
                o.append(f'<circle cx="{mx}" cy="{my}" r="{w/2}" fill="#fff" stroke="{LINE}" stroke-width="{4 if end else 1.8}"/>')
                for k, line in enumerate(wrap(n["label"], 18)):
                    o.append(f'<text x="{mx}" y="{y+h+18+k*15}" text-anchor="middle" font-size="12.5" fill="{INK}">{esc(line)}</text>')
            # pain-point badges
            bx = (x + w - 4) if n["kind"] == "task" else (x + w + 2)
            by = (y - 10) if n["kind"] == "task" else (y - 2)
            for k, p in enumerate(reversed(n["pains"])):
                o.append(f'<rect x="{bx-34-k*38}" y="{by}" width="34" height="18" rx="9" fill="{PAIN}"/>'
                         f'<text x="{bx-17-k*38}" y="{by+13}" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">{p}</text>')
        # annotations
        for t in self.notes:
            if t["attach"]:
                n = self.nodes[t["attach"]]
                ax, ay = n["mx"], n["my"]
                o.append(f'<line x1="{ax}" y1="{ay}" x2="{t["x"]}" y2="{t["y"]+t["h"]/2}" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="3,4"/>')
            o.append(f'<rect x="{t["x"]}" y="{t["y"]}" width="{t["w"]}" height="{t["h"]}" fill="#fff" fill-opacity="0.94"/>')
            o.append(f'<path d="M{t["x"]+12},{t["y"]} L{t["x"]},{t["y"]} L{t["x"]},{t["y"]+t["h"]} L{t["x"]+12},{t["y"]+t["h"]}" fill="none" stroke="{t["color"]}" stroke-width="1.6"/>')
            for k, line in enumerate(t["lines"]):
                o.append(f'<text x="{t["x"]+10}" y="{t["y"]+20+k*17}" font-size="13" fill="{t["color"]}">{esc(line)}</text>')
        # legend
        ly = Y0 + self.pool_h + 50
        o.append(f'<line x1="{X0}" y1="{ly-22}" x2="{X0+self.pool_w}" y2="{ly-22}" stroke="#d0d5dd"/>')
        lx = X0
        items = [("start", "Start"), ("end", "End"), ("task", "Task"), ("gw", "Decision"),
                 ("ctrl", "Control step (fraud / compliance check)"), ("pain", "Pain point (see pain-point log)")]
        for kind, label in items:
            if kind == "start": o.append(f'<circle cx="{lx+12}" cy="{ly}" r="11" fill="#fff" stroke="{LINE}" stroke-width="1.8"/>'); off = 30
            elif kind == "end": o.append(f'<circle cx="{lx+12}" cy="{ly}" r="11" fill="#fff" stroke="{LINE}" stroke-width="4"/>'); off = 30
            elif kind == "task": o.append(f'<rect x="{lx}" y="{ly-12}" width="40" height="24" rx="6" fill="#fff" stroke="{LINE}" stroke-width="1.6"/>'); off = 50
            elif kind == "gw": o.append(f'<polygon points="{lx+13},{ly-13} {lx+26},{ly} {lx+13},{ly+13} {lx},{ly}" fill="#fff" stroke="{LINE}" stroke-width="1.6"/>'); off = 36
            elif kind == "ctrl": o.append(f'<rect x="{lx}" y="{ly-12}" width="40" height="24" rx="6" fill="{CTRL_FILL}" stroke="{CTRL}" stroke-width="2.6"/>'); off = 50
            else: o.append(f'<rect x="{lx}" y="{ly-9}" width="34" height="18" rx="9" fill="{PAIN}"/><text x="{lx+17}" y="{ly+4}" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">P#</text>'); off = 44
            o.append(f'<text x="{lx+off}" y="{ly+5}" font-size="13" fill="{INK}">{label}</text>')
            lx += off + len(label) * 7.2 + 36
        o.append(f'<text x="{X0}" y="{ly+48}" font-size="12.5" fill="{MUTED}">Fictional bank and procedures; no real bank documents or customer data. '
                 f'Source: practitioner interview (former branch staff, 9 years). Notation: BPMN 2.0.2 (omg.org/spec/BPMN/2.0.2).</text>')
        o.append("</svg>")
        return "\n".join(o)

    # ---------------- BPMN XML ----------------
    def bpmn(self):
        P = f"Process_{self.key}"
        tagmap = {"task": "task", "gateway": "exclusiveGateway", "start": "startEvent", "end": "endEvent"}
        incoming = {n: [] for n in self.nodes}; outgoing = {n: [] for n in self.nodes}
        for f in self.flows: outgoing[f["src"]].append(f["id"]); incoming[f["tgt"]].append(f["id"])
        x = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" '
             'xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" '
             'xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Defs_' + self.key + '" '
             'targetNamespace="https://github.com/kamilisha" exporter="kamilisha build_maps.py" exporterVersion="1.0">',
             f'  <bpmn:collaboration id="Collab_{self.key}">',
             f'    <bpmn:participant id="Pool_{self.key}" name="Fictional bank · branch — {esc(self.title)}" processRef="{P}" />']
        for t in self.notes:
            x.append(f'    <bpmn:textAnnotation id="{t["id"]}"><bpmn:text>{esc(t["text"])}</bpmn:text></bpmn:textAnnotation>')
            if t["attach"]:
                x.append(f'    <bpmn:association id="Assoc_{t["id"]}" sourceRef="{t["attach"]}" targetRef="{t["id"]}" />')
        x.append('  </bpmn:collaboration>')
        x.append(f'  <bpmn:process id="{P}" name="{esc(self.title)}" isExecutable="false">')
        x.append(f'    <bpmn:laneSet id="LaneSet_{self.key}">')
        for i, name in enumerate(self.lanes):
            x.append(f'      <bpmn:lane id="Lane_{self.key}_{i}" name="{esc(name)}">')
            for n in self.nodes.values():
                if n["lane"] == i: x.append(f'        <bpmn:flowNodeRef>{n["id"]}</bpmn:flowNodeRef>')
            x.append('      </bpmn:lane>')
        x.append('    </bpmn:laneSet>')
        for n in self.nodes.values():
            doc = []
            if n["control"]: doc.append("CONTROL STEP")
            if n["pains"]: doc.append("Pain points: " + ", ".join(n["pains"]))
            x.append(f'    <bpmn:{tagmap[n["kind"]]} id="{n["id"]}" name="{esc(n["label"])}">')
            if doc: x.append(f'      <bpmn:documentation>{esc("; ".join(doc))}</bpmn:documentation>')
            for fid in incoming[n["id"]]: x.append(f'      <bpmn:incoming>{fid}</bpmn:incoming>')
            for fid in outgoing[n["id"]]: x.append(f'      <bpmn:outgoing>{fid}</bpmn:outgoing>')
            x.append(f'    </bpmn:{tagmap[n["kind"]]}>')
        for f in self.flows:
            nm = f' name="{esc(f["label"].replace(chr(10), " "))}"' if f["label"] else ""
            x.append(f'    <bpmn:sequenceFlow id="{f["id"]}"{nm} sourceRef="{f["src"]}" targetRef="{f["tgt"]}" />')
        x.append('  </bpmn:process>')
        x.append(f'  <bpmndi:BPMNDiagram id="Diagram_{self.key}"><bpmndi:BPMNPlane id="Plane_{self.key}" bpmnElement="Collab_{self.key}">')
        x.append(f'    <bpmndi:BPMNShape id="Pool_{self.key}_di" bpmnElement="Pool_{self.key}" isHorizontal="true"><dc:Bounds x="{X0}" y="{Y0}" width="{self.pool_w}" height="{self.pool_h}" /></bpmndi:BPMNShape>')
        for i in range(len(self.lanes)):
            x.append(f'    <bpmndi:BPMNShape id="Lane_{self.key}_{i}_di" bpmnElement="Lane_{self.key}_{i}" isHorizontal="true"><dc:Bounds x="{X0+POOL_BAND}" y="{self.lane_top(i)}" width="{self.pool_w-POOL_BAND}" height="{LANE_H}" /></bpmndi:BPMNShape>')
        for n in self.nodes.values():
            x.append(f'    <bpmndi:BPMNShape id="{n["id"]}_di" bpmnElement="{n["id"]}"><dc:Bounds x="{n["x"]:.0f}" y="{n["y"]:.0f}" width="{n["w"]}" height="{n["h"]}" /></bpmndi:BPMNShape>')
        for f in self.flows:
            wps = "".join(f'<di:waypoint x="{px:.0f}" y="{py:.0f}" />' for px, py in f["pts"])
            x.append(f'    <bpmndi:BPMNEdge id="{f["id"]}_di" bpmnElement="{f["id"]}">{wps}</bpmndi:BPMNEdge>')
        for t in self.notes:
            x.append(f'    <bpmndi:BPMNShape id="{t["id"]}_di" bpmnElement="{t["id"]}"><dc:Bounds x="{t["x"]}" y="{t["y"]}" width="{t["w"]}" height="{t["h"]}" /></bpmndi:BPMNShape>')
            if t["attach"]:
                n = self.nodes[t["attach"]]
                x.append(f'    <bpmndi:BPMNEdge id="Assoc_{t["id"]}_di" bpmnElement="Assoc_{t["id"]}"><di:waypoint x="{n["mx"]:.0f}" y="{n["my"]:.0f}" /><di:waypoint x="{t["x"]}" y="{t["y"]+t["h"]/2:.0f}" /></bpmndi:BPMNEdge>')
        x.append('  </bpmndi:BPMNPlane></bpmndi:BPMNDiagram>')
        x.append('</bpmn:definitions>')
        return "\n".join(x)


# =====================================================================
# MAP 1 — how branch staff find a procedure today
# =====================================================================
def map1():
    m = Map("lookup", "Map 1 — Procedure lookup (as-is)",
            "How a branch officer finds the current procedure today, and where wrong answers enter.",
            ["Customer", "Branch officer", "Colleague / supervisor", "Back office (QA)"], 9)
    m.node("m1_start", "start", 0, 0, "Customer makes a request")
    m.node("m1_sure", "gateway", 1, 1, "Sure of the current procedure?")
    m.node("m1_search", "task", 1, 2, "Search intranet for the right circular", pains=["P6"])
    m.node("m1_found", "gateway", 1, 3, "Right section found quickly?", pains=["P6"])
    m.node("m1_read", "task", 1, 4, "Read the section in a 20–50 page circular", pains=["P7"])
    m.node("m1_ask", "task", 2, 4, "Answer from memory or habit (kwa mazoea)", pains=["P1", "P2"])
    m.node("m1_serve", "task", 1, 5, "Serve customer, including control steps")
    m.node("m1_qa", "gateway", 3, 6, "Error found at QA review?", pains=["P3"])
    m.node("m1_rework", "task", 3, 7, "Return for rework; customer recalled")
    m.node("m1_end", "end", 1, 8, "Request completed")

    m.flow("m1_start", "m1_sure")
    m.flow("m1_sure", "m1_search", "No")
    m.flow("m1_sure", "m1_serve", "Yes (may be out of date)", exit="top",
           via=[(None, m.lane_top(1) + 16), (m.nodes["m1_serve"]["mx"], None)], enter="top",
           lpos=(m.nodes["m1_sure"]["mx"] + 40, m.lane_top(1) + 12, "start"))
    m.flow("m1_search", "m1_found")
    m.flow("m1_found", "m1_read", "Yes")
    m.flow("m1_found", "m1_ask", "No: ask a colleague", exit="bottom", enter="left",
           lpos=(m.nodes["m1_found"]["mx"] + 8, m.lane_top(2) + 22, "start"))
    m.flow("m1_read", "m1_serve")
    m.flow("m1_ask", "m1_serve", exit="right", enter="bottom",
           via=[(m.nodes["m1_serve"]["mx"], None)])
    m.flow("m1_serve", "m1_qa", exit="right", enter="left", via=[(m.cx(5) + 95, None)])
    m.flow("m1_qa", "m1_rework", "Yes")
    m.flow("m1_qa", "m1_end", "No", exit="top", enter="left",
           lpos=(m.nodes["m1_qa"]["mx"] + 8, m.nodes["m1_qa"]["y"] - 26, "start"))
    m.flow("m1_rework", "m1_serve", exit="bottom", enter="bottom",
           via=[(None, m.lane_top(4) - 14), (m.nodes["m1_serve"]["mx"] - 30, None)],
           )
    # fix rework entry: enter serve bottom slightly left of centre to avoid the colleague arrow
    f = m.flows[-1]; sx = m.nodes["m1_serve"]["mx"] - 30; sb = m.nodes["m1_serve"]["y"] + TASK_H
    f["pts"] = [f["pts"][0], (f["pts"][0][0], m.lane_top(4) - 14), (sx, m.lane_top(4) - 14), (sx, sb)]
    # move the colleague arrow to enter serve bottom right of centre
    for fl in m.flows:
        if fl["src"] == "m1_ask":
            ex = m.nodes["m1_serve"]["mx"] + 30
            fl["pts"] = [fl["pts"][0], (ex, fl["pts"][0][1]), (ex, sb)]

    m.note("m1_n1", "Update emails get missed, so the colleague may answer from an old version of the circular (P1, P2).",
           m.cx(1) - 40, m.lane_top(2) + 50, 280)
    m.note("m1_n2", "Two officers can give the same customer different answers (P2).",
           m.cx(5) - 60, m.lane_top(0) + 40, 260)
    m.note("m1_n3", "Errors QA misses surface later as audit queries, or as a fraud loss (P3).",
           m.cx(7) - 20, m.lane_top(2) + 30, 290, attach="m1_end", color=PAIN)
    return m

# =====================================================================
# MAP 2 — card replacement
# =====================================================================
def map2():
    m = Map("card", "Map 2 — Card replacement (as-is)",
            "Four control steps protect the bank. The signed blocking form is the one skipped when staff follow the old circular.",
            ["Customer", "Branch officer", "Supervisor", "Card centre", "Back office (QA)"], 12)
    m.node("m2_start", "start", 0, 0, "Asks to replace a lost or damaged card")
    m.node("m2_id", "task", 1, 1, "Verify customer identity", control=True)
    m.node("m2_ver", "gateway", 1, 2, "Which circular does the officer follow?", pains=["P1", "P2"])
    m.node("m2_form", "task", 1, 3, "Obtain signed card-blocking form", control=True, pains=["P4"])
    m.node("m2_block", "task", 1, 4, "Block old card on the card system", control=True)
    m.node("m2_req", "task", 1, 5, "Capture replacement request; charge fee")
    m.node("m2_auth", "gateway", 2, 6, "Authorise?")
    m.node("m2_make", "task", 3, 7, "Produce new card")
    m.node("m2_qa", "gateway", 4, 8, "Old card confirmed blocked and form on file?", pains=["P3"])
    m.node("m2_exc", "task", 4, 9, "Block card; raise exception to branch")
    m.node("m2_hand", "task", 1, 10, "Hand over new card after ID check", control=True)
    m.node("m2_end", "end", 1, 11, "Replacement complete")

    m.flow("m2_start", "m2_id")
    m.flow("m2_id", "m2_ver")
    m.flow("m2_ver", "m2_form", "Current (v2)")
    habit_y = m.cy(1) + 62
    m.flow("m2_ver", "m2_block", exit="bottom", enter="bottom",
           via=[(None, habit_y), (m.nodes["m2_block"]["mx"], None)])
    m.flows[-1]["label"] = "Habit (old v1): form skipped"
    m.flows[-1]["risk"] = True
    m.flows[-1]["lpos"] = (m.nodes["m2_form"]["x"] - 8, habit_y - 7, "start")
    m.flow("m2_form", "m2_block")
    m.flow("m2_block", "m2_req")
    m.flow("m2_req", "m2_auth", exit="right", enter="top")
    m.flow("m2_auth", "m2_make", "Yes", exit="bottom", enter="left",
           lpos=(m.nodes["m2_auth"]["mx"] + 8, m.cy(2) + 50, "start"))
    m.flow("m2_auth", "m2_req", "No: correct", exit="left", enter="bottom",
           via=[(m.nodes["m2_req"]["mx"], None)],
           lpos=(m.nodes["m2_req"]["mx"] + 10, m.cy(2) - 8, "start"))
    m.flow("m2_make", "m2_qa", exit="bottom", enter="left")
    m.flow("m2_qa", "m2_exc", "No")
    m.flow("m2_qa", "m2_hand", "Yes", exit="top", enter="left",
           lpos=(m.nodes["m2_qa"]["mx"] + 8, m.nodes["m2_qa"]["y"] - 26, "start"))
    m.flow("m2_exc", "m2_hand", exit="right", enter="bottom",
           via=[(m.nodes["m2_hand"]["mx"], None)])
    m.flow("m2_hand", "m2_end")

    m.note("m2_n1", "Old circular (v1): block on the system, no form needed. Current circular (v2): signed blocking form first, then block. Habit still follows v1 (P1, P2).",
           m.cx(1) - 70, m.lane_top(2) + 20, 360, attach="m2_ver")
    m.note("m2_n2", "Skipping the form (P4) is caught by QA, later by an audit query, or not at all: the lost card keeps transacting and the bank takes a fraud loss.",
           m.cx(3) - 30, m.lane_top(2) + 22, 330, color=PAIN)
    return m

# =====================================================================
# MAP 3 — business account opening
# =====================================================================
def map3():
    m = Map("account", "Map 3 — Business account opening (as-is)",
            "The documents check is where branches disagree, because the required list changed and habit did not.",
            ["Customer", "Branch officer", "Compliance", "Back office (QA)"], 11)
    m.node("m3_start", "start", 0, 0, "Requests a business account")
    m.node("m3_list", "task", 1, 1, "Give documents list for the entity type", pains=["P2", "P5"])
    m.node("m3_return", "task", 0, 2, "Returns with documents")
    m.node("m3_docs", "gateway", 1, 3, "Documents complete per current circular?", control=True, pains=["P5"])
    m.node("m3_verify", "task", 1, 4, "Verify owners and signatories", control=True)
    m.node("m3_screen", "task", 1, 5, "Screen and risk-rate the customer", control=True)
    m.node("m3_risk", "gateway", 1, 6, "High risk?")
    m.node("m3_edd", "task", 2, 7, "Enhanced due diligence and approval", control=True)
    m.node("m3_open", "task", 1, 8, "Open account and mandate in core banking")
    m.node("m3_qa", "gateway", 3, 9, "File complete and correct?", pains=["P3"])
    m.node("m3_back", "task", 3, 10, "Return file to branch; customer recalled")
    m.node("m3_end", "end", 1, 10, "Account activated")

    m.flow("m3_start", "m3_list")
    m.flow("m3_list", "m3_return", exit="right", enter="bottom",
           via=[(m.nodes["m3_return"]["mx"], None)])
    m.flow("m3_return", "m3_docs", exit="right", enter="top",
           via=[(m.nodes["m3_docs"]["mx"], None)])
    m.flow("m3_docs", "m3_verify", "Yes")
    m.flow("m3_docs", "m3_list", "No: another trip", exit="bottom", enter="bottom",
           via=[(None, m.cy(1) + 66), (m.nodes["m3_list"]["mx"], None)])
    m.flows[-1]["lpos"] = (m.nodes["m3_list"]["mx"] + 90, m.cy(1) + 57, "start")
    m.flow("m3_verify", "m3_screen")
    m.flow("m3_screen", "m3_risk")
    m.flow("m3_risk", "m3_open", "No")
    m.flow("m3_risk", "m3_edd", "Yes", exit="bottom", enter="left",
           lpos=(m.nodes["m3_risk"]["mx"] + 8, m.cy(1) + 62, "start"))
    m.flow("m3_edd", "m3_open", exit="right", enter="bottom",
           via=[(m.nodes["m3_open"]["mx"], None)])
    m.flow("m3_open", "m3_qa", exit="right", enter="left", via=[(m.cx(8) + 95, None)])
    m.flow("m3_qa", "m3_end", "Yes", exit="top", enter="left",
           lpos=(m.nodes["m3_qa"]["mx"] + 8, m.nodes["m3_qa"]["y"] - 26, "start"))
    m.flow("m3_qa", "m3_back", "No")
    m.flow("m3_back", "m3_open", "", exit="bottom", enter="bottom")
    f = m.flows[-1]; ox = m.nodes["m3_open"]["mx"] + 40; ob = m.nodes["m3_open"]["y"] + TASK_H
    f["pts"] = [f["pts"][0], (f["pts"][0][0], m.lane_top(4) - 12), (ox, m.lane_top(4) - 12), (ox, ob)]
    f["lpos"] = (ox + 10, m.lane_top(4) - 20, "start")
    m.nodes["m3_back"]["label"] = "Return file to branch; customer recalled"
    m.note("m3_n1", "Old circular (v1): business licence for every business account. Current (v2): sole proprietors may give a tax registration certificate instead. Some branches still ask for the licence (P2, P5).",
           m.cx(1) - 70, m.lane_top(2) + 26, 400)
    m.note("m3_n2", "Each wrong list costs the customer a wasted trip and the branch a QA return (P3, P5).",
           m.cx(4) - 40, m.lane_top(2) + 44, 330, color=PAIN)
    return m


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    names = {"lookup": "map-1-as-is-procedure-lookup", "card": "map-2-as-is-card-replacement",
             "account": "map-3-as-is-account-opening"}
    for m in (map1(), map2(), map3()):
        base = os.path.join(out, names[m.key])
        open(base + ".bpmn", "w", encoding="utf-8").write(m.bpmn())
        open(base + ".svg", "w", encoding="utf-8").write(m.svg())
        try:
            import cairosvg
            cairosvg.svg2png(url=base + ".svg", write_to=base + ".png", output_width=2400)
        except ImportError:
            print("cairosvg not installed: PNG skipped")
        print("built", base)
