"""Overall use case diagram (hand-placed SVG, UML notation).
Compact layout: 17 px text on a 1460 px canvas, i.e. about 8 pt when printed on a landscape page.
Usage: python ucdiag.py <out_dir>"""
import math
import os
import sys
from html import escape
from PIL import ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
F = {k: ImageFont.truetype(f"C:/Windows/Fonts/{v}", s) for k, (v, s) in {
    "t": ("segoeui.ttf", 17), "tb": ("segoeuib.ttf", 17.5), "s": ("segoeui.ttf", 13.5)}.items()}
NAVY, INK, SLATE = "#12263A", "#1F2933", "#5B6B7A"
W, H = 1460, 1040
svg, UC, LABELS = [], {}, []


def text(x, y, s, cls, anchor="middle"):
    svg.append(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}">{escape(s)}</text>')


def actor(x, y, label, abstract=False):
    svg.append(f'<g stroke="{NAVY}" stroke-width="2" fill="none">'
               f'<circle cx="{x}" cy="{y - 24}" r="10" fill="#FFFFFF"/>'
               f'<line x1="{x}" y1="{y - 14}" x2="{x}" y2="{y + 9}"/>'
               f'<line x1="{x - 16}" y1="{y - 6}" x2="{x + 16}" y2="{y - 6}"/>'
               f'<line x1="{x}" y1="{y + 9}" x2="{x - 12}" y2="{y + 28}"/>'
               f'<line x1="{x}" y1="{y + 9}" x2="{x + 12}" y2="{y + 28}"/></g>')
    LABELS.append((x, y + 50, label, "ai" if abstract else "a"))
    return (x, y)


def usecase(key, x, y, title, sub="", kind="n", minw=180):
    big = kind in ("uc1", "uc2")
    tw = max(F["tb" if big else "t"].getlength(title), F["s"].getlength(sub) if sub else 0)
    rx = max(minw / 2, tw / 2 + 24) + (8 if big else 0)
    ry = (33 if sub else 26) + (4 if big else 0)
    fill, stroke, sw = {"n": ("#FFFFFF", NAVY, 1.5), "inc": ("#F7F9FB", SLATE, 1.3), "t4": ("#FFF8E6", "#C98A1E", 1.8),
                        "uc1": ("#FFF1EC", "#E4572E", 2.6), "uc2": ("#EAF3FB", "#2E7DAF", 2.6)}[kind]
    svg.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx:.1f}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    if sub:
        text(x, y - 3, title, "ub" if big else "u")
        text(x, y + 17, sub, "us")
    else:
        text(x, y + 6, title, "ub" if big else "u")
    UC[key] = (x, y, rx, ry)


def border(key, tx, ty):
    x, y, rx, ry = UC[key]
    a = math.atan2(ty - y, tx - x)
    return x + rx * math.cos(a), y + ry * math.sin(a)


def assoc(a, key, bold=False):
    ax, ay = a
    px, py = border(key, ax, ay)
    sx = ax + (24 if px > ax else -24)
    svg.append(f'<line x1="{sx}" y1="{ay - 4}" x2="{px:.1f}" y2="{py:.1f}" stroke="{INK}" stroke-width="{2.2 if bold else 1.4}"/>')


