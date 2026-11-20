"""Screenshot the Bootstrap prototype screens and record clickable hot-spots for the Figma plugin.

Usage: python shoot.py <ui_dir> [screen ...]
For every screen it writes out/<screen>.png (desktop 1440 wide, mock-up), and when listed in VARIANTS
also -mobile (390 wide), -wire (wireframe) and -sketch (sketch) images. Hot-spots (elements with
data-goto) are saved to out/hotspots.json in CSS pixels of the desktop or mobile frame.
"""
import json
import pathlib
import sys
from playwright.sync_api import sync_playwright

UI = pathlib.Path(sys.argv[1]).resolve()
ONLY = set(sys.argv[2:])
SCREENS = sorted(p.stem for p in (UI / "screens").glob("*.html"))
MOBILE = {"02-menu", "03-checkout-local", "06-tracking", "09-shipper"}
LOWFI = {"01-home", "02-menu", "03-checkout-local", "04-checkout-tourist", "06-tracking", "08-kitchen", "11-admin-hubs", "13-report-r1"}
OUT = UI / "out"
OUT.mkdir(exist_ok=True)
hot_path = OUT / "hotspots.json"
hot = json.loads(hot_path.read_text(encoding="utf-8")) if hot_path.exists() else {}


def shoot(page, name, url, width, suffix):
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(url)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(600)  # fonts and charts
    path = OUT / f"{name}{suffix}.png"
    page.screenshot(path=str(path), full_page=True)
    spots = page.eval_on_selector_all("[data-goto]", """els => els.map(e => {
        const r = e.getBoundingClientRect();
        return {target: e.dataset.goto, x: Math.round(r.left + scrollX), y: Math.round(r.top + scrollY),
                w: Math.round(r.width), h: Math.round(r.height)}; }).filter(s => s.w > 0 && s.h > 0)""")
    size = page.evaluate("() => [document.documentElement.scrollWidth, document.documentElement.scrollHeight]")
    return path, spots, size


with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")
    page = browser.new_page(device_scale_factor=2)
    for name in SCREENS:
        if ONLY and name not in ONLY:
            continue
        url = (UI / "screens" / f"{name}.html").as_uri()
        if name == "00-landing":
            url += "?static=1"
        width = 390 if name == "09-shipper" else 1440
        path, spots, size = shoot(page, name, url, width, "")
        hot[name] = {"w": size[0], "h": size[1], "spots": spots}
        print("shot", path.name, size)
        if name in MOBILE and name != "09-shipper":
            path, spots, size = shoot(page, name, url, 390, "-mobile")
            hot[name + "-mobile"] = {"w": size[0], "h": size[1], "spots": spots}
            print("shot", path.name, size)
        if name in LOWFI:
            for mode in ("wire", "sketch"):
                path, _, size = shoot(page, name, url + f"?mode={mode}", width, f"-{mode}")
                print("shot", path.name, size)
    browser.close()
hot_path.write_text(json.dumps(hot, indent=1), encoding="utf-8")
