"""Build the Figma development plugin that assembles the whole SaigonBite Part 2 Figma file.

It embeds the prototype screenshots (sketch, wireframe, desktop + mobile mock-ups) and the click
hot-spots recorded by tools/ui/shoot.py. Running the plugin once in Figma creates the pages, frames,
prototype links and flow starting points. Usage: python build_plugin.py <repo_root>
"""
import base64
import io
import json
import pathlib
import sys
from PIL import Image

ROOT = pathlib.Path(sys.argv[1])
OUT_UI = ROOT / "design" / "ui" / "out"
DEST = ROOT / "design" / "figma-plugin"
DEST.mkdir(parents=True, exist_ok=True)
hot = json.loads((OUT_UI / "hotspots.json").read_text(encoding="utf-8"))

TITLES = {
    "00-landing": "Landing page (night city)", "00-sign-in": "Sign in · Local or Tourist",
    "01-home": "Customer · Choose a hub", "02-menu": "Customer · Hub menu & brands", "03-checkout-local": "Local customer · Checkout (COD)",
    "04-checkout-tourist": "Foreign tourist · Checkout (PayPal)", "05-paypal-success": "Tourist · PayPal sandbox confirmed",
    "06-tracking": "Customer · Order tracking", "07-register": "Register · Local vs Tourist", "08-kitchen": "Kitchen staff · Order board",
    "09-shipper": "Shipper · Delivery (mobile)", "10-admin-dashboard": "Admin · Dashboard (Tier 4)", "11-admin-hubs": "UC2 · Hubs & capacity",
    "12-admin-hub-edit": "UC2 · Edit / deactivate hub", "13-report-r1": "Admin · Revenue report R1", "14-report-r2": "Admin · Hub utilization R2",
}


