"""Rebuild and package the Part 2 submission (optionally with the public Figma link).

Usage:
    python tools/finalize_part2.py --figma "https://www.figma.com/..."   # insert the link: readme, report, slides
    python tools/finalize_part2.py                                       # rebuild the report only
    python tools/finalize_part2.py --sync                                # move _pending/ files into place
Steps: readme.txt link -> report .docx -> PDF (Word, bookmarks) -> [slides .pptx -> PDF] -> zip -> repo docs/part2 (+ git push).
A file that is open in another program (Foxit, PowerPoint) cannot be replaced; its new version is kept in
G7_Part2_Submission/_pending/ and the zip is always built from the fresh files. Close the program and run --sync.
"""
import argparse
import os
import pathlib
import shutil
import subprocess
import tempfile
import zipfile

REPO = pathlib.Path(__file__).resolve().parents[1]
FINAL = REPO.parent
SUB = FINAL / "G7_Part2_Submission"
PENDING = SUB / "_pending"
PLACEHOLDER = "[PASTE THE FIGMA LINK HERE]"
SKILL = os.environ.get("SKILL_DIR", r"C:/Users/Admin/.claude/skills/synced/8970aa71-7356-41c7-8ab9-a47bd6676d1b_95e5a8cc-809a-4ef6-be97-2ea8dc6b6f10/pptx")
PACKAGE = ("TeamG7_Part2_Design.pdf", "TeamG7_Part2_Presentation.pptx", "readme.txt")

ap = argparse.ArgumentParser()
ap.add_argument("--figma", default="", help="public Figma link")
ap.add_argument("--slides", action="store_true", help="rebuild the slides even without --figma")
ap.add_argument("--sync", action="store_true", help="only move _pending/ files into place")
ap.add_argument("--no-push", action="store_true")
a = ap.parse_args()
pending = []


def run(*cmd, **kw):
    print(">", " ".join(str(c) for c in cmd)[:140])
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def put(src, dst):
    """Copy src to dst; when dst is locked by another program keep the new file in _pending/."""
    try:
        shutil.copyfile(src, dst)
    except PermissionError:
        PENDING.mkdir(exist_ok=True)
        shutil.copyfile(src, PENDING / dst.name)
        pending.append(dst)


if a.sync:
    for f in sorted(PENDING.glob("*")) if PENDING.exists() else []:
        target = (SUB / "_extras" / f.name) if f.name.endswith("_backup.pdf") else (SUB / f.name)
        try:
            shutil.copyfile(f, target)
            f.unlink()
            print("updated", target.name)
        except PermissionError:
            print("still open in another program:", target.name)
    if PENDING.exists() and not any(PENDING.iterdir()):
        PENDING.rmdir()
    raise SystemExit

tmp = pathlib.Path(tempfile.mkdtemp())          # ASCII temp path for Office automation
fresh = {name: SUB / name for name in PACKAGE}

# 1. readme.txt
readme = SUB / "readme.txt"
if a.figma:
    readme.write_text(readme.read_text(encoding="utf-8").replace(PLACEHOLDER, a.figma), encoding="utf-8")

# 2. report -> PDF with bookmarks
figma_args = ["--figma", a.figma] if a.figma else []
run("python", "-X", "utf8", REPO / "tools/report/build_report.py", REPO,
    FINAL / "G7_Part1_Revised/_editable_source (not for submission)/TeamG7_SE_Final_Report_SaigonBite.docx",
    FINAL / "drive-download-20261025T122604Z-1-001/SE_Sem01_2627_Report_Template.docx", tmp / "report.docx", *figma_args)
run("cscript", "//nologo", REPO / "tools/report/docx2pdf.vbs", tmp / "report.docx", tmp / "report.pdf")
put(tmp / "report.docx", SUB / "_source/TeamG7_Part2_Design.docx")
put(tmp / "report.pdf", SUB / "TeamG7_Part2_Design.pdf")
fresh["TeamG7_Part2_Design.pdf"] = tmp / "report.pdf"

# 3. slides -> PDF backup (only when the link changes the slides or when asked)
if a.figma or a.slides:
    env = dict(os.environ, SKILL_DIR=SKILL, NODE_PATH=str(REPO / "tools/slides/node_modules"))
    run("node", REPO / "tools/slides/build_slides.js", tmp / "deck.pptx", *([a.figma] if a.figma else []), env=env, cwd=REPO / "tools/slides")
    run("powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", REPO / "tools/slides/topdf.ps1",
        "-In", tmp / "deck.pptx", "-Out", tmp / "deck.pdf")
    put(tmp / "deck.pptx", SUB / "TeamG7_Part2_Presentation.pptx")
    put(tmp / "deck.pdf", SUB / "_extras/TeamG7_Part2_Presentation_backup.pdf")
    fresh["TeamG7_Part2_Presentation.pptx"] = tmp / "deck.pptx"

# 4. zip for eLearning, always from the fresh files
zpath = SUB / "G7_PART2_SUBMISSION_524H0055_524H0169.zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for name, src in fresh.items():
        z.write(src, name)
print("zip", zpath.name, zpath.stat().st_size // 1024, "KB")

# 5. repository copy (+ push)
for name, src in fresh.items():
    shutil.copyfile(src, REPO / "docs/part2" / name)
if not a.no_push:
    run("git", "-C", REPO, "add", "docs/part2")
    msg = "Add the public Figma link to the Part 2 submission" if a.figma else "Rebuild the Part 2 submission"
    if subprocess.run(["git", "-C", str(REPO), "diff", "--cached", "--quiet"]).returncode:
        run("git", "-C", REPO, "commit", "-q", "-m", msg, "-m", "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
        run("git", "-C", REPO, "push", "-q")
shutil.rmtree(tmp, ignore_errors=True)
for p in pending:
    print("OPEN IN ANOTHER PROGRAM – new version kept in _pending/:", p.name, "-> close it and run: python tools/finalize_part2.py --sync")
print("done")
