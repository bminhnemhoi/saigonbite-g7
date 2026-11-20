"""Part 1 resubmission extras: AI usage log (Appendix) with the Tier 4 revision row, and the Marking Sheet tier.
Usage: python update_part1_extras.py <appendix_in.docx> <appendix_out.docx> <marking_in.xlsx> <marking_out.xlsx>"""
import copy
import sys
import docx
import openpyxl
from docx.shared import RGBColor

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
import content_part2 as C  # noqa: E402

app_in, app_out, mk_in, mk_out = sys.argv[1:5]
d = docx.Document(app_in)
info, log = d.tables[0], d.tables[1]
cell = info.rows[1].cells[3]
cell.paragraphs[0].runs[0].text = "26 October 2026 · revised 20 November 2026 (Tier 4)"
for r in cell.paragraphs[0].runs[1:]:
    r._r.getparent().remove(r._r)
for row in C.AI_ROWS_P1:
    log._tbl.append(copy.deepcopy(log.rows[-1]._tr))
    for j, v in enumerate(row):
        c = log.rows[-1].cells[j]
        first = c.paragraphs[0]
        rpr = copy.deepcopy(first.runs[0]._r.rPr) if first.runs and first.runs[0]._r.rPr is not None else None
        for p in list(c.paragraphs):
            p._p.getparent().remove(p._p)
        np_ = c.add_paragraph()
        run = np_.add_run(v.replace(", 20 Nov 2026", "\n20 Nov 2026"))
        if rpr is not None:
            run._r.insert(0, rpr)
d.save(app_out)
print("appendix rows", len(log.rows))

wb = openpyxl.load_workbook(mk_in)
s = wb["Summary"]
s["B6"] = "Tier 4"
wb.save(mk_out)
print("marking sheet tier", s["B6"].value)
