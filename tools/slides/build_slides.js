// Team G7 – SaigonBite – Presentation 2 (Design Review, 7–10 minutes). Usage: node build_slides.js <out.pptx> [figmaUrl]
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.SKILL_DIR + "/scripts/apply_theme.js");
const NOTES = require("./notes.js");

const OUT = process.argv[2] || "deck.pptx";
const FIGMA = process.argv[3] || "Figma link in readme.txt";
const R = (...p) => path.resolve(__dirname, "../..", ...p);
const BRAND = (f) => R("design/brand", f);
const UML = (f) => R("design/uml/out", f), ARC = (f) => R("design/architecture", f), UI = (f) => R("design/ui/out", f), IMG = (f) => R("design/ui/assets/img", f);

const THEME = {
  name: "SaigonBite G7", headFontFace: "Segoe UI", bodyFontFace: "Segoe UI",
  colors: { dk1: "1F2933", lt1: "FFFFFF", dk2: "12263A", lt2: "F1F4F7", accent1: "E4572E", accent2: "1E8A5F", accent3: "E9A23B",
            accent4: "C0392B", accent5: "5B6B7A", accent6: "2E7DAF", hlink: "2E7DAF", folHlink: "5B6B7A" },
};

// image size readers (PNG and JPEG) so pictures keep their aspect ratio
function dims(file) {
  const b = fs.readFileSync(file);
  if (b[0] === 0x89) return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
  let i = 2;
  while (i < b.length) {
    const marker = b[i + 1], len = b.readUInt16BE(i + 2);
    if (marker >= 0xc0 && marker <= 0xc3) return { h: b.readUInt16BE(i + 5), w: b.readUInt16BE(i + 7) };
    i += 2 + len;
  }
  throw new Error("size? " + file);
}

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "Team G7 (524H0055, 524H0169)";
pres.title = "SaigonBite – Design Review (Part 2)";
const C = pres.SchemeColor;

pres.defineSlideMaster({
  title: "SB_DARK", background: { color: C.text2 },
  objects: [],
});
pres.defineSlideMaster({
  title: "SB_CONTENT", background: { color: C.background1 },
  margin: [0.4, 0.5, 0.45, 0.5],
  objects: [
    { rect: { x: 0, y: 7.12, w: 13.333, h: 0.38, fill: { color: C.background2 } } },
    { image: { x: 0.5, y: 7.17, w: 0.27, h: 0.27, path: R("design/brand/mark-512.png") } },
    { text: { text: "SaigonBite · Team G7 · Part 2 Design Review", options: { x: 0.85, y: 7.15, w: 7, h: 0.3, fontSize: 10, color: C.accent5, isTextBox: true } } },
    { image: { x: 0.45, y: 0.24, w: 1.12, h: 0.62, path: R("design/brand/tdtu-logo.png") } },
    { placeholder: { options: { name: "kicker", type: "body", x: 1.78, y: 0.28, w: 8.9, h: 0.32, fontSize: 11.5, bold: true, color: C.accent1, charSpacing: 1.5 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 1.78, y: 0.56, w: 8.95, h: 0.72, fontSize: 27, bold: true, color: C.text2, align: "left", valign: "top" }, text: "" } },
  ],
  slideNumber: { x: 12.4, y: 7.15, w: 0.5, h: 0.3, fontSize: 10, color: C.accent5, align: "right" },
});

