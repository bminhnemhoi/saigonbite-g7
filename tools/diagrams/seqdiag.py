"""Small UML sequence-diagram renderer (SVG) with exact text measurement.

Generic renderers overlapped labels, activation bars and numbers, and produced tiny text.
This renderer lays out lifelines from measured label widths, wraps long messages and draws
UML notation: an `sd` frame, actor/boundary/control/interface/database/external heads,
activation bars, numbered synchronous and reply messages, self calls, alt/else/opt/loop
fragments, interaction references and notes. Sizes are chosen so that the diagram stays
readable (about 8 pt or more) when it is placed on an A4 page.
"""
from html import escape
from PIL import ImageFont

FONT = "C:/Windows/Fonts/segoeui.ttf"
FONT_B = "C:/Windows/Fonts/segoeuib.ttf"
FS = 16      # message text
LH = 21      # message line height
HFS = 16     # participant name
SFS = 12.5   # stereotype
GFS = 15     # fragment guard
NFS = 15     # note text
NAVY, INK = "#12263A", "#1F2933"
_fonts = {}


def font(bold=False, size=FS):
    key = (bold, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT_B if bold else FONT, size)
    return _fonts[key]


def tw(text, bold=False, size=FS):
    return font(bold, size).getlength(text)


def wrap(text, width, bold=False, size=FS):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split(" "):
            trial = (cur + " " + w).strip()
            if tw(trial, bold, size) <= width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


KIND_STYLE = {
    "actor": ("#FFFFFF", NAVY, ""),
    "boundary": ("#EAF3FB", "#2E7DAF", "«boundary»"),
    "control": ("#FFFFFF", NAVY, "«control»"),
    "strategy": ("#FFF1EC", "#E4572E", "«interface»"),
    "database": ("#F1F4F7", "#5B6B7A", ""),
    "external": ("#FFF8E6", "#C98A1E", "«external system»"),
}


