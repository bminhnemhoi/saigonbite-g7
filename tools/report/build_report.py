"""Build report v2.0 (Part 1 updated for Tier 4 + Part 2) from the team's Part 1 .docx.

Usage: python build_report.py <repo_root> <part1_docx> <template_docx> <out_docx> [--figma URL] [--github URL]
Large diagrams are placed on landscape pages so that their text stays readable (about 8 pt or more).
"""
import argparse
import copy
import datetime
import pathlib
import sys

import docx
import docx.text.paragraph
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from docx.table import Table
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import content_part2 as C  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("root"); ap.add_argument("part1"); ap.add_argument("template"); ap.add_argument("out")
ap.add_argument("--figma", default="[Figma link – added after publishing, see readme.txt]", help="Figma design file URL")
ap.add_argument("--figma-proto", default="", help="Figma prototype (Present) URL")
ap.add_argument("--github", default="https://github.com/bminhnemhoi/saigonbite-g7")
ap.add_argument("--part1-only", action="store_true", help="Part 1 resubmission: Tier 4 updates without the Part 2 chapter")
a = ap.parse_args()
ROOT = pathlib.Path(a.root)
UML, ARCH, UI = ROOT / "design/uml/out", ROOT / "design/architecture", ROOT / "design/ui/out"

doc = docx.Document(a.part1)
tpl = docx.Document(a.template)
body = doc.element.body
SLATE = RGBColor(0x5B, 0x6B, 0x7A)


# ------------------------------------------------------------------ helpers
def find_para(start):
    for p in doc.paragraphs:
        if p.text.strip().startswith(start):
            return p
    raise KeyError(start)


def set_para_text(p, text):
    runs = p.runs
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def data_rpr():
    """Run properties of a normal data cell in the team document (keeps fonts identical to Part 1)."""
    r = doc.tables[6].rows[1].cells[1].paragraphs[0].runs[0]._r
    return copy.deepcopy(r.rPr) if r.rPr is not None else None


DATA_RPR = data_rpr()


def write_cell(cell, text, bold=False):
    paras = text if isinstance(text, list) else [text]
    ppr = cell.paragraphs[0]._p.pPr
    ppr = copy.deepcopy(ppr) if ppr is not None else None
    for p in list(cell.paragraphs):
        p._p.getparent().remove(p._p)
    for t in paras:
        p = cell.add_paragraph()
        if ppr is not None:
            p._p.insert(0, copy.deepcopy(ppr))
        r = p.add_run(t)
        if DATA_RPR is not None:
            r._r.insert(0, copy.deepcopy(DATA_RPR))
        r.bold = True if bold else None
        r.italic = None
        r.font.color.rgb = RGBColor(0x1F, 0x29, 0x33)


def write_header(cell, text):
    """Replace a header cell's text but keep the template's header formatting."""
    p = cell.paragraphs[0]
    if p.runs:
        p.runs[0].text = text
        for r in p.runs[1:]:
            r._r.getparent().remove(r._r)
    else:
        p.add_run(text).bold = True
    for extra in cell.paragraphs[1:]:
        extra._p.getparent().remove(extra._p)


def end_insert(el):
    sect = body.find(qn("w:sectPr"))
    sect.addprevious(el)


def clone_rows(table, n):
    """Make the table have header + n data rows by cloning its first data row."""
    rows = table._tbl.findall(qn("w:tr"))
    first = rows[1]
    for r in rows[1:]:
        table._tbl.remove(r)
    for _ in range(n):
        table._tbl.append(copy.deepcopy(first))


def tpl_table(index, n_rows=None):
    tbl = copy.deepcopy(tpl.tables[index]._tbl)
    end_insert(tbl)
    t = Table(tbl, doc._body)
    if n_rows is not None:
        clone_rows(t, n_rows)
    return t


def para(text="", style=None, bold_lead=None, size=None, italic=False, align=None, space_after=None, keep=False):
    p = doc.add_paragraph(style=style) if style else doc.add_paragraph()
    if bold_lead:
        r = p.add_run(bold_lead); r.bold = True
    if text:
        r = p.add_run(text); r.italic = italic or None
        if size:
            r.font.size = Pt(size)
    if align:
        p.alignment = align
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    if keep:
        p.paragraph_format.keep_with_next = True
    return p


def link(p, url, text=None):
    """Append a clickable hyperlink run (kept as a live link in the PDF export); plain text when url is not a URL."""
    if not url.startswith("http"):
        return p.add_run(text or url)
    r_id = p.part.relate_to(url, RT.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), r_id)
    r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    col = OxmlElement("w:color"); col.set(qn("w:val"), "0563C1"); rpr.append(col)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rpr.append(u)
    r.append(rpr)
    t = OxmlElement("w:t"); t.text = text or url; t.set(qn("xml:space"), "preserve"); r.append(t)
    h.append(r); p._p.append(h)
    return h