let n = 0;
function content(sect, kicker, title, who) {
  const s = pres.addSlide({ masterName: "SB_CONTENT", sectionTitle: sect });
  s.addText(kicker, { placeholder: "kicker" });
  s.addText(title, { placeholder: "title" });
  if (who) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 10.85, y: 0.36, w: 2.0, h: 0.42, rectRadius: 0.21, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: "presenter chip" });
    s.addText([{ text: "Presenter  ", options: { color: C.accent5, fontSize: 10 } }, { text: who, options: { bold: true, color: C.text2, fontSize: 12 } }],
      { x: 10.85, y: 0.36, w: 2.0, h: 0.42, align: "center", valign: "middle", margin: 0, isTextBox: true });
  }
  s.addNotes(NOTES[n++]);
  return s;
}
function pic(s, file, x, y, maxW, maxH, opts = {}) {
  const d = dims(file); const r = d.w / d.h;
  let w = maxW, h = w / r;
  if (h > maxH) { h = maxH; w = h * r; }
  const ox = opts.align === "left" ? 0 : (maxW - w) / 2;
  s.addImage({ path: file, x: x + ox, y, w, h, altText: opts.alt || path.basename(file), objectName: opts.name || path.basename(file) });
  if (opts.frame) s.addShape(pres.shapes.RECTANGLE, { x: x + ox, y, w, h, fill: { type: "none" }, line: { color: "C8D1DA", width: 1 } });
  return { x: x + ox, y, w, h };
}
function card(s, x, y, w, h, head, body, color, opts = {}) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: opts.fill || C.background1 }, line: { color: opts.line || "D9E0E6", width: 1 } });
  s.addShape(pres.shapes.RECTANGLE, { x, y: y + 0.12, w: 0.07, h: h - 0.24, fill: { color: color || C.accent1 }, line: { color: color || C.accent1 } });
  s.addText(head, { x: x + 0.2, y: y + 0.08, w: w - 0.3, h: 0.36, fontSize: opts.hs || 14.5, bold: true, color: C.text2, valign: "top", margin: 0, isTextBox: true });
  s.addText(body, { x: x + 0.2, y: y + 0.44, w: w - 0.3, h: h - 0.5, fontSize: opts.bs || 12.5, color: C.text1, valign: "top", margin: 0, paraSpaceAfter: 3, isTextBox: true });
}
function chip(s, x, y, w, text, fill, color) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.38, rectRadius: 0.19, fill: { color: fill }, line: { color: fill } });
  s.addText(text, { x, y, w, h: 0.38, fontSize: 11.5, bold: true, color, align: "center", valign: "middle", margin: 0, isTextBox: true });
}

// ---------------------------------------------------------------- 1 title
pres.addSection({ title: "Opening" });
{
  const s = pres.addSlide({ masterName: "SB_DARK", sectionTitle: "Opening" });
  s.addImage({ path: IMG("ctx-night-skyline-river.jpg"), x: 0, y: 0, w: 13.333, h: 7.5, sizing: { type: "cover", w: 13.333, h: 7.5 }, altText: "Ho Chi Minh City skyline at night over the Saigon River" });
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 13.333, h: 7.5, fill: { color: C.text2, transparency: 22 }, line: { color: C.text2, transparency: 100 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 7.6, h: 7.5, fill: { color: C.text2, transparency: 8 }, line: { color: C.text2, transparency: 100 } });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.62, y: 0.45, w: 1.5, h: 0.9, rectRadius: 0.08, fill: { color: "FFFFFF" }, line: { color: "FFFFFF" } });
  s.addImage({ path: BRAND("tdtu-logo.png"), x: 0.72, y: 0.52, w: 1.3, h: 0.72, altText: "Ton Duc Thang University logo" });
  s.addImage({ path: BRAND("logo-horizontal-white.png"), x: 2.35, y: 0.42, w: 3.3, h: 0.96, altText: "SaigonBite logo" });
  s.addText("SOFTWARE ENGINEERING · SEM01_2627 · PART 2 DESIGN REVIEW", { x: 0.7, y: 1.55, w: 7, h: 0.35, fontSize: 12, bold: true, color: C.accent1, charSpacing: 1.5, isTextBox: true });
  s.addText("Design Review", { x: 0.7, y: 1.95, w: 7, h: 1.0, fontSize: 52, bold: true, color: C.background1, isTextBox: true });
  s.addText("How we will build a load-aware cloud-kitchen platform", { x: 0.7, y: 2.95, w: 6.6, h: 0.9, fontSize: 21, color: "D5DEE7", isTextBox: true });
  chip(s, 0.7, 3.95, 3.3, "Tier 4 · approved at Presentation 1", C.accent1, C.background1);
  chip(s, 4.1, 3.95, 3.1, "ASP.NET Core MVC · EF Core · SQL", "24384C", "D5DEE7");
  const ppl = [["Lê Xuân Khánh", "524H0055", "UC1 · Place and Manage Orders"], ["Ngô Bình Minh", "524H0169", "UC2 · Manage Hubs & Capacity"]];
  ppl.forEach((p, i) => {
    const y = 4.72 + i * 0.98;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y, w: 6.4, h: 0.88, rectRadius: 0.1, fill: { color: "FFFFFF", transparency: 90 }, line: { color: "FFFFFF", transparency: 75 } });
    s.addText([{ text: p[0] + "  ", options: { bold: true, color: C.background1, fontSize: 17 } }, { text: p[1], options: { color: "B8C6D3", fontSize: 13 } }],
      { x: 0.95, y: y + 0.08, w: 6, h: 0.4, margin: 0, isTextBox: true });
    s.addText(p[2], { x: 0.95, y: y + 0.46, w: 6, h: 0.32, fontSize: 13.5, color: "F5B9A5", margin: 0, isTextBox: true });
  });
  s.addText("Instructor: Phạm Thái Kỳ Trung", { x: 0.7, y: 6.78, w: 6, h: 0.35, fontSize: 12, color: "B8C6D3", isTextBox: true });
  s.addNotes(NOTES[n++]);
}