def dashed(a, b, label, curve=None):
    if curve is None:
        p1, p2 = border(a, *UC[b][:2]), border(b, *UC[a][:2])
        svg.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" class="dash" marker-end="url(#open)"/>')
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    else:
        p1 = (UC[a][0] - UC[a][2], UC[a][1])
        p2 = (UC[b][0] - UC[b][2], UC[b][1])
        cx = min(p1[0], p2[0]) - curve
        svg.append(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} C{cx:.1f},{p1[1]:.1f} {cx:.1f},{p2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="none" class="dash" marker-end="url(#open)"/>')
        mx, my = cx + curve * 0.25, (p1[1] + p2[1]) / 2
    svg.append(f'<rect x="{mx - 37}" y="{my - 12}" width="74" height="18" fill="#FBFCFD"/>')
    text(mx, my + 3, label, "st")


svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#FFFFFF"/>')
svg.append(f'<rect x="290" y="16" width="945" height="950" rx="14" fill="#FBFCFD" stroke="{NAVY}" stroke-width="1.8"/>')
text(310, 46, "SaigonBite Platform", "sys", "start")

A, M, B = 455, 772, 1068
usecase("REG", A, 140, "Register Account", "phone + OTP · passport + email")
usecase("BROWSE", A + 75, 248, "Browse Menus", "hubs · brands · dishes")
usecase("UC1", A, 400, "UC1 · Place and Manage Orders", "place · track · edit · cancel", "uc1")
usecase("LOAD", M, 262, "View Hub Load", "BR7, BR8", "inc", minw=170)
usecase("CALC", M, 380, "Calculate Price", "BR1–BR12", "inc", minw=170)
usecase("PAY", M, 500, "Select Payment Method", "BR13, BR14", "inc")
usecase("PAYPAL", M, 650, "Pay with PayPal Sandbox", "Tier 4 · live API", "t4")
usecase("PROC", B, 82, "Process Orders", "confirm · reject · prepare · ready")
usecase("DELIV", B, 172, "Deliver Orders", "pick up · confirm cash · fail")
usecase("UC2", B, 262, "UC2 · Manage Hubs & Capacity", "create · view · edit · deactivate", "uc2")
for k, t, s, kind, yy in [("MENU", "Manage Menu & Brands", "", "n", 352), ("VOU", "Manage Vouchers", "", "n", 422),
                          ("ACC", "Manage User Accounts", "", "n", 492), ("ASG", "Assign Shipper (A-01)", "", "n", 562),
                          ("RAIN", "Set Heavy-Rain Flag", "", "n", 632), ("R1", "View Revenue Report R1", "", "n", 702),
                          ("R2", "View Hub Utilization R2", "", "n", 772), ("DASH", "Use Admin Dashboard", "Tier 4 · KPIs and charts", "t4", 862)]:
    usecase(k, B, yy, t, s, kind, minw=250)

lc = actor(78, 300, "Local Customer")
ft = actor(78, 520, "Foreign Tourist")
cu = actor(212, 410, "Customer", abstract=True)
ks = actor(1355, 72, "Kitchen Staff")
sh = actor(1355, 185, "Shipper")
ad = actor(1362, 560, "System Admin")
svg.append('<rect x="62" y="800" width="196" height="58" rx="8" fill="#FFF8E6" stroke="#C98A1E" stroke-width="1.7" stroke-dasharray="6 3"/>')
text(160, 822, "«system»", "st")
text(160, 846, "PayPal Sandbox API", "a")

for (x, y) in (lc, ft):
    svg.append(f'<line x1="{x + 24}" y1="{y - 4}" x2="{cu[0] - 28}" y2="{cu[1] - 4}" stroke="{INK}" stroke-width="1.5" marker-end="url(#gen)"/>')
for k in ("REG", "BROWSE"):
    assoc(cu, k)
assoc(cu, "UC1", bold=True)
assoc(ks, "PROC")
assoc(sh, "DELIV")
for k in ("UC2", "MENU", "VOU", "ACC", "ASG", "RAIN", "R1", "R2", "DASH"):
    assoc(ad, k, bold=(k == "UC2"))
px, py = border("PAYPAL", 258, 829)
svg.append(f'<line x1="258" y1="829" x2="{px:.1f}" y2="{py:.1f}" stroke="{INK}" stroke-width="1.4"/>')

dashed("UC1", "CALC", "«include»")
dashed("UC1", "PAY", "«include»")
dashed("PAYPAL", "PAY", "«extend»")
dashed("UC2", "LOAD", "«include»")
dashed("DASH", "R2", "«include»", curve=36)
dashed("DASH", "R1", "«include»", curve=62)

nx, ny = 330, 560
svg.append(f'<path d="M{nx},{ny} H{nx + 250} L{nx + 264},{ny + 14} V{ny + 58} H{nx} z" fill="#FFF8E6" stroke="#E9A23B" stroke-width="1.2"/>')
text(nx + 12, ny + 24, "extension point: online payment", "nt", "start")
text(nx + 12, ny + 46, "condition: Tourist selects PayPal", "nt", "start")
svg.append(f'<line x1="{nx + 200}" y1="{ny + 58}" x2="{UC["PAYPAL"][0] - UC["PAYPAL"][2] + 20:.1f}" y2="{UC["PAYPAL"][1] - 18}" stroke="#E9A23B" stroke-dasharray="4 3" stroke-width="1.3"/>')

for lx, ly, label, cls in LABELS:
    w = F["tb"].getlength(label) + 10
    svg.append(f'<rect x="{lx - w / 2:.1f}" y="{ly - 17}" width="{w:.1f}" height="23" rx="4" fill="#FFFFFF"/>')
    text(lx, ly, label, cls)

x = 300
for fill, stroke, label in [("#FFF1EC", "#E4572E", "UC1 – Lê Xuân Khánh (524H0055)"), ("#EAF3FB", "#2E7DAF", "UC2 – Ngô Bình Minh (524H0169)"),
                            ("#FFF8E6", "#C98A1E", "Tier 4 extension"), ("#F7F9FB", SLATE, "included use case")]:
    svg.append(f'<ellipse cx="{x + 18}" cy="1004" rx="18" ry="10" fill="{fill}" stroke="{stroke}" stroke-width="1.7"/>')
    text(x + 44, 1010, label, "lg", "start")
    x += 70 + F["t"].getlength(label) * 16 / 17

head = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">
<defs>
<marker id="open" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="10" markerHeight="10" orient="auto"><path d="M0,0 L10,5 L0,10" fill="none" stroke="#3B4A5A" stroke-width="1.5"/></marker>
<marker id="gen" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="15" markerHeight="15" orient="auto"><path d="M0,0 L12,6 L0,12 z" fill="#FFFFFF" stroke="#1F2933" stroke-width="1.2"/></marker>
</defs>
<style>
.u{{font-size:17px;fill:#1F2933}} .ub{{font-size:17.5px;font-weight:700;fill:#12263A}} .us{{font-size:13.5px;fill:#5B6B7A}}
.a{{font-size:17px;font-weight:700;fill:#12263A}} .ai{{font-size:17px;font-weight:700;font-style:italic;fill:#12263A}}
.st{{font-size:14px;fill:#5B6B7A;font-style:italic}} .sys{{font-size:21px;font-weight:700;fill:#12263A}}
.dash{{stroke:#3B4A5A;stroke-width:1.4;stroke-dasharray:6 4}} .nt{{font-size:14.5px;fill:#1F2933}} .lg{{font-size:16px;fill:#1F2933}}
</style>"""
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "usecase_overview.svg"), "w", encoding="utf-8") as f:
    f.write(head + "\n" + "\n".join(svg) + "\n</svg>")
print("usecase_overview.svg", W, H)