def b64(path, width, quality):
    im = Image.open(path).convert("RGB")
    h = round(im.height * width / im.width)
    im = im.resize((width, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def tiles(path, css_w, css_h, scale, quality):
    """Split a tall screenshot into slices of at most 2800 css px so each image stays under 4096 px."""
    im = Image.open(path).convert("RGB")
    px_per_css = im.width / css_w
    out, y = [], 0
    while y < css_h:
        hh = min(2800, css_h - y)
        part = im.crop((0, round(y * px_per_css), im.width, round((y + hh) * px_per_css)))
        part = part.resize((round(css_w * scale), round(hh * scale)), Image.LANCZOS)
        buf = io.BytesIO(); part.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
        out.append({"y": y, "h": hh, "img": base64.b64encode(buf.getvalue()).decode("ascii")})
        y += hh
    return out


screens = []
for name in sorted(TITLES):
    info = hot[name]
    mobile = name == "09-shipper"
    screens.append({"id": name, "title": TITLES[name], "w": info["w"], "h": info["h"], "spots": info["spots"],
                    "tiles": tiles(OUT_UI / f"{name}.png", info["w"], info["h"], 2 if mobile else 1, 86)})
mobiles = []
for name in ("02-menu", "03-checkout-local", "06-tracking"):
    info = hot[name + "-mobile"]
    mobiles.append({"id": name + "-mobile", "title": TITLES[name] + " (390 px)", "w": info["w"], "h": info["h"], "spots": [],
                    "img": b64(OUT_UI / f"{name}-mobile.png", int(info["w"] * 1.5), 84)})
lowfi = {}
for mode, q in (("sketch", 78), ("wire", 80)):
    lowfi[mode] = []
    for p in sorted(OUT_UI.glob(f"*-{mode}.png")):
        name = p.stem[: -(len(mode) + 1)]
        im = Image.open(p)
        lowfi[mode].append({"id": f"{name}-{mode}", "title": f"{TITLES[name]} – {mode}", "w": im.width // 2, "h": im.height // 2,
                            "img": b64(p, im.width // 2, q)})

BRAND = ROOT / "design" / "brand"


def b64png(path, width):
    im = Image.open(path).convert("RGBA")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
    return {"w": im.width, "h": im.height, "img": base64.b64encode(buf.getvalue()).decode("ascii")}


brand = {"logo": b64png(BRAND / "logo-horizontal-white.png", 1200), "sheet": b64png(BRAND / "brand-sheet.png", 1600)}
data = {"screens": screens, "mobiles": mobiles, "sketch": lowfi["sketch"], "wire": lowfi["wire"], "brand": brand}
(DEST / "data.js").write_text("const DATA = " + json.dumps(data) + ";\n", encoding="utf-8")

CODE = r"""
// SaigonBite G7 – builds the Part 2 Figma file (pages, frames, prototype links, flows).
const C = { navy: {r:18/255,g:38/255,b:58/255}, chili: {r:228/255,g:87/255,b:46/255}, ink: {r:31/255,g:41/255,b:51/255},
            slate: {r:91/255,g:107/255,b:122/255}, bg: {r:245/255,g:247/255,b:250/255}, white: {r:1,g:1,b:1},
            green: {r:30/255,g:138/255,b:95/255}, amber: {r:233/255,g:162/255,b:59/255}, blue: {r:46/255,g:125/255,b:175/255}, red: {r:192/255,g:57/255,b:43/255} };

async function text(parent, str, x, y, size, style, color, width) {
  const t = figma.createText();
  t.fontName = { family: "Inter", style: style || "Regular" };
  t.characters = str; t.fontSize = size; t.fills = [{ type: "SOLID", color: color || C.ink }];
  if (width) { t.textAutoResize = "HEIGHT"; t.resize(width, t.height); }
  t.x = x; t.y = y; parent.appendChild(t); return t;
}

function imageFrame(page, s, x, y) {
  const f = figma.createFrame();
  f.name = s.title; f.resize(s.w, s.h); f.x = x; f.y = y; f.clipsContent = true;
  if (s.tiles) {            // tall screens are stored as slices stacked inside the frame
    f.fills = [{ type: "SOLID", color: C.white }];
    for (const t of s.tiles) {
      const r = figma.createRectangle(); r.name = "screen slice"; r.resize(s.w, t.h); r.x = 0; r.y = t.y;
      const img = figma.createImage(figma.base64Decode(t.img));
      r.fills = [{ type: "IMAGE", imageHash: img.hash, scaleMode: "FILL" }]; r.locked = true; f.appendChild(r);
    }
  } else {
    const img = figma.createImage(figma.base64Decode(s.img));
    f.fills = [{ type: "IMAGE", imageHash: img.hash, scaleMode: "FILL" }];
  }
  page.appendChild(f); return f;
}

async function labelFor(page, frame, caption) {
  const t = await text(page, caption, frame.x, frame.y - 52, 28, "Bold", C.navy);
  return t;
}

async function grid(page, list, cols, gapX, gapY, startY, startX, leadId) {
  let x0 = startX || 0; const made = {};
  const lead = leadId && list.find(s => s.id === leadId);
  if (lead) {               // a tall screen (the landing page) gets its own column on the left
    const f = imageFrame(page, lead, x0, (startY || 0) + 60);
    await labelFor(page, f, lead.title); made[lead.id] = f;
    x0 += lead.w + gapX * 2; list = list.filter(s => s !== lead);
  }
  let x = x0, y = startY || 0, col = 0, rowH = 0;
  for (const s of list) {
    const f = imageFrame(page, s, x, y + 60);
    await labelFor(page, f, s.title);
    made[s.id] = f; rowH = Math.max(rowH, s.h + 60);
    col++; x += s.w + gapX;
    if (col === cols) { col = 0; x = x0; y += rowH + gapY; rowH = 0; }
  }
  return made;
}

// The free Starter plan allows 3 pages per design file, so the file uses exactly 3 pages and
// shows the design stages as named sections. Re-running the plugin reuses and clears the same pages.
async function usePage(index, name) {
  let p = figma.root.children[index];
  if (!p) p = figma.createPage();
  await p.loadAsync();
  for (const n of [...p.children]) n.remove();
  p.name = name; return p;
}

async function stageSection(page, name, y, list, cols, gapX, gapY, leadId) {
  const sec = figma.createSection ? figma.createSection() : figma.createFrame();
  sec.name = name; page.appendChild(sec); sec.x = 0; sec.y = y;
  await grid(sec, list, cols, gapX, gapY, 100, 100, leadId);
  let w = 0, h = 0;
  for (const c of sec.children) { w = Math.max(w, c.x + c.width); h = Math.max(h, c.y + c.height); }
  if (sec.resizeWithoutConstraints) sec.resizeWithoutConstraints(w + 100, h + 100); else sec.resize(w + 100, h + 100);
  return sec;
}

async function setLink(node, destId) {
  const reaction = { trigger: { type: "ON_CLICK" }, actions: [{ type: "NODE", destinationId: destId, navigation: "NAVIGATE",
    transition: { type: "PUSH", direction: "LEFT", matchLayers: false, easing: { type: "EASE_IN_AND_OUT" }, duration: 0.45 }, preserveScrollPosition: false }] };
  if (node.setReactionsAsync) { await node.setReactionsAsync([reaction]); }
  else { node.reactions = [reaction]; }
}

async function main() {
  await figma.loadFontAsync({ family: "Inter", style: "Regular" });
  await figma.loadFontAsync({ family: "Inter", style: "Bold" });
  await figma.loadFontAsync({ family: "Inter", style: "Semi Bold" });
  try { figma.root.name = "SaigonBite – Team G7 – Part 2 UI/UX"; } catch (e) { /* the file name is set by the user */ }

  // ---------- Page 1: 00 Cover + design system
  const cover = await usePage(0, "00 · Cover & design system");
  await figma.setCurrentPageAsync(cover);
  const cf = figma.createFrame(); cf.name = "Cover"; cf.resize(1600, 900); cf.fills = [{ type: "SOLID", color: C.navy }]; cover.appendChild(cf);
  const lg = figma.createRectangle(); lg.name = "SaigonBite logo"; lg.resize(DATA.brand.logo.w / 1.6, DATA.brand.logo.h / 1.6); lg.x = 80; lg.y = 70;
  lg.fills = [{ type: "IMAGE", imageHash: figma.createImage(figma.base64Decode(DATA.brand.logo.img)).hash, scaleMode: "FIT" }]; cf.appendChild(lg);
  await text(cf, "Cloud-kitchen food delivery hub – UI/UX prototype (Part 2)", 100, 250, 34, "Semi Bold", { r: .85, g: .9, b: .94 });
  await text(cf, "Team G7 · Lê Xuân Khánh (524H0055) – UC1 Place and Manage Orders · Ngô Bình Minh (524H0169) – UC2 Manage Hubs & Capacity", 100, 320, 22, "Regular", { r: .8, g: .86, b: .9 }, 1400);
  await text(cf, "Pages: 00 Cover & design system · 01–04 Design stages (sections: Sketch → Wireframe → Mock-up desktop → Mock-up mobile) · 05 Prototype", 100, 420, 22, "Regular", C.white, 1400);
  await text(cf, "Prototype flows (Present ▶ on page 05): ① Local customer orders with cash  ② Foreign tourist pays with PayPal sandbox  ③ Admin: dashboard, hubs (UC2), reports R1 & R2", 100, 470, 22, "Regular", C.white, 1400);
  await text(cf, "Bootstrap 5 responsive grid · English / Vietnamese · ASP.NET Core MVC (Tier 4)", 100, 800, 20, "Semi Bold", { r: .95, g: .55, b: .4 });

  // design system (brand sheet) under the cover
  await text(cover, "Design system – SaigonBite brand essentials (logo, colours, type)", 0, 1040, 32, "Bold", C.navy);
  const df = figma.createFrame(); df.name = "Design system – brand essentials"; df.resize(DATA.brand.sheet.w, DATA.brand.sheet.h);
  df.fills = [{ type: "IMAGE", imageHash: figma.createImage(figma.base64Decode(DATA.brand.sheet.img)).hash, scaleMode: "FILL" }];
  df.x = 0; df.y = 1110; cover.appendChild(df);

  // ---------- Page 2: 01–04 design stages, one section per stage, stacked top to bottom
  const pStages = await usePage(1, "01–04 · Sketch → Wireframe → Mock-up");
  await figma.setCurrentPageAsync(pStages);
  let y = 0;
  const stages = [
    ["01 · Sketch (stage 1)", DATA.sketch, 3, 140, 160],
    ["02 · Wireframe (stage 2)", DATA.wire, 3, 140, 160],
    ["03 · Mock-up desktop (stage 3)", DATA.screens.filter(s => s.id !== "09-shipper"), 3, 160, 180, "00-landing"],
    ["04 · Mock-up mobile 390 px (stage 3)", DATA.mobiles.concat(DATA.screens.filter(s => s.id === "09-shipper")), 4, 120, 160],
  ];
  for (const [name, list, cols, gx, gy, lead] of stages) {
    const sec = await stageSection(pStages, name, y, list, cols, gx, gy, lead);
    y += sec.height + 400;
  }

  // ---------- Page 3: 05 Prototype (stage 4) – frames with hot-spots
  const pP = await usePage(2, "05 · Prototype (stage 4)");
  await figma.setCurrentPageAsync(pP);
  const frames = await grid(pP, DATA.screens, 3, 200, 220, 0, 0, "00-landing");
  let links = 0;
  for (const s of DATA.screens) {
    const f = frames[s.id];
    for (const sp of s.spots) {
      if (!frames[sp.target] || sp.target === s.id) continue;
      const r = figma.createRectangle();
      r.name = "hotspot → " + sp.target; r.x = sp.x; r.y = sp.y; r.resize(Math.max(sp.w, 8), Math.max(sp.h, 8));
      r.fills = [{ type: "SOLID", color: C.chili, opacity: 0 }];
      f.appendChild(r);
      await setLink(r, frames[sp.target].id); links++;
    }
  }
  pP.flowStartingPoints = [
    { nodeId: frames["00-landing"].id, name: "1 · Local customer – landing → sign in → order, pay cash (UC1)" },
    { nodeId: frames["04-checkout-tourist"].id, name: "2 · Foreign tourist – PayPal sandbox (Tier 4)" },
    { nodeId: frames["10-admin-dashboard"].id, name: "3 · Admin – dashboard, hubs (UC2), reports R1 & R2" },
  ];

  figma.viewport.scrollAndZoomIntoView(Object.values(frames));
  figma.closePlugin(`SaigonBite file built: ${DATA.screens.length} prototype screens, ${links} links, 3 flows.`);
}

main().catch(e => figma.closePlugin("Error: " + e.message));
"""
(DEST / "code.js").write_text((DEST / "data.js").read_text(encoding="utf-8") + CODE, encoding="utf-8")
(DEST / "data.js").unlink()
manifest = {"name": "SaigonBite G7 – Part 2 file builder", "id": "saigonbite-g7-part2-builder", "api": "1.0.0", "main": "code.js",
            "editorType": ["figma"], "documentAccess": "dynamic-page", "networkAccess": {"allowedDomains": ["none"]}}
(DEST / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
size = (DEST / "code.js").stat().st_size
print(f"code.js {size / 1e6:.1f} MB · screens {len(screens)} · mobiles {len(mobiles)} · sketch {len(lowfi['sketch'])} · wire {len(lowfi['wire'])}")
print("links", sum(len([s for s in sc['spots'] if s['target'] in TITLES and s['target'] != sc['id']]) for sc in screens))