// ---------------------------------------------------------------- 2 changes since Part 1
pres.addSection({ title: "Changes" });
{
  const s = content("Changes", "FEEDBACK APPLIED", "Since Part 1: Tier 4, with three owned extensions", "Khánh");
  const parts = [
    ["(a) Live PayPal sandbox", "FR36 · one new Strategy class, Orders v2 create → approve → capture", "Owner: Khánh", C.accent6],
    ["(b) Interactive Admin dashboard", "FR37 · KPIs, live hub load, filters, heavy-rain switch", "Owner: Minh", C.accent2],
    ["(c) Playwright end-to-end tests", "NFR7 · Local, Tourist, kitchen, shipper, reports, invalid move", "Owners: both", C.accent3],
  ];
  parts.forEach((p, i) => {
    const y = 1.6 + i * 1.6;
    card(s, 0.5, y, 7.2, 1.38, p[0], p[1], p[3], { hs: 17, bs: 14 });
    chip(s, 5.75, y + 0.12, 1.75, p[2], "F1F4F7", "12263A");
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.2, y: 1.6, w: 4.65, h: 4.58, rectRadius: 0.1, fill: { color: C.text2 }, line: { color: C.text2 } });
  s.addText("Today’s walkthrough", { x: 8.5, y: 1.78, w: 4.2, h: 0.45, fontSize: 18, bold: true, color: C.background1, isTextBox: true });
  const ag = ["Use cases and specifications", "Sequences and the order state machine", "CRC cards → class diagrams", "Strategy pattern for payments", "Database logic", "Architecture and where prices live", "UI/UX stages and live Figma demo"];
  s.addText(ag.map((t, i) => ({ text: `${i + 1}   ${t}`, options: { breakLine: i < ag.length - 1 } })),
    { x: 8.5, y: 2.3, w: 4.2, h: 3.7, fontSize: 14.5, color: "D5DEE7", paraSpaceAfter: 9, valign: "top", isTextBox: true });
  s.addText("Report v2.0 · Feedback Log, Section 1.1, FR36, FR37, NFR7 and the Team Workbook are updated.", { x: 0.5, y: 6.5, w: 12.3, h: 0.4, fontSize: 12.5, color: C.accent5, isTextBox: true });
}

// ---------------------------------------------------------------- 3 use cases
pres.addSection({ title: "Use cases" });
{
  const s = content("Use cases", "2.1 OVERALL USE CASE DIAGRAM", "Use cases: one Customer, two ways in", "Minh");
  pic(s, UML("usecase_overview.png"), 0.4, 1.45, 8.6, 5.55, { frame: false });
  card(s, 9.25, 1.55, 3.6, 1.6, "Actor generalisation", "Local Customer and Foreign Tourist inherit UC1 from Customer; only sign-up and payment options differ (BR18).", C.accent6);
  card(s, 9.25, 3.3, 3.6, 1.6, "Ownership, full CRUD", "UC1 Place and Manage Orders – Khánh.\nUC2 Manage Hubs & Capacity – Minh.", C.accent1);
  card(s, 9.25, 5.05, 3.6, 1.6, "«include» and «extend»", "Pricing and payment selection always run; PayPal sandbox extends only when a tourist picks it.", C.accent3);
}

