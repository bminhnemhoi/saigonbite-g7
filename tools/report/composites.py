"""Composite figures for the report and slides: UI design stages and the responsive mobile set.
Usage: python composites.py <repo_root>"""
import json
import pathlib
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(sys.argv[1])
OUT = ROOT / "design" / "ui" / "out"
FB = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 46)
FR = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 32)
NAVY, CHILI = (18, 38, 58), (228, 87, 46)


def stages(screen="03-checkout-local"):
    hot = json.loads((OUT / "hotspots.json").read_text(encoding="utf-8"))[screen]
    panels = []
    titles = [("1  Sketch", "paper-style layout of blocks"), ("2  Wireframe", "grey boxes, real content order"),
              ("3  Mock-up", "brand colours, real photos, real prices"), ("4  Prototype", "click areas linked in Figma")]
    for i, mode in enumerate(["-sketch", "-wire", "", ""]):
        im = Image.open(OUT / f"{screen}{mode}.png").convert("RGB")
        if i == 3:  # draw the click areas recorded for the Figma prototype
            d = ImageDraw.Draw(im, "RGBA")
            sx = im.width / hot["w"]
            for s in hot["spots"]:
                box = [s["x"] * sx, s["y"] * sx, (s["x"] + s["w"]) * sx, (s["y"] + s["h"]) * sx]
                d.rectangle(box, outline=CHILI + (255,), width=8, fill=CHILI + (40,))
                d.text((box[0] + 10, box[3] + 8), "→ " + s["target"], font=FR, fill=CHILI)
        im = im.crop((0, 0, im.width, min(im.height, int(im.width * 0.68))))
        im = im.resize((1400, int(1400 * im.height / im.width)), Image.LANCZOS)
        panels.append(im)
    w, h = panels[0].width, max(p.height for p in panels)
    pad, head = 40, 110
    canvas = Image.new("RGB", (2 * w + 3 * pad, 2 * (h + head) + 3 * pad), "white")
    d = ImageDraw.Draw(canvas)
    for i, p in enumerate(panels):
        x = pad + (i % 2) * (w + pad)
        y = pad + (i // 2) * (h + head + pad)
        d.text((x, y), titles[i][0], font=FB, fill=NAVY)
        d.text((x + FB.getlength(titles[i][0]) + 24, y + 12), titles[i][1], font=FR, fill=(91, 107, 122))
        canvas.paste(p, (x, y + head - 20))
        d.rectangle([x - 1, y + head - 21, x + p.width, y + head - 20 + p.height], outline=(200, 209, 218), width=3)
    canvas.save(OUT / "ui_stages.png", optimize=True)
    print("ui_stages.png", canvas.size)


def mobiles():
    names = [("02-menu-mobile", "Menu & cart"), ("03-checkout-local-mobile", "Checkout"), ("06-tracking-mobile", "Tracking"), ("09-shipper", "Shipper")]
    ims = []
    for n, _ in names:
        im = Image.open(OUT / f"{n}.png").convert("RGB")
        im = im.crop((0, 0, im.width, min(im.height, int(im.width * 2.05))))
        im = im.resize((640, int(640 * im.height / im.width)), Image.LANCZOS)
        ims.append(im)
    h = max(i.height for i in ims)
    pad, head = 40, 90
    canvas = Image.new("RGB", (4 * 640 + 5 * pad, h + head + 2 * pad + 20), (245, 247, 250))
    d = ImageDraw.Draw(canvas)
    for k, (im, (_, title)) in enumerate(zip(ims, names)):
        x = pad + k * (640 + pad)
        d.text((x, pad), title, font=FB, fill=NAVY)
        d.rounded_rectangle([x - 14, pad + head - 14, x + 654, pad + head + im.height + 14], radius=46, fill=NAVY)
        canvas.paste(im, (x, pad + head))
    canvas.save(OUT / "ui_mobile_set.png", optimize=True)
    print("ui_mobile_set.png", canvas.size)


stages()
mobiles()


def landing():
    im = Image.open(OUT / "00-landing.png").convert("RGB")
    full = im.resize((round(im.width * 1900 / im.height), 1900), Image.LANCZOS)
    hero = im.crop((0, 0, im.width, round(im.width * 910 / 1440)))
    hero = hero.resize((round(hero.width * 1900 / hero.height), 1900), Image.LANCZOS)
    pad = 50
    canvas = Image.new("RGB", (full.width + hero.width + 3 * pad, 1900 + 2 * pad + 90), "white")
    d = ImageDraw.Draw(canvas)
    d.text((pad, pad - 10), "Whole page (scroll)", font=FB, fill=NAVY)
    d.text((full.width + 2 * pad, pad - 10), "Hero section at 1440 × 910 – night-city photo with motion", font=FB, fill=NAVY)
    canvas.paste(full, (pad, pad + 80)); canvas.paste(hero, (full.width + 2 * pad, pad + 80))
    for x, w in ((pad, full.width), (full.width + 2 * pad, hero.width)):
        d.rectangle([x - 2, pad + 78, x + w + 1, pad + 81 + 1900], outline=(200, 209, 218), width=4)
    canvas.save(OUT / "landing_overview.png", optimize=True)
    print("landing_overview.png", canvas.size)


landing()


def landing_hero():
    im = Image.open(OUT / "00-landing.png").convert("RGB")
    hero = im.crop((0, 0, im.width, round(im.width * 910 / 1440))).resize((1920, 1213), Image.LANCZOS)
    hero.save(OUT / "landing_hero.png", optimize=True)
    print("landing_hero.png", hero.size)


landing_hero()


def cover_band():
    im = Image.open(ROOT / "design/ui/assets/img/ctx-night-skyline-river.jpg").convert("RGB")
    w, h = im.size
    th = round(w / 3.6)
    band = im.crop((0, max(0, (h - th) // 2 + round(h * 0.08)), w, max(0, (h - th) // 2 + round(h * 0.08)) + th)).resize((2400, 667), Image.LANCZOS)
    band.save(OUT / "cover_band.jpg", quality=90)
    print("cover_band.jpg", band.size)


cover_band()


def phones():
    """Four mobile screens in realistic phone frames on a soft gradient (slides)."""
    names = ["02-menu-mobile", "03-checkout-local-mobile", "06-tracking-mobile", "09-shipper"]
    W, H = 3600, 1840
    bg = Image.new("RGB", (W, H))
    top, bot = (243, 246, 250), (226, 233, 240)
    for y in range(H):
        k = y / H
        ImageDraw.Draw(bg).line([(0, y), (W, y)], fill=tuple(round(top[i] + (bot[i] - top[i]) * k) for i in range(3)))
    pw, ph = 720, 1500                      # phone body
    sw, sh = pw - 52, ph - 52               # screen
    gap = (W - 4 * pw) // 5
    for i, n in enumerate(names):
        im = Image.open(OUT / f"{n}.png").convert("RGB")
        page = im.resize((sw, round(im.height * sw / im.width)), Image.LANCZOS)
        top_px = page.getpixel((8, 8))
        dark = sum(top_px) < 300
        bar_h = 92
        screen = Image.new("RGB", (sw, sh), top_px)
        screen.paste(page.crop((0, 0, sw, sh - bar_h)), (0, bar_h))
        gd = ImageDraw.Draw(screen)
        ink = (255, 255, 255) if dark else (18, 24, 32)
        ft = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 34)
        gd.text((64, 26), "15:04", font=ft, fill=ink)
        bx = sw - 70                                   # battery
        gd.rounded_rectangle([bx - 52, 34, bx, 58], radius=7, outline=ink, width=3)
        gd.rectangle([bx - 46, 40, bx - 14, 52], fill=ink)
        gd.rectangle([bx + 2, 41, bx + 6, 51], fill=ink)
        for k in range(4):                             # signal bars
            gd.rounded_rectangle([bx - 128 + k * 13, 56 - (k + 1) * 6, bx - 120 + k * 13, 58], radius=2, fill=ink)
        gd.rounded_rectangle([sw // 2 - 110, sh - 26, sw // 2 + 110, sh - 16], radius=5, fill=(30, 36, 44) if not dark else (230, 234, 238))
        x = gap + i * (pw + gap)
        y = 230 + (40 if i % 2 else 0)
        sh_img = Image.new("RGBA", (pw + 120, ph + 120), (0, 0, 0, 0))
        ImageDraw.Draw(sh_img).rounded_rectangle([60, 80, pw + 60, ph + 70], radius=110, fill=(18, 38, 58, 70))
        from PIL import ImageFilter
        sh_img = sh_img.filter(ImageFilter.GaussianBlur(28))
        bg.paste(sh_img, (x - 60, y - 40), sh_img)
        d = ImageDraw.Draw(bg)
        d.rounded_rectangle([x, y, x + pw, y + ph], radius=104, fill=(16, 20, 26))
        d.rounded_rectangle([x + 6, y + 6, x + pw - 6, y + ph - 6], radius=98, outline=(58, 66, 78), width=4)
        mask = Image.new("L", (sw, sh), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, sw - 1, sh - 1], radius=80, fill=255)
        bg.paste(screen, (x + 26, y + 26), mask)
        d.rounded_rectangle([x + pw // 2 - 95, y + 44, x + pw // 2 + 95, y + 92], radius=24, fill=(16, 20, 26))
    labels = ["Menu & cart", "Checkout · BR10 breakdown", "Order tracking", "Shipper · COD confirm"]
    f = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 58)
    d = ImageDraw.Draw(bg)
    for i, t in enumerate(labels):
        x = gap + i * (pw + gap) + pw // 2
        d.text((x - f.getlength(t) / 2, 90), t, font=f, fill=NAVY)
    bg.save(OUT / "ui_phones.png", optimize=True)
    print("ui_phones.png", bg.size)


phones()