def short_url(url):
    """https://www.figma.com/design/KEY/Title?... -> https://www.figma.com/design/KEY (the title part is optional)."""
    parts = url.split("?")[0].split("/")
    return "/".join(parts[:5]) if "figma.com" in url else url


def heading(text, level):
    return doc.add_paragraph(text, style=f"Heading {level}")


def section(landscape):
    s = doc.add_section(WD_SECTION.NEW_PAGE)
    if landscape:
        s.orientation, s.page_width, s.page_height = WD_ORIENT.LANDSCAPE, Inches(11), Inches(8.5)
        s.left_margin = s.right_margin = Inches(0.7)
        s.top_margin, s.bottom_margin = Inches(0.6), Inches(0.65)
    else:
        s.orientation, s.page_width, s.page_height = WD_ORIENT.PORTRAIT, Inches(8.5), Inches(11)
        s.left_margin = s.right_margin = Inches(1.0)
        s.top_margin, s.bottom_margin = Inches(0.8333), Inches(0.9028)
    return s


FIG = {"n": 0}


def figure(path, caption, max_w, max_h, number=None):
    im = Image.open(path)
    ratio = im.width / im.height
    w = min(max_w, max_h * ratio)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(path), width=Inches(w))
    FIG["n"] += 1
    n = number or f"2.{FIG['n']}"
    c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run(f"Figure {n}. "); r.bold = True; r.font.size = Pt(9.5)
    r = c.add_run(caption); r.italic = True; r.font.size = Pt(9.5); r.font.color.rgb = SLATE
    c.paragraph_format.space_after = Pt(10)
    return p


LAND = (9.6, 6.55)        # max image size on a landscape page (inches)
LAND_HALF = (9.6, 3.05)   # two figures on one landscape page
PORT = (6.5, 8.2)


def land_figure(path, caption):
    section(True)
    figure(path, caption, *LAND)


# ------------------------------------------------------------------ 1. cover, abstract, feedback log
if not a.part1_only:
    set_para_text(find_para("Part 1: Project Proposal & Requirements Engineering"), C.COVER_PART)
# brand on the cover: mark above the title, night-city band below it
title_p = doc.paragraphs[0]
for p in doc.paragraphs:
    if p.text.strip().startswith("SaigonBite"):
        title_p = p
        break
logo_p = title_p.insert_paragraph_before()
logo_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
logo_p.paragraph_format.space_after = Pt(4)
logo_p.add_run().add_picture(str(ROOT / "design/brand/mark-512.png"), width=Inches(0.85))
band_p = docx.text.paragraph.Paragraph(copy.deepcopy(logo_p._p), logo_p._parent)
title_p._p.addnext(band_p._p)
for r in list(band_p.runs):
    r._r.getparent().remove(r._r)
band_p.paragraph_format.space_before = Pt(6)
band_p.add_run().add_picture(str(UI / "cover_band.jpg"), width=Inches(5.8))
title_p.paragraph_format.space_before = Pt(8)
logo_p.paragraph_format.space_before = Pt(0)
# drop empty paragraphs directly before the logo so the cover keeps one page with the abstract
prev = logo_p._p.getprevious()
while prev is not None and prev.tag == qn("w:p") and not "".join(prev.itertext()).strip() and not prev.xpath(".//w:drawing"):
    nxt = prev.getprevious(); prev.getparent().remove(prev); prev = nxt
cov = doc.tables[0]
write_cell(cov.rows[1].cells[1], "Tier 4", bold=True)
write_cell(cov.rows[1].cells[2], "v1.1 (Tier 4 revision)" if a.part1_only else "v2.0 (Part 2)")
write_cell(cov.rows[1].cells[3], datetime.date(2026, 11, 20).strftime("%d %B %Y"))
write_cell(doc.tables[1].rows[1].cells[0], C.ABSTRACT_P1 if a.part1_only else C.ABSTRACT)
set_para_text(find_para("No feedback has been received"), C.FEEDBACK_INTRO)
fb = doc.tables[2]
for i, row in enumerate(C.FEEDBACK_ROWS_P1 if a.part1_only else C.FEEDBACK_ROWS):
    if i + 1 >= len(fb.rows):
        fb._tbl.append(copy.deepcopy(fb.rows[-1]._tr))
    for j, val in enumerate(row):
        write_cell(fb.rows[i + 1].cells[j], val, bold=(j == 0))