// ---------------------------------------------------------------- 4 UC1 request pipeline
pres.addSection({ title: "UC1" });
{
  const s = content("UC1", "2.2.1 UC1 PLACE AND MANAGE ORDERS · AUTHOR 524H0055", "Placing an order: one request, one transaction", "Khánh");
  pic(s, ARC("request_pipeline.png"), 0.45, 1.45, 12.45, 4.45);
  const alts = [["A1 Hub ≥ 90%", "choose an active hub below 90% within 8 km (A-04)"], ["A3 Edit while Placed", "re-price from the snapshot, re-check BR1, BR12, BR14"], ["E3 Payment fails", "ROLLBACK – no partial order (NFR5)"]];
  alts.forEach((a, i) => card(s, 0.5 + i * 4.18, 5.95, 3.98, 1.05, a[0], a[1], [C.accent4, C.accent6, C.accent1][i], { hs: 14, bs: 12.5 }));
}
{
  const s = content("UC1", "2.3.1 UC1 SEQUENCE (2/2)", "Payment strategy and the transaction boundary", "Khánh");
  pic(s, UML("seq_uc1_place_order_2.png"), 0.4, 1.4, 8.7, 5.65, { frame: true });
  card(s, 9.35, 1.5, 3.5, 1.65, "Resolver decides", "Methods of the other group and COD above 1,000,000 are rejected before anything is saved (BR13, BR14).", C.accent6);
  card(s, 9.35, 3.3, 3.5, 1.65, "One transaction", "Order, lines, snapshot, payment and the first history row commit together (NFR5, NFR6).", C.accent2);
  card(s, 9.35, 5.1, 3.5, 1.65, "Tier 4 hook", "PayPal returns ApprovalRequired; capture happens on return – no other class changes.", C.accent3);
}

// ---------------------------------------------------------------- 6 UC2
pres.addSection({ title: "UC2" });
{
  const s = content("UC2", "2.2.2 UC2 MANAGE HUBS & CAPACITY · AUTHOR 524H0169", "Hubs: full CRUD around one number – the load", "Minh");
  const crud = [["C  Create", "Capacity must be a positive whole number; at least one active brand (FR5, FR28).", C.accent2],
                ["R  Read", "Load = (Confirmed + Preparing) ÷ capacity, unrounded (A-06): Quiet < 30% · Normal · Full ≥ 90%.", C.accent6],
                ["U  Update", "New capacity or brands are used at once by the discount and protection rules (BR7, BR8).", C.accent3],
                ["D  Deactivate", "Soft-delete; refused while orders are active (A-07); history and R2 stay correct.", C.accent4]];
  crud.forEach((c, i) => card(s, 0.5, 1.5 + i * 1.38, 5.9, 1.25, c[0], c[1], c[2], { hs: 15, bs: 13 }));
  pic(s, UML("seq_uc2_manage_hubs_2.png"), 6.7, 1.4, 6.2, 5.65, { frame: true });
}

// ---------------------------------------------------------------- 7 state machine
pres.addSection({ title: "Behaviour" });
{
  const s = content("Behaviour", "2.3.3 ORDER STATE DIAGRAM (TEAM)", "Eight states; only the right role moves an order", "Khánh");
  pic(s, UML("state_order.png"), 0.4, 1.35, 5.2, 5.7);
  const pts = [["Transition table in the business layer", "OrderStateMachine holds (from, to, role, guard). The UI only hides buttons; the server decides (BR15).", C.accent1],
               ["Every move is audited", "Each accepted transition writes OrderStatusHistory with actor and Vietnam time; rows are never edited (NFR6).", C.accent2],
               ["Guards from the specification", "Kitchen of the order’s hub only · COD needs cash confirmed (BR14) · shipper assigned by Admin (A-01).", C.accent6],
               ["Tested, not assumed", "15 invalid-transition tests S-01…S-15 are already in the Team Workbook.", C.accent3]];
  pts.forEach((p, i) => card(s, 6.0, 1.5 + i * 1.38, 6.85, 1.25, p[0], p[1], p[2], { hs: 15, bs: 13 }));
}

