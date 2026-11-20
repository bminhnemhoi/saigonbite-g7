"""Render SVG or HTML files to crisp PNG with Edge (Playwright). Usage: python svg2png.py scale file1.svg [file2.html ...]"""
import pathlib
import sys
from playwright.sync_api import sync_playwright

scale = float(sys.argv[1])
files = [pathlib.Path(f).resolve() for f in sys.argv[2:]]
with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")
    for f in files:
        page = browser.new_page(device_scale_factor=scale, viewport={"width": 800, "height": 600})
        if f.suffix == ".svg":
            svg = f.read_text(encoding="utf-8")
            page.set_content(f'<html><body style="margin:0;background:#fff">{svg}</body></html>')
            el = page.locator("svg").first
        else:
            page.goto(f.as_uri())
            page.wait_for_load_state("networkidle")
            el = page.locator("#capture").first
        el.screenshot(path=str(f.with_suffix(".png")))
        page.close()
        print("png", f.with_suffix(".png").name)
    browser.close()