# ------------------------------------------------------------------ 2. Part 1 updates for Tier 4
tp = find_para("Technology tier.")
runs = tp.runs
rest = C.TIER_PARAGRAPH[len("Technology tier. "):]
runs[0].text = "Technology tier. "
runs[0].bold = True
if len(runs) > 1:
    runs[1].text = rest
    runs[1].bold = False
    for r in runs[2:]:
        r._r.getparent().remove(r._r)
else:
    tp.add_run(rest)

frt = doc.tables[6]
done = False
for row in frt.rows:
    for cell in row.cells:
        for p in cell.paragraphs:
            for r in p.runs:
                if C.FR22_OLD in r.text:
                    r.text = r.text.replace(C.FR22_OLD, C.FR22_NEW); done = True
if not done:
    print("warning: FR22 text not found")
for fr in C.NEW_FRS:
    frt._tbl.append(copy.deepcopy(frt.rows[-1]._tr))
    for j, val in enumerate(fr):
        write_cell(frt.rows[-1].cells[j], val, bold=(j == 0))
nfr = doc.tables[7]
nfr._tbl.append(copy.deepcopy(nfr.rows[-1]._tr))
for j, val in enumerate(C.NEW_NFR):
    write_cell(nfr.rows[-1].cells[j], val, bold=(j in (0, 1)))
amb = doc.tables[8]
for row in amb.rows[1:]:
    aid = row.cells[0].text.strip()
    write_cell(row.cells[3], C.ASSUMPTION_ANSWERS.get(aid, C.ASSUMPTION_DEFAULT))
find_para("The specification deliberately leaves some decisions open")
amb_p = find_para("The specification deliberately leaves some decisions open")
set_para_text(amb_p, "The specification deliberately leaves some decisions open. The team records each gap below with the assumption it "
                     "designs and tests against, and the requirements that depend on it. The assumptions were presented at Presentation 1; "
                     "A-01, A-02 and A-06 were raised explicitly for confirmation. Written answers will be recorded here and in the Team Workbook.")