// ---------------------------------------------------------------- 8 CRC → class
pres.addSection({ title: "Structure" });
{
  const s = content("Structure", "2.4.1 CRC CARDS → 2.4.2 CLASS DIAGRAMS", "CRC cards first: who does what, and with whom", "Minh");
  const crc = [["OrderService", "Coordinates place, edit, cancel; one transaction", "PricingService · HubLoadService · StateMachine · Resolver"],
               ["PricingService", "BR1–BR12 in the BR10 order; rounds once", "IClock · Voucher"],
               ["HubLoadService", "Counts Confirmed + Preparing; finds hubs < 90%", "DbContext · Hub"],
               ["OrderStateMachine", "Allowed transitions; writes history", "Order · OrderStatusHistory"],
               ["PaymentStrategyResolver", "Methods per customer type; picks a strategy", "IPaymentStrategy × 5"],
               ["HubService (UC2)", "Hub CRUD; blocks deactivation with active orders", "DbContext · HubLoadService"]];
  crc.forEach((c, i) => {
    const x = 0.5 + (i % 2) * 3.55, y = 1.5 + Math.floor(i / 2) * 1.83;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 3.4, h: 1.68, rectRadius: 0.06, fill: { color: "FFFDF7" }, line: { color: "E9C98A", width: 1.2 } });
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 3.4, h: 0.42, fill: { color: C.text2 }, line: { color: C.text2 } });
    s.addText(c[0], { x: x + 0.12, y, w: 3.2, h: 0.42, fontSize: 13.5, bold: true, color: C.background1, valign: "middle", margin: 0, isTextBox: true });
    s.addText(c[1], { x: x + 0.12, y: y + 0.48, w: 3.2, h: 0.62, fontSize: 12, color: C.text1, valign: "top", margin: 0, isTextBox: true });
    s.addText("↔ " + c[2], { x: x + 0.12, y: y + 1.1, w: 3.2, h: 0.5, fontSize: 10.5, color: C.accent5, italic: true, valign: "top", margin: 0, isTextBox: true });
  });
  pic(s, UML("class_users.png"), 7.75, 1.45, 5.1, 2.15, { frame: true });
  pic(s, UML("class_orders.png"), 7.75, 3.8, 5.1, 3.2, { frame: true });
}
{
  const s = content("Structure", "2.4.2 STRATEGY PATTERN (BR13, NFR2)", "Five payment methods behind one interface", "Khánh");
  pic(s, UML("class_strategy.png"), 0.4, 1.4, 7.9, 5.65, { frame: true });
  s.addText("Adding a method = 1 class + 1 line", { x: 8.6, y: 1.5, w: 4.3, h: 0.45, fontSize: 18, bold: true, color: C.text2, isTextBox: true });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.6, y: 2.05, w: 4.3, h: 2.55, rectRadius: 0.06, fill: { color: "0F1E2D" }, line: { color: "0F1E2D" } });
  const code = ["// Program.cs – registrations only", "AddScoped<IPaymentStrategy, MoMoStrategy>();", "AddScoped<IPaymentStrategy, VnPayStrategy>();", "AddScoped<IPaymentStrategy, CashOnDeliveryStrategy>();", "AddScoped<IPaymentStrategy, ApplePayStrategy>();", "AddScoped<IPaymentStrategy, PayPalSandboxStrategy>();"];
  s.addText(code.map((t, i) => ({ text: t, options: { breakLine: i < code.length - 1, color: i === 0 ? "7F93A8" : (i === 5 ? "F5B9A5" : "D5DEE7") } })),
    { x: 8.75, y: 2.15, w: 4.1, h: 2.35, fontFace: "Consolas", fontSize: 10.5, valign: "top", margin: 0, paraSpaceAfter: 4, isTextBox: true });
  card(s, 8.6, 4.8, 4.3, 1.05, "Ready for the Week 5 Change Request", "A new payment method edits no existing payment class.", C.accent2, { hs: 13.5, bs: 12.5 });
  card(s, 8.6, 6.0, 4.3, 0.98, "Rule enforced in one place", "Resolver refuses the other group’s methods (BR13).", C.accent6, { hs: 13.5, bs: 12.5 });
}

// ---------------------------------------------------------------- 10 database
pres.addSection({ title: "Database" });
{
  const s = content("Database", "2.4.3 DATABASE LOGIC (EF CORE CODE FIRST)", "A schema that keeps every price reproducible", "Minh");
  pic(s, UML("erd_orders_payments.png"), 0.4, 1.4, 8.2, 5.65, { frame: true });
  const d = [["One schema, two customers", "Users + LocalCustomerProfiles + TouristProfiles (table-per-type, BR18).", C.accent6],
             ["Snapshot on the order", "Placement time, hub load, rain flag and S…R2, Total are stored (BR17).", C.accent1],
             ["Soft-delete", "Hubs, brands, items, users, vouchers are deactivated, never deleted (FR24).", C.accent3],
             ["Audit and concurrency", "Append-only status history; RowVersion stops double moves (NFR5, NFR6).", C.accent2]];
  d.forEach((x, i) => card(s, 8.85, 1.5 + i * 1.38, 4.0, 1.25, x[0], x[1], x[2], { hs: 14, bs: 12.5 }));
}

