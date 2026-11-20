"""Record the animated landing page (Ken Burns hero, counters, scroll reveals, marquee) to MP4 and a hero GIF.
Usage: python record_landing.py <ui_dir> <ffmpeg.exe>"""
import pathlib
import shutil
import subprocess
import sys
import tempfile
from playwright.sync_api import sync_playwright

UI = pathlib.Path(sys.argv[1]).resolve()
FFMPEG = sys.argv[2]
OUT = UI / "out"
tmp = pathlib.Path(tempfile.mkdtemp())
with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, record_video_dir=str(tmp), record_video_size={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.goto((UI / "screens" / "00-landing.html").as_uri())
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(4200)                      # hero: Ken Burns, glow, counters
    height = page.evaluate("document.documentElement.scrollHeight")
    y = 0
    while y < height - 900:
        y = min(y + 14, height - 900)
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(16)
        if y in (900, 1806, 2800, 3500, 4300):      # short pauses on each section
            page.wait_for_timeout(900)
    page.wait_for_timeout(1800)
    video = page.video.path()
    ctx.close()
    browser.close()
mp4 = OUT / "landing_motion.mp4"
subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(video), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-movflags", "+faststart", str(mp4)], check=True)
shutil.rmtree(tmp, ignore_errors=True)
print("video", mp4.stat().st_size // 1024, "KB")