if not a.part1_only:
    # ------------------------------------------------------------------ 3. detach References + Appendix, then append Part 2
    ref_h = find_para("References")
    tail, el = [], ref_h._p
    while el is not None and el.tag != qn("w:sectPr"):
        nxt = el.getnext()
        tail.append(el)
        el.getparent().remove(el)
        el = nxt

    h = heading("Part 2: Software Design, Architecture & UI/UX (20 marks)", 1)
    h.paragraph_format.page_break_before = True
    para(C.P2_INTRO)

    # 2.1
    heading("2.1 Overall Use Case Diagram", 2)
    para(C.UC_OVERVIEW)
    p = para(bold_lead="Project links: ")
    p.add_run("GitHub repository "); link(p, a.github)
    if a.figma.startswith("http"):
        p.add_run(" · Figma file "); link(p, a.figma, short_url(a.figma))
    if a.figma_proto:
        p.add_run(" · clickable prototype "); link(p, a.figma_proto, short_url(a.figma_proto))
    land_figure(UML / "usecase_overview.png", "Overall use case diagram – system boundary, actor generalisation Customer → Local Customer / Foreign Tourist, UC1 and UC2 owners and the Tier 4 extension.")

    # 2.2
    section(False)
    heading("2.2 Use Case Specifications", 2)
    para("Each specification cites the FR and BR IDs of Part 1. The post-conditions are written so that they can be checked directly by the Part 3 test cases.")


    def spec(title, s):
        heading(title, 3)
        t = tpl_table(9)
        vals = [s["name"], s["actors"], s["ids"], s["pre"], s["main"], s["alt"], s["exc"], s["post"]]
        for i, v in enumerate(vals):
            write_cell(t.rows[i + 1].cells[1], v)


    spec("2.2.1 Use Case 1: Place and Manage Orders (author: 524H0055 – Lê Xuân Khánh)", C.UC1_SPEC)
    doc.add_paragraph()
    spec("2.2.2 Use Case 2: Manage Hubs & Capacity (author: 524H0169 – Ngô Bình Minh)", C.UC2_SPEC)

    # 2.3
    section(False)
    heading("2.3 Behavioral Diagrams", 2)
    heading("2.3.1 Sequence Diagrams for Use Case 1 (author: 524H0055)", 3)
    para(C.SEQ_TEXT_UC1)
    land_figure(UML / "seq_uc1_place_order_1.png", "UC1 sequence diagram, part 1 – check the hub load and quote the price (BR1–BR12, BR8).")
    land_figure(UML / "seq_uc1_place_order_2.png", "UC1 sequence diagram, part 2 – choose the payment strategy and save the order in one transaction (BR13, BR14, NFR5, NFR6).")
    land_figure(UML / "seq_tier4_paypal_sandbox.png", "Tier 4 – PayPal Developer sandbox flow: create order, buyer approval, capture or cancel (FR36).")
    section(False)
    heading("2.3.2 Sequence Diagrams for Use Case 2 (author: 524H0169)", 3)
    para(C.SEQ_TEXT_UC2)
    land_figure(UML / "seq_uc2_manage_hubs_1.png", "UC2 sequence diagram, part 1 – create a hub and list hubs with their current load (FR5, FR6, BR7, BR8).")
    land_figure(UML / "seq_uc2_manage_hubs_2.png", "UC2 sequence diagram, part 2 – edit a hub and deactivate it as a soft-delete (FR24, A-07).")
    section(False)
    heading("2.3.3 Order State Diagram (team)", 3)
    para(C.STATE_TEXT)
    figure(UML / "state_order.png", "Order lifecycle state diagram – 8 states, triggering actors, guards and entry actions (BR14–BR16, A-01, A-02).", 6.3, 7.0)

    # 2.4
    section(False)
    heading("2.4 Structural & CRC Design", 2)
    heading("2.4.1 CRC Cards", 3)
    para(C.CRC_INTRO)
    t = tpl_table(10, len(C.CRC))
    for i, row in enumerate(C.CRC):
        for j, v in enumerate(row):
            write_cell(t.rows[i + 1].cells[j], v, bold=(j == 0))
    heading("2.4.2 UML Class Diagrams", 3)
    para(C.CLASS_TEXT)
    land_figure(UML / "class_users.png", "Class diagram – User generalisation: Local Customers and Foreign Tourists share one schema (BR18, FR1).")
    land_figure(UML / "class_orders.png", "Class diagram – ordering model with the price snapshot and price breakdown value objects (BR10, BR17).")
    land_figure(UML / "class_services.png", "Class diagram – business-layer services behind interfaces; pricing rules only in PricingService (NFR2).")
    land_figure(UML / "class_strategy.png", "Class diagram – payment Strategy pattern: one interface, one class per method, selection by customer type (BR13).")
    section(False)
    heading("2.4.3 Database Design Notes", 3)
    para("The physical model below is generated by EF Core Code First migrations. Figures 2.12 and 2.13 split the ERD into accounts and catalogue, and orders and payments; key columns only.")
    t = tpl_table(11, len(C.DB_NOTES))
    write_header(t.rows[0].cells[0], "Design decision")
    write_header(t.rows[0].cells[1], "How and why")
    for i, (k, v) in enumerate(C.DB_NOTES):
        write_cell(t.rows[i + 1].cells[0], k, bold=True)
        write_cell(t.rows[i + 1].cells[1], v)
    section(False)
    figure(UML / "erd_accounts_catalogue.png", "ERD (crow’s foot) – accounts, staff, hubs and catalogue. Customer generalisation as table-per-type.", 6.5, 8.0)
    land_figure(UML / "erd_orders_payments.png", "ERD (crow’s foot) – orders, lines, status history and payments with the BR17 snapshot columns.")

    # 2.5
    section(False)
    heading("2.5 Architecture & Quality Design", 2)
    para(C.ARCH_TEXT)
    t = tpl_table(11)
    for i, (k, v) in enumerate(C.PRINCIPLES):
        write_cell(t.rows[i + 1].cells[1], v)
    para()
    para("Design of the three Tier 4 parts", bold_lead=None).runs[0].bold = True
    for lead_txt, txt in C.TIER4_TEXT:
        para(txt, bold_lead=lead_txt)
    land_figure(ARCH / "architecture_layers.png", "Architecture – ASP.NET Core MVC in three layers with NFR tags, cross-cutting concerns and quality gates.")
    section(True)
    figure(ARCH / "request_pipeline.png", "Request pipeline – one “place order” request through the layers in one transaction.", *LAND_HALF)
    figure(ARCH / "pricing_pipeline.png", "Pricing pipeline inside PricingService – the BR10 order with both worked examples.", *LAND_HALF)

    # 2.6
    section(False)
    heading("2.6 UI/UX Design", 2)
    para(C.UI_TEXT)
    p = para(bold_lead="Figma design file (public, anyone with the link can view): ")
    link(p, a.figma, short_url(a.figma))
    if a.figma_proto:
        p = para(bold_lead="Clickable prototype (opens in Present mode, Fit width, at flow 1 – the landing page): ")
        link(p, a.figma_proto, short_url(a.figma_proto))
    para("The Figma file has three pages: 00 Cover & design system (brand essentials); 01–04 Sketch → Wireframe → Mock-up, with one section per stage (01 Sketch, 02 Wireframe, 03 Mock-up desktop, 04 Mock-up mobile 390 px); and 05 Prototype, with three flows: Local customer with cash, Foreign tourist with the PayPal sandbox, and Admin with hubs and reports.")
    t = tpl_table(10, len(C.UI_MAP))
    for j, hdr in enumerate(["Screen", "Requirements shown", "Figure"]):
        write_header(t.rows[0].cells[j], hdr)
    for i, row in enumerate(C.UI_MAP):
        for j, v in enumerate(row):
            write_cell(t.rows[i + 1].cells[j], v)
    land_figure(UI / "ui_stages.png", "The four UI/UX stages for the Local checkout screen: sketch, wireframe, mock-up and prototype click areas.")
    screens = [
        ("01-home", "Customer home – hubs near the address with load bands: Quiet −10%, Normal, Full (≥ 90%) and out of the 8 km coverage."),
        ("02-menu", "Hub TD menu and brand browsing with real dishes; unavailable item disabled (BR12); cart with S = 200,000 ₫."),
        ("03-checkout-local", "Local Customer checkout – BR10 price breakdown of the specification example (205,000 ₫) and MoMo, VNPay, COD enabled."),
        ("04-checkout-tourist", "Foreign Tourist checkout – voucher, free delivery, rain surcharge, rounding (269,000 ₫); Apple Pay, PayPal and COD enabled."),
        ("05-paypal-success", "Tier 4 – payment captured by the PayPal Developer sandbox, capture ID stored on the order."),
        ("06-tracking", "Order tracking – status history, price snapshot and the cancel rule (BR16, BR17)."),
        ("07-register", "Registration – Local Customer by phone and OTP, Foreign Tourist by passport and email (BR18)."),
        ("08-kitchen", "Kitchen board – confirm, reject with a reason, start cooking, mark ready; live hub load."),
        ("10-admin-dashboard", "Tier 4 – interactive Admin dashboard: KPIs, revenue trend, live hub load, orders by state, payment mix, heavy-rain switch."),
        ("11-admin-hubs", "UC2 – hubs with capacity, active orders and load bands; inactive hub kept for history."),
        ("12-admin-hub-edit", "UC2 – edit hub with capacity validation and deactivation blocked by active orders (A-07)."),
    ]
    for name, cap in screens:
        land_figure(UI / f"{name}.png", cap)
    land_figure(UI / "ui_phones.png", "Responsive layout at 390 px on a phone: menu with cart, checkout with the BR10 breakdown, tracking and the shipper screen (COD confirmation, failed delivery).")
    land_figure(UI / "13-report-r1.png", "Revenue report R1 – by brand category and payment method, Cancelled and Failed orders excluded (FR25).")
    land_figure(UI / "14-report-r2.png", "Hub utilization report R2 – orders handled, average preparation time, current load and Quiet Kitchen discounts (FR26).")
    land_figure(UI / "landing_overview.png", "Landing page – real night photographs of Ho Chi Minh City, Quiet Kitchen pricing, transparent price example and both payment groups; motion in landing_motion.mp4.")
    land_figure(UI / "00-sign-in.png", "Sign in – Bến Thành Market at night, phone or passport / email login, EN/VI toggle (FR2–FR4, NFR3).")

    # ------------------------------------------------------------------ 4. re-attach References and Appendix in portrait
    section(False)
    for el in tail:
        end_insert(el)
    ref_last = None
    for p in doc.paragraphs:
        if p.text.strip().startswith("7. K. Schwaber"):
            ref_last = p
    anchor = ref_last._p
    for txt in C.EXTRA_REFS:
        new_p = copy.deepcopy(ref_last._p)
        anchor.addnext(new_p)
        anchor = new_p
        from docx.text.paragraph import Paragraph
        np_ = Paragraph(new_p, ref_last._parent)
        set_para_text(np_, txt)

ai = doc.tables[-1]
for row in (C.AI_ROWS_P1 if a.part1_only else C.AI_ROWS):
    ai._tbl.append(copy.deepcopy(ai.rows[-1]._tr))
    for j, v in enumerate(row):
        write_cell(ai.rows[-1].cells[j], v)

doc.core_properties.title = ("SaigonBite – Team G7 – Part 1 report (v1.1, Tier 4)" if a.part1_only else "SaigonBite – Team G7 – Part 1 and Part 2 report (v2.0)")
doc.core_properties.author = "Team G7 (524H0055, 524H0169)"
doc.save(a.out)
print("saved", a.out, "figures:", FIG["n"])