// ---------------------------------------------------------------- 11 architecture, 12 pricing
pres.addSection({ title: "Architecture" });
{
  const s = content("Architecture", "2.5 ARCHITECTURE & QUALITY DESIGN", "Three layers: thin controllers, rules in services", "Khánh");
  pic(s, ARC("architecture_layers.png"), 0.4, 1.38, 12.5, 5.68);
}
{
  const s = content("Architecture", "2.5 WHERE THE PRICING RULES LIVE", "All price rules in one service, in BR10 order", "Khánh");
  pic(s, ARC("pricing_pipeline.png"), 0.4, 1.45, 12.5, 4.7);
  const p = [["Testable", "each threshold is one private method → EP/BVA unit tests", C.accent2], ["Reproducible", "edits re-price from the stored snapshot (BR17)", C.accent6], ["Local change", "a new rule changes PricingService only (SOLID: S, O)", C.accent1]];
  p.forEach((x, i) => card(s, 0.5 + i * 4.18, 6.2, 3.98, 0.82, x[0], x[1], x[2], { hs: 13.5, bs: 12 }));
}

// ---------------------------------------------------------------- 13 Tier 4
pres.addSection({ title: "Tier 4" });
{
  const s = content("Tier 4", "TIER 4 · DESIGNED END TO END, OWNERS AND ACCEPTANCE", "Tier 4: three extras, each with a design and a test", "Khánh · Minh");
  const cols = [
    { h: "(a) Live PayPal sandbox", id: "FR36 · owner Khánh", img: UML("seq_tier4_paypal_sandbox.png"), color: C.accent6,
      pts: ["Orders v2: OAuth → create → buyer approves → capture; refund on cancel", "Only PayPalSandboxStrategy calls PayPal (keys in user secrets)", "Accept: capture ID stored; refund appears in the sandbox"] },
    { h: "(b) Interactive Admin dashboard", id: "FR37 · owner Minh", img: UI("10-admin-dashboard.png"), color: C.accent2,
      pts: ["KPIs, live hub load, orders by state, payment mix", "Date and hub filters; heavy-rain switch (BR5)", "Accept: numbers equal R1 and R2 for the same filter"] },
    { h: "(c) Playwright end-to-end tests", id: "NFR7 · owners both", img: null, color: C.accent3,
      pts: ["E2E-01 Local order, COD 205,000 ₫", "E2E-02 Tourist pays in PayPal sandbox, 269,000 ₫", "E2E-03 Kitchen confirm → ready · E2E-04 shipper COD → Delivered", "E2E-05 Delivered → Preparing is rejected (BR15)", "E2E-06/07 R1, R2 and dashboard totals", "Accept: 100% pass headless; HTML report + traces"] },
  ];
  cols.forEach((c, i) => {
    const x = 0.5 + i * 4.18, w = 3.98;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.45, w, h: 5.55, rectRadius: 0.08, fill: { color: C.background1 }, line: { color: "D9E0E6", width: 1 } });
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.45, w, h: 0.09, fill: { color: c.color }, line: { color: c.color } });
    s.addText(c.h, { x: x + 0.2, y: 1.62, w: w - 0.4, h: 0.4, fontSize: 16, bold: true, color: C.text2, margin: 0, isTextBox: true });
    s.addText(c.id, { x: x + 0.2, y: 2.0, w: w - 0.4, h: 0.3, fontSize: 11.5, bold: true, color: C.accent1, margin: 0, isTextBox: true });
    let y = 2.42;
    if (c.img) { const r = pic(s, c.img, x + 0.2, y, w - 0.4, 2.15, { frame: true }); y = r.y + r.h + 0.18; }
    s.addText(c.pts.map((t, k) => ({ text: t, options: { bullet: { indent: 12 }, breakLine: k < c.pts.length - 1 } })),
      { x: x + 0.2, y, w: w - 0.4, h: 6.85 - y, fontSize: 12, color: C.text1, valign: "top", paraSpaceAfter: 5, margin: 0, isTextBox: true });
  });
}