class Seq:
    def __init__(self, name):
        self.name = name
        self.parts, self.idx, self.ev = [], {}, []

    # ---- model ---------------------------------------------------------------
    def p(self, pid, label, kind="control"):
        self.idx[pid] = len(self.parts)
        self.parts.append({"id": pid, "label": label, "kind": kind})
        return self

    def msg(self, a, b, text, reply=False):
        self.ev.append(("msg", a, b, text, reply)); return self

    def reply(self, a, b, text):
        return self.msg(a, b, text, True)

    def self_(self, a, text):
        self.ev.append(("self", a, text)); return self

    def act(self, a):
        self.ev.append(("act", a)); return self

    def deact(self, a):
        self.ev.append(("deact", a)); return self

    def frag(self, kind, guard):
        self.ev.append(("frag", kind, guard)); return self

    def else_(self, guard):
        self.ev.append(("else", guard)); return self

    def end(self):
        self.ev.append(("end",)); return self

    def note(self, a, b, text):
        self.ev.append(("note", a, b, text)); return self

    def ref(self, a, b, text):
        self.ev.append(("ref", a, b, text)); return self

    def section(self, title):
        self.ev.append(("section", title)); return self

    # ---- layout --------------------------------------------------------------
    def _head(self, part):
        lines = part["label"].split("\n")
        w = max(tw(l, True, HFS) for l in lines)
        st = KIND_STYLE[part["kind"]][2]
        if st:
            w = max(w, tw(st, False, SFS))
        if part["kind"] == "actor":
            return max(w, 70) + 10, 48 + 20 * len(lines)
        h = 20 * len(lines) + (17 if st else 0) + 22
        return max(w + 30, 130), max(h, 54)

    def render(self, path, max_label=212, min_gap=136):
        n = len(self.parts)
        heads = [self._head(p) for p in self.parts]
        head_h = max(h for _, h in heads)
        gaps = [max((heads[i][0] + heads[i + 1][0]) / 2 + 24, min_gap) for i in range(n - 1)] + [0]
        for e in self.ev:
            if e[0] == "msg":
                i, j = sorted((self.idx[e[1]], self.idx[e[2]]))
                need = min(tw("00 " + e[3]), max_label) + 36
                span = sum(gaps[i:j])
                if span < need:
                    for k in range(i, j):
                        gaps[k] += (need - span) / (j - i)
            elif e[0] == "self":
                i = self.idx[e[1]]
                need = min(tw("00 " + e[2]), max_label) + 64
                if i < n - 1 and gaps[i] < need:
                    gaps[i] = need
        xs = [34 + heads[0][0] / 2]
        for g in gaps[:-1]:
            xs.append(xs[-1] + g)
        width = xs[-1] + heads[-1][0] / 2 + 34
        for e in self.ev:
            if e[0] == "self" and self.idx[e[1]] == n - 1:
                width = max(width, xs[-1] + min(tw("00 " + e[2]), max_label) + 90)

        top = 44
        y = top + head_h + 24
        out, frames, notes, acts = [], [], [], []
        stack = {p["id"]: [] for p in self.parts}
        fstack, num = [], 0

        def ax(pid, side):
            d = len(stack[pid])
            x = xs[self.idx[pid]]
            return x if d == 0 else x + (d - 1) * 5 + (6 if side > 0 else -6)

        def involve(pids, extra_right=0):
            for f in fstack:
                for pid in pids:
                    x = xs[self.idx[pid]]
                    f["minx"] = min(f["minx"], x)
                    f["maxx"] = max(f["maxx"], x + extra_right)

        nw = lambda k: tw(f"{k} ", True)
        for e in self.ev:
            k = e[0]
            if k == "msg":
                _, a, b, text, rep = e
                num += 1
                ia, ib = self.idx[a], self.idx[b]
                span = abs(xs[ib] - xs[ia]) - 26
                lines = wrap(text, min(max_label, max(span - nw(num), 70)))
                y += LH * len(lines) + 2
                x1 = ax(a, 1 if ib > ia else -1)
                x2 = ax(b, -1 if ib > ia else 1)
                lx = min(x1, x2) + (16 if x2 < x1 else 10)
                for li, line in enumerate(lines):
                    ty = y - 7 - LH * (len(lines) - 1 - li)
                    if li == 0:
                        out.append(f'<text x="{lx:.1f}" y="{ty:.1f}" class="m"><tspan class="n">{num}</tspan> {escape(line)}</text>')
                    else:
                        out.append(f'<text x="{lx + nw(num):.1f}" y="{ty:.1f}" class="m">{escape(line)}</text>')
                dash = ' stroke-dasharray="7 5"' if rep else ""
                out.append(f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" class="ln"{dash} marker-end="url(#{"open" if rep else "solid"})"/>')
                involve([a, b])
                y += 13
            elif k == "self":
                _, a, text = e
                num += 1
                lines = wrap(text, max_label)
                x = ax(a, 1)
                y += 6
                lx = x + 38
                for li, line in enumerate(lines):
                    pre = f'<tspan class="n">{num}</tspan> ' if li == 0 else ""
                    off = 0 if li == 0 else nw(num)
                    out.append(f'<text x="{lx + off:.1f}" y="{y + 14 + LH * li:.1f}" class="m">{pre}{escape(line)}</text>')
                h = max(26, LH * len(lines) + 4)
                out.append(f'<path d="M{x:.1f},{y:.1f} H{x + 30:.1f} V{y + h:.1f} H{x + 2:.1f}" class="ln" fill="none" marker-end="url(#solid)"/>')
                involve([a], extra_right=38 + max(tw(l) for l in lines) + 10)
                y += h + 14
            elif k == "act":
                stack[e[1]].append(y - 18)
            elif k == "deact":
                y0 = stack[e[1]].pop()
                d = len(stack[e[1]])
                acts.append((xs[self.idx[e[1]]] - 6 + d * 5, y0, y - y0 + 4))
            elif k == "frag":
                y += 8
                fstack.append({"kind": e[1], "guard": e[2], "y0": y, "elses": [], "minx": 1e9, "maxx": -1e9})
                y += 30
            elif k == "else":
                y += 8
                fstack[-1]["elses"].append((y, e[1]))
                y += 27
            elif k == "end":
                y += 6
                f = fstack.pop()
                f["y1"], f["depth"] = y, len(fstack)
                frames.append(f)
                for g in fstack:
                    g["minx"] = min(g["minx"], f["minx"] - 14)
                    g["maxx"] = max(g["maxx"], f["maxx"] + 14)
                y += 10
            elif k in ("note", "ref"):
                _, a, b, text = e
                ia, ib = sorted((self.idx[a], self.idx[b]))
                x0, x1 = xs[ia] - 50, (xs[ib] + 50 if ib != ia else xs[ia] + 260)
                lines = wrap(text, x1 - x0 - (110 if k == "ref" else 24), size=NFS)
                h = 21 * len(lines) + 16
                y += 8
                notes.append((k, x0, y, x1 - x0, h, lines))
                involve([self.parts[ia]["id"], self.parts[ib]["id"]])
                y += h + 14
            elif k == "section":
                y += 10
                notes.append(("section", y, e[1]))
                y += 40
        y += 20
        height = y + 26

        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" font-family="Segoe UI, Arial, sans-serif">',
               """<defs>
<marker id="solid" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="10" markerHeight="10" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#2B3A4A"/></marker>
<marker id="open" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="10" markerHeight="10" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10" fill="none" stroke="#2B3A4A" stroke-width="1.5"/></marker>
</defs>
<style>
.m{font-size:16px;fill:#1F2933}
.n{font-weight:700;fill:#E4572E}
.ln{stroke:#2B3A4A;stroke-width:1.5}
.life{stroke:#9AA5B1;stroke-width:1.3;stroke-dasharray:6 6}
.hd{font-size:16px;font-weight:700;fill:#12263A}
.st{font-size:12.5px;fill:#5B6B7A;font-style:italic}
.ft{font-size:15px;font-weight:700;fill:#FFFFFF}
.gd{font-size:15px;fill:#12263A;font-weight:600}
.nt{font-size:15px;fill:#1F2933}
.sec{font-size:16px;font-weight:700;fill:#12263A}
</style>""",
               f'<rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" fill="#FFFFFF"/>']
        sd = f"sd {self.name}"
        sdw = tw(sd, True, 15) + 28
        svg.append(f'<rect x="8" y="8" width="{width - 16:.0f}" height="{height - 16:.0f}" fill="none" stroke="#12263A" stroke-width="1.4"/>')
        svg.append(f'<path d="M8,8 H{8 + sdw:.0f} V24 L{sdw - 2:.0f},36 H8 z" fill="#12263A"/>')
        svg.append(f'<text x="18" y="28" class="ft">{escape(sd)}</text>')
        for nd in notes:
            if nd[0] == "section":
                _, sy, title = nd
                svg.append(f'<rect x="20" y="{sy:.1f}" width="{width - 40:.0f}" height="30" fill="#F1F4F7" stroke="#C8D1DA"/>')
                svg.append(f'<text x="34" y="{sy + 21:.1f}" class="sec">{escape(title)}</text>')
        for i in range(n):
            svg.append(f'<line x1="{xs[i]:.1f}" y1="{top + head_h:.1f}" x2="{xs[i]:.1f}" y2="{height - 24:.1f}" class="life"/>')
        labels = []
        for f in sorted(frames, key=lambda f: f["depth"]):
            dep = f["depth"]
            fx0 = max(18 + 12 * dep, f["minx"] - 60 + 12 * dep)
            fx1 = min(width - 18 - 12 * dep, f["maxx"] + 60 - 12 * dep)
            svg.append(f'<rect x="{fx0:.1f}" y="{f["y0"]:.1f}" width="{fx1 - fx0:.1f}" height="{f["y1"] - f["y0"]:.1f}" fill="none" stroke="#5B6B7A" stroke-width="1.3"/>')
            tag = f["kind"]
            tgw = tw(tag, True, 14) + 20
            labels.append(f'<path d="M{fx0:.1f},{f["y0"]:.1f} H{fx0 + tgw:.1f} V{f["y0"] + 14:.1f} L{fx0 + tgw - 9:.1f},{f["y0"] + 23:.1f} H{fx0:.1f} z" fill="#E8EEF4" stroke="#5B6B7A"/>')
            labels.append(f'<text x="{fx0 + 8:.1f}" y="{f["y0"] + 17:.1f}" style="font-size:14px;font-weight:700;fill:#12263A">{escape(tag)}</text>')
            g = "[" + f["guard"] + "]"
            gx = fx0 + tgw + 9
            labels.append(f'<rect x="{gx - 3:.1f}" y="{f["y0"] + 4:.1f}" width="{tw(g, True, GFS) + 6:.1f}" height="20" fill="#FFFFFF"/>')
            labels.append(f'<text x="{gx:.1f}" y="{f["y0"] + 19:.1f}" class="gd">{escape(g)}</text>')
            for ey, eg in f["elses"]:
                svg.append(f'<line x1="{fx0:.1f}" y1="{ey:.1f}" x2="{fx1:.1f}" y2="{ey:.1f}" stroke="#5B6B7A" stroke-dasharray="7 5"/>')
                g2 = "[" + eg + "]"
                labels.append(f'<rect x="{fx0 + 8:.1f}" y="{ey + 5:.1f}" width="{tw(g2, True, GFS) + 6:.1f}" height="20" fill="#FFFFFF"/>')
                labels.append(f'<text x="{fx0 + 11:.1f}" y="{ey + 20:.1f}" class="gd">{escape(g2)}</text>')
        for x0, y0, h in acts:
            svg.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="12" height="{h:.1f}" fill="#E8EEF4" stroke="#12263A" stroke-width="1.1"/>')
        svg.extend(labels)
        for nd in notes:
            if nd[0] == "section":
                continue
            k, x0, ny, w, h, lines = nd
            if k == "note":
                svg.append(f'<path d="M{x0:.1f},{ny:.1f} H{x0 + w - 12:.1f} L{x0 + w:.1f},{ny + 12:.1f} V{ny + h:.1f} H{x0:.1f} z" fill="#FFF8E6" stroke="#E9A23B" stroke-width="1.2"/>')
                tx = x0 + 12
            else:  # interaction use: ref frame
                svg.append(f'<rect x="{x0:.1f}" y="{ny:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#FFFFFF" stroke="#12263A" stroke-width="1.4"/>')
                svg.append(f'<path d="M{x0:.1f},{ny:.1f} H{x0 + 52:.1f} V{ny + 14:.1f} L{x0 + 43:.1f},{ny + 23:.1f} H{x0:.1f} z" fill="#12263A"/>')
                svg.append(f'<text x="{x0 + 10:.1f}" y="{ny + 17:.1f}" style="font-size:14px;font-weight:700;fill:#FFFFFF">ref</text>')
                tx = x0 + (w - max(tw(l, True, NFS) for l in lines)) / 2
            for li, line in enumerate(lines):
                cls = "nt" if k == "note" else "gd"
                svg.append(f'<text x="{tx:.1f}" y="{ny + 21 + 21 * li:.1f}" class="{cls}">{escape(line)}</text>')
        svg.extend(out)
        for i, part in enumerate(self.parts):
            w, h = heads[i]
            x = xs[i]
            fill, stroke, st = KIND_STYLE[part["kind"]]
            lines = part["label"].split("\n")
            y0 = top + head_h - h
            if part["kind"] == "actor":
                cy = y0 + 4
                svg.append(f'<g stroke="{NAVY}" stroke-width="1.9" fill="none"><circle cx="{x}" cy="{cy + 8}" r="8" fill="#FFFFFF"/><line x1="{x}" y1="{cy + 16}" x2="{x}" y2="{cy + 30}"/><line x1="{x - 12}" y1="{cy + 21}" x2="{x + 12}" y2="{cy + 21}"/><line x1="{x}" y1="{cy + 30}" x2="{x - 10}" y2="{cy + 41}"/><line x1="{x}" y1="{cy + 30}" x2="{x + 10}" y2="{cy + 41}"/></g>')
                for li, line in enumerate(lines):
                    svg.append(f'<text x="{x}" y="{cy + 62 + 20 * li}" text-anchor="middle" class="hd">{escape(line)}</text>')
                continue
            if part["kind"] == "database":
                svg.append(f'<path d="M{x - w / 2:.1f},{y0 + 9:.1f} v{h - 18:.1f} a{w / 2:.1f},9 0 0 0 {w:.1f},0 v-{h - 18:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
                svg.append(f'<ellipse cx="{x:.1f}" cy="{y0 + 9:.1f}" rx="{w / 2:.1f}" ry="9" fill="#FFFFFF" stroke="{stroke}" stroke-width="1.5"/>')
                ty = y0 + 9 + (h - 9) / 2 - 10 * (len(lines) - 1) + 6
            else:
                dash = ' stroke-dasharray="6 3"' if part["kind"] == "external" else ""
                svg.append(f'<rect x="{x - w / 2:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="1.6"{dash}/>')
                ty = y0 + 23
                if st:
                    svg.append(f'<text x="{x:.1f}" y="{ty - 3:.1f}" text-anchor="middle" class="st">{escape(st)}</text>')
                    ty += 18
            for li, line in enumerate(lines):
                svg.append(f'<text x="{x:.1f}" y="{ty + 20 * li:.1f}" text-anchor="middle" class="hd">{escape(line)}</text>')
        svg.append("</svg>")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(svg))
        return width, height
