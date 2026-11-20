"""Render brand assets (logo lock-ups, mark, brand sheet) to PNG. Usage: python render_brand.py <repo_root>"""
import pathlib
import shutil
import sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(sys.argv[1]).resolve()
BR = ROOT / "design" / "brand"
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    pg = b.new_page(device_scale_factor=3, viewport={"width": 1700, "height": 1200})
    pg.goto((BR / "brand.html").as_uri())
    pg.wait_for_load_state("networkidle")
    pg.wait_for_timeout(500)
    for el, name in (("#logo-light", "logo-horizontal.png"), ("#logo-dark", "logo-horizontal-dark.png"), ("#logo-ondark", "logo-horizontal-white.png"), ("#sheet", "brand-sheet.png")):
        # transparent page background for the logo files, so they sit cleanly on photos and dark slides
        pg.evaluate("t => { document.documentElement.style.background = t; document.body.style.background = t; }",
                    "#fff" if el == "#sheet" else "transparent")
        pg.locator(el).screenshot(path=str(BR / name), omit_background=(el != "#sheet"))
        print("png", name)
    pg2 = b.new_page(device_scale_factor=1, viewport={"width": 512, "height": 512})
    svg = (BR / "mark.svg").read_text(encoding="utf-8").replace("<svg ", '<svg width="512" height="512" ', 1)
    pg2.set_content(f'<html><body style="margin:0;background:transparent">{svg}</body></html>')
    pg2.locator("svg").screenshot(path=str(BR / "mark-512.png"), omit_background=True)
    print("png mark-512.png")
    b.close()
dst = ROOT / "design" / "ui" / "assets" / "brand"
dst.mkdir(parents=True, exist_ok=True)
for f in ("mark.svg", "mark-512.png", "logo-horizontal.png", "logo-horizontal-dark.png", "logo-horizontal-white.png"):
    shutil.copyfile(BR / f, dst / f)