// ---------------------------------------------------------------- 14 UI stages, 15 landing, 16 customer, 17 operations, 18 mobile
pres.addSection({ title: "UI/UX" });
{
  const s = content("UI/UX", "2.6 UI/UX DESIGN · FOUR STAGES", "From sketch to a clickable Figma prototype", "Minh");
  pic(s, UI("ui_stages.png"), 0.4, 1.4, 7.8, 5.65, { frame: false });
  card(s, 8.45, 1.5, 4.4, 1.55, "Figma file", "00 Cover · 01 Sketch · 02 Wireframe · 03 Mock-up desktop · 04 Mobile · 05 Prototype (3 flows) · 06 Brand & design system", C.accent1, { bs: 12.5 });
  card(s, 8.45, 3.2, 4.4, 1.35, "Bootstrap 5 grid", "Customer flow at 390 px and 1440 px; EN/VI toggle (NFR3).", C.accent6, { bs: 12.5 });
  card(s, 8.45, 4.7, 4.4, 1.35, "Real data, real rules", "Checkout totals follow BR10: 205,000 ₫ (Local) and 269,000 ₫ (Tourist).", C.accent2, { bs: 12.5 });
  s.addText([{ text: "Live demo: ", options: { bold: true, color: C.accent1 } }, { text: FIGMA, options: { color: C.text2 } }],
    { x: 8.45, y: 6.25, w: 4.4, h: 0.7, fontSize: 12, valign: "top", isTextBox: true });
}
{
  const s = content("UI/UX", "LANDING PAGE · FIRST IMPRESSION", "Landing page: Saigon by night", "Minh");
  pic(s, UI("landing_hero.png"), 0.45, 1.42, 8.75, 5.55, { frame: true, align: "left" });
  pic(s, UI("00-landing.png"), 9.42, 1.42, 1.3, 5.55, { frame: true, align: "left" });
  const fx = ["Real night photos (Wikimedia Commons, CC)", "Slow Ken Burns zoom + soft lantern glow", "Counting stats, scroll-reveal sections", "Dish carousel, animated hub-load bars", "205,000 ₫ example counts up line by line", "19 s screen recording in _extras"];
  s.addText("Motion", { x: 10.95, y: 1.45, w: 2.0, h: 0.35, fontSize: 14, bold: true, color: C.text2, margin: 0, isTextBox: true });
  s.addText(fx.map((t, k) => ({ text: t, options: { bullet: { indent: 10 }, breakLine: k < fx.length - 1 } })),
    { x: 10.95, y: 1.85, w: 1.95, h: 5.1, fontSize: 11.5, color: C.text1, valign: "top", paraSpaceAfter: 6, margin: 0, isTextBox: true });
}
function gallery(sect, kicker, title, who, shots) {
  const s = content(sect, kicker, title, who);
  shots.forEach((sh, i) => {
    const x = 0.5 + (i % 2) * 6.22, y = 1.42 + Math.floor(i / 2) * 2.86;
    const r = pic(s, UI(sh[0]), x, y, 3.9, 2.62, { frame: true, align: "left" });
    s.addText(sh[1], { x: x + r.w + 0.15, y: y + 0.05, w: 6.0 - r.w - 0.2, h: 0.4, fontSize: 13.5, bold: true, color: C.text2, margin: 0, isTextBox: true });
    s.addText(sh[2], { x: x + r.w + 0.15, y: y + 0.45, w: 6.0 - r.w - 0.2, h: 2.1, fontSize: 11.5, color: C.text1, valign: "top", margin: 0, isTextBox: true });
  });
  return s;
}
gallery("UI/UX", "PROTOTYPE · CUSTOMER JOURNEY (UC1)", "Customer journey: from hub choice to tracking", "Minh", [
  ["01-home.png", "Choose a hub", "Load bands on every hub: Quiet −10%, Normal, Full ≥ 90% (refused), outside 8 km (BR2, BR7, BR8)."],
  ["02-menu.png", "Menu and brands", "Three brands of one hub, real dishes, sold-out item disabled (BR12), cart with S = 200,000 ₫."],
  ["03-checkout-local.png", "Checkout – Local", "Every BR10 line with its rule, total 205,000 ₫; MoMo, VNPay, COD only (BR13, BR14)."],
  ["06-tracking.png", "Tracking", "Status history, price snapshot (BR17) and the cancel rule (BR16)."],
]);
gallery("UI/UX", "PROTOTYPE · TIER 4, UC2 AND REPORTS", "Operations: dashboard, hubs and reports", "Minh", [
  ["10-admin-dashboard.png", "Admin dashboard · Tier 4", "KPIs, revenue trend, live hub load, orders by state, payment mix, heavy-rain switch (FR37)."],
  ["11-admin-hubs.png", "UC2 · Hubs & capacity", "Capacity, active orders, unrounded load and band; inactive hub kept for history (A-07)."],
  ["13-report-r1.png", "Report R1 · Revenue", "By brand category and payment method; Cancelled and Failed excluded (FR25)."],
  ["04-checkout-tourist.png", "Tourist checkout · PayPal", "Voucher, free delivery, rain surcharge, total 269,000 ₫; Apple Pay, PayPal, COD (FR36)."],
]);
{
  const s = content("UI/UX", "RESPONSIVE · 390 PX MOBILE (NFR3)", "The same screens on a phone", "Minh");
  pic(s, UI("ui_phones.png"), 0.45, 1.38, 12.45, 5.3);
  chip(s, 0.5, 6.62, 7.2, "Bootstrap grid collapses to one column · no horizontal scroll · touch targets ≥ 44 px", "F1F4F7", "12263A");
  chip(s, 7.9, 6.62, 4.95, "Live demo in Figma: page 05 · Prototype ▶", C.accent1, C.background1);
}

// ---------------------------------------------------------------- 15 closing
pres.addSection({ title: "Close" });
{
  const s = pres.addSlide({ masterName: "SB_DARK", sectionTitle: "Close" });
  s.addImage({ path: IMG("ctx-night-ben-thanh.jpg"), x: 6.4, y: 0, w: 6.933, h: 7.5, sizing: { type: "cover", w: 6.933, h: 7.5 }, altText: "Ben Thanh Market lit up at night" });
  s.addShape(pres.shapes.RECTANGLE, { x: 6.4, y: 0, w: 6.933, h: 7.5, fill: { color: C.text2, transparency: 70 }, line: { color: C.text2, transparency: 100 } });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.62, y: 0.42, w: 1.3, h: 0.78, rectRadius: 0.07, fill: { color: "FFFFFF" }, line: { color: "FFFFFF" } });
  s.addImage({ path: BRAND("tdtu-logo.png"), x: 0.71, y: 0.48, w: 1.12, h: 0.62, altText: "Ton Duc Thang University logo" });
  s.addImage({ path: BRAND("logo-horizontal-white.png"), x: 2.12, y: 0.41, w: 2.75, h: 0.8, altText: "SaigonBite logo" });
  s.addText("NEXT · PART 3", { x: 0.7, y: 1.4, w: 5.5, h: 0.35, fontSize: 12, bold: true, color: C.accent1, charSpacing: 1.5, isTextBox: true });
  s.addText("Build exactly what we designed", { x: 0.7, y: 1.75, w: 5.6, h: 1.1, fontSize: 32, bold: true, color: C.background1, isTextBox: true });
  const steps = [["Week 5", "Running skeleton: schema + UC1 end to end; absorb the Change Request"], ["Week 6", "UC1 and UC2 complete; PricingService EP/BVA tests; PayPal sandbox; dashboard"], ["Week 7", "Playwright suite, RTM, final report, video and live demo"]];
  steps.forEach((st, i) => {
    const y = 3.0 + i * 1.12;
    s.addShape(pres.shapes.OVAL, { x: 0.7, y, w: 0.5, h: 0.5, fill: { color: C.accent1 }, line: { color: C.accent1 } });
    s.addText(String(i + 1), { x: 0.7, y, w: 0.5, h: 0.5, fontSize: 15, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText([{ text: st[0] + "\n", options: { bold: true, color: C.background1, fontSize: 15 } }, { text: st[1], options: { color: "C9D4DF", fontSize: 13 } }],
      { x: 1.4, y: y - 0.08, w: 4.9, h: 1.0, valign: "top", margin: 0, isTextBox: true });
  });
  s.addText("Questions?", { x: 0.7, y: 6.45, w: 5, h: 0.6, fontSize: 24, bold: true, color: C.accent1, isTextBox: true });
  s.addNotes(NOTES[n++]);
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  const JSZip = require("jszip");
  const zip = await JSZip.loadAsync(fs.readFileSync(OUT), { createFolders: false });
  zip.forEach((p, f) => { if (f.dir) zip.remove(p); });
  for (const name of Object.keys(zip.files).filter(f => /^ppt\/slides\/slide\d+\.xml$/.test(f))) {
    let xml = await zip.file(name).async("string");
    if (!xml.includes("<p:transition")) {
      xml = xml.replace("</p:clrMapOvr>", '</p:clrMapOvr><p:transition spd="med"><p:fade/></p:transition>');
      zip.file(name, xml);
    }
  }
  fs.writeFileSync(OUT, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
  console.log("wrote", OUT, "slides:", n);
})();
