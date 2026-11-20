"""Graphviz-based UML: use case, class (domain + business), state, ERD and activity diagrams.

Every diagram is generated from Python data so that names stay consistent with the report,
the slides and the code skeleton. Output: <out>/<name>.dot and <name>.png (rendered by `dot`).
Usage: python structural.py <out_dir>
"""
import os
import subprocess
import sys
from html import escape

OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
HERE = os.path.dirname(os.path.abspath(__file__))
# Graphviz needs an ASCII path for <IMG>: copy the actor icon to the temp folder.
import shutil, tempfile
ACTOR = os.path.join(tempfile.gettempdir(), "saigonbite_actor.png")
shutil.copyfile(os.path.join(HERE, "actor.png"), ACTOR)
ACTOR = ACTOR.replace("\\", "/")

NAVY, INK, SLATE, LINE = "#12263A", "#1F2933", "#5B6B7A", "#3B4A5A"
CHILI, GREEN, AMBER, RED, BLUE = "#E4572E", "#1E8A5F", "#C98A1E", "#C0392B", "#2E7DAF"

GRAPH = 'fontname="Segoe UI" bgcolor="white" pad="0.3"'
NODE = 'fontname="Segoe UI" fontsize=14 color="#12263A" fontcolor="#1F2933"'
EDGE = 'fontname="Segoe UI" fontsize=13 color="#3B4A5A" fontcolor="#3B4A5A" arrowsize=1.0 penwidth=1.4 labelfontsize=13'


def render(name, dot, dpi=200):
    path = os.path.join(OUT, name + ".dot")
    with open(path, "w", encoding="utf-8") as f:
        f.write(dot)
    # Graphviz cannot open non-ASCII paths on Windows, so pipe through stdin/stdout.
    for fmt, extra in (("png", [f"-Gdpi={dpi}"]), ("svg", [])):
        r = subprocess.run(["dot", f"-T{fmt}", *extra], input=dot.encode("utf-8"), capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.decode("utf-8", "replace"))
        with open(os.path.join(OUT, f"{name}.{fmt}"), "wb") as f:
            f.write(r.stdout)
    print("rendered", name)


# ---------------------------------------------------------------- class boxes
HEADER = {
    "entity": (NAVY, "#FFFFFF"), "abstract": (NAVY, "#FFFFFF"), "service": ("#24384C", "#FFFFFF"),
    "interface": (BLUE, "#FFFFFF"), "strategy": (CHILI, "#FFFFFF"), "value": ("#F3E3BF", INK),
    "enum": ("#DDE3E9", INK), "controller": ("#3B4A5A", "#FFFFFF"),
}
STEREO = {"abstract": "«abstract»", "interface": "«interface»", "value": "«value object»",
          "enum": "«enumeration»", "controller": "«controller»", "strategy": "«strategy»", "service": "«service»"}


def cls(name, kind="entity", attrs=(), ops=(), note=None):
    bg, fg = HEADER[kind]
    st = STEREO.get(kind, "")
    title = f"<I>{escape(name)}</I>" if kind in ("abstract", "interface") else escape(name)
    head = f'<FONT POINT-SIZE="11.5" COLOR="{fg}">{st}</FONT><BR/>' if st else ""
    rows = [f'<TR><TD BGCOLOR="{bg}" CELLPADDING="5">{head}<FONT COLOR="{fg}" POINT-SIZE="16"><B>{title}</B></FONT></TD></TR>']
    if attrs:
        body = "<BR ALIGN=\"LEFT\"/>".join(escape(a) for a in attrs) + "<BR ALIGN=\"LEFT\"/>"
        rows.append(f'<TR><TD ALIGN="LEFT" BALIGN="LEFT" CELLPADDING="5"><FONT FACE="Consolas" POINT-SIZE="13.5">{body}</FONT></TD></TR>')
    if ops:
        body = "<BR ALIGN=\"LEFT\"/>".join(escape(o) for o in ops) + "<BR ALIGN=\"LEFT\"/>"
        rows.append(f'<TR><TD ALIGN="LEFT" BALIGN="LEFT" CELLPADDING="5"><FONT FACE="Consolas" POINT-SIZE="13.5">{body}</FONT></TD></TR>')
    if not attrs and not ops:
        rows.append('<TR><TD HEIGHT="6"></TD></TR>')
    border = "#C8D1DA" if kind in ("value", "enum") else NAVY
    return (f'"{name}" [shape=plain label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" COLOR="{border}" BGCOLOR="white">'
            + "".join(rows) + "</TABLE>>];")


def gen(parent, child):            # generalisation: hollow triangle at the parent
    return f'"{parent}" -> "{child}" [dir=back arrowtail=empty arrowsize=1.1];'


def real(iface, impl):             # realisation
    return f'"{iface}" -> "{impl}" [dir=back arrowtail=empty style=dashed arrowsize=1.1];'


def comp(whole, part, h="", t="", label="", agg=False):
    tail = "odiamond" if agg else "diamond"
    return f'"{whole}" -> "{part}" [dir=both arrowtail={tail} arrowhead=none headlabel="{h}" taillabel="{t}" label="{label}"];'


def assoc(a, b, h="", t="", label="", extra=""):
    return f'"{a}" -> "{b}" [arrowhead=vee headlabel="{h}" taillabel="{t}" label="{label}" {extra}];'


def dep(a, b, label=""):
    return f'"{a}" -> "{b}" [style=dashed arrowhead=vee label="{label}"];'


def legend(items):
    cells = "".join(f'<TD BGCOLOR="{HEADER[k][0]}" WIDTH="14"></TD><TD ALIGN="LEFT"><FONT POINT-SIZE="13">{t}</FONT></TD>' for k, t in items)
    return f'legend [shape=plain label=<<TABLE BORDER="0" CELLSPACING="4"><TR>{cells}</TR></TABLE>>];'


def class_domain():
    n = [
        cls("User", "abstract", ["+ Id : int", "+ Email : string", "+ PasswordHash : string", "+ Role : Role", "+ IsActive : bool", "+ CreatedAtUtc : DateTime"]),
        cls("Customer", "abstract", ["+ Type : CustomerType", "+ DisplayName : string"]),
        cls("LocalCustomer", "entity", ["+ PhoneNumber : string", "+ PhoneVerifiedAt : DateTime?"]),
        cls("ForeignTourist", "entity", ["+ PassportNumber : string", "+ Nationality : string", "+ EmailVerifiedAt : DateTime?"]),
        cls("KitchenStaff", "entity", ["+ HubId : int"]),
        cls("Shipper", "entity", ["+ IsAvailable : bool"]),
        cls("SystemAdmin", "entity"),
        cls("Hub", "entity", ["+ Id : int", "+ Name : string", "+ Address : string", "+ Latitude, Longitude : double", "+ KitchenCapacity : int", "+ IsActive : bool"],
            ["+ LoadPercent(active) : decimal"]),
        cls("Brand", "entity", ["+ Id : int", "+ Name : string", "+ Category : string", "+ IsActive : bool"]),
        cls("MenuItem", "entity", ["+ Id : int", "+ Name : string", "+ Price : decimal", "+ IsAvailable : bool", "+ IsDeleted : bool"]),
        cls("Voucher", "entity", ["+ Code : string", "+ Type : VoucherType", "+ Value : decimal", "+ MaxDiscount : decimal", "+ MinSubtotal : decimal", "+ ValidFrom, ValidTo : DateOnly", "+ IsActive : bool"]),
        cls("Order", "entity", ["+ Id : int", "+ Status : OrderStatus", "+ DeliveryAddress : string", "+ DistanceKm : decimal", "+ Method : PaymentMethod", "+ Snapshot : PriceSnapshot", "+ Price : PriceBreakdown", "+ CancelReason : string?"]),
        cls("OrderLine", "entity", ["+ MenuItemId : int", "+ UnitPrice : decimal", "+ Quantity : int  {1..20}"], ["+ LineTotal() : decimal"]),
        cls("PriceSnapshot", "value", ["+ PlacedAtLocal : DateTime", "+ HubLoadPercent : decimal", "+ HeavyRainOn : bool"]),
        cls("PriceBreakdown", "value", ["+ S, Q, V : decimal", "+ D, R, R2 : decimal", "+ RawTotal : decimal", "+ Total : decimal"]),
        cls("OrderStatusHistory", "entity", ["+ From : OrderStatus?", "+ To : OrderStatus", "+ ActorUserId : int", "+ ChangedAtLocal : DateTime", "+ Reason : string?"]),
        cls("Payment", "entity", ["+ Method : PaymentMethod", "+ Amount : decimal", "+ Status : PaymentStatus", "+ ProviderRef : string?", "+ PaidAt, RefundedAt : DateTime?"]),
        cls("SystemSetting", "entity", ["+ HeavyRainOn : bool", "+ UpdatedAtLocal : DateTime"]),
        cls("OrderStatus", "enum", ["Placed", "Confirmed", "Preparing", "Ready", "OutForDelivery", "Delivered", "Cancelled", "Failed"]),
    ]
    e = [
        gen("User", "Customer"), gen("User", "KitchenStaff"), gen("User", "Shipper"), gen("User", "SystemAdmin"),
        gen("Customer", "LocalCustomer"), gen("Customer", "ForeignTourist"),
        assoc("Customer", "Order", "*", "1", " places"),
        assoc("Shipper", "Order", "*", "0..1", " delivers"),
        assoc("Hub", "Order", "*", "1", " cooks"),
        assoc("Voucher", "Order", "*", "0..1", " applied to"),
        f'"Hub" -> "KitchenStaff" [arrowhead=none dir=both arrowtail=odiamond headlabel="*" taillabel="1" label=" employs" constraint=false];',
        '"Hub" -> "Brand" [arrowhead=none headlabel="*" taillabel="*" label=" operates"];',
        comp("Brand", "MenuItem", "*", "1", " offers"),
        comp("Order", "OrderLine", "1..30", "1"),
        assoc("OrderLine", "MenuItem", "1", "*", "", "constraint=false"),
        comp("Order", "PriceSnapshot", "1", "1"),
        comp("Order", "PriceBreakdown", "1", "1"),
        comp("Order", "OrderStatusHistory", "1..*", "1", " history"),
        comp("Order", "Payment", "1", "1"),
        '"Order" -> "OrderStatus" [style=dashed arrowhead=vee];',
        '{rank=same; "Customer"; "KitchenStaff"; "Shipper"; "SystemAdmin"; "SystemSetting"}',
        '{rank=same; "LocalCustomer"; "ForeignTourist"; "Hub"; "Voucher"}',
    ]
    lg = legend([("abstract", "abstract / entity"), ("value", "value object (owned type)"), ("enum", "enumeration")])
    dot = f"""digraph G {{ graph [{GRAPH} rankdir=TB nodesep=0.35 ranksep=0.55 splines=spline]; node [{NODE}]; edge [{EDGE} labeldistance=1.8 labelangle=35];
{chr(10).join(n)}
{chr(10).join(e)}
{lg}
}}"""
    render("class_domain", dot)


def class_business():
    n = [
        cls("CheckoutController", "controller", ["- orders : IOrderService", "- payments : IPaymentStrategyResolver"], ["+ Index() : IActionResult", "+ Place(CheckoutVm) : IActionResult"]),
        cls("IOrderService", "interface", [], ["+ PlaceOrder(PlaceOrderCommand) : OrderResult", "+ EditItems(orderId, lines) : OrderResult", "+ Cancel(orderId, actor, reason) : OrderResult"]),
        cls("OrderService", "service", ["- pricing : IPricingService", "- hubLoad : IHubLoadService", "- payments : IPaymentStrategyResolver", "- states : IOrderStateMachine", "- db : SaigonBiteDbContext"]),
        cls("IPricingService", "interface", [], ["+ Quote(PriceRequest) : PriceBreakdown"]),
        cls("PricingService", "service", ["- clock : IClock  (UTC+7)"], ["+ Quote(PriceRequest) : PriceBreakdown", "- Validate(req)            BR1, BR2, BR12", "- QuietDiscount(S, load)   BR7", "- VoucherDiscount(S, Q, v) BR9", "- DeliveryFee(km)          BR3, BR6", "- RushSurcharge(D, time)   BR4", "- RainSurcharge(flag)      BR5", "- RoundOnce(raw)           BR11"]),
        cls("IHubLoadService", "interface", [], ["+ GetLoad(hubId) : decimal", "+ CanAccept(hubId) : bool", "+ FindAlternatives(address, km) : List<Hub>"]),
        cls("IOrderStateMachine", "interface", [], ["+ CanTransition(from, to, role) : bool", "+ Transition(order, to, actor, reason)"]),
        cls("OrderStateMachine", "service", ["- allowed : Dictionary<(from, to), Rule>"], ["+ CanTransition(from, to, role) : bool", "+ Transition(order, to, actor, reason)"]),
        cls("IPaymentStrategyResolver", "interface", [], ["+ AvailableFor(CustomerType) : List<PaymentMethod>", "+ Resolve(PaymentMethod, CustomerType) : IPaymentStrategy"]),
        cls("PaymentStrategyResolver", "service", ["- strategies : IEnumerable<IPaymentStrategy>"]),
        cls("IPaymentStrategy", "interface", ["+ Method : PaymentMethod", "+ Group : CustomerType?"], ["+ Pay(Order) : PaymentResult", "+ Refund(Payment) : PaymentResult"]),
        cls("MoMoStrategy", "strategy", ["Group = Local  (simulated)"]),
        cls("VnPayStrategy", "strategy", ["Group = Local  (simulated)"]),
        cls("CashOnDeliveryStrategy", "strategy", ["Group = any  (Total ≤ 1,000,000)"]),
        cls("ApplePayStrategy", "strategy", ["Group = Tourist  (simulated)"]),
        cls("PayPalSandboxStrategy", "strategy", ["Group = Tourist  (live sandbox)", "- client : PayPalClient"], ["+ Capture(Payment) : PaymentResult"]),
    ]
    e = [
        dep("CheckoutController", "IOrderService"),
        real("IOrderService", "OrderService"),
        dep("OrderService", "IPricingService"), dep("OrderService", "IHubLoadService"),
        dep("OrderService", "IOrderStateMachine"), dep("OrderService", "IPaymentStrategyResolver"),
        real("IPricingService", "PricingService"), real("IOrderStateMachine", "OrderStateMachine"),
        real("IPaymentStrategyResolver", "PaymentStrategyResolver"),
        '"PaymentStrategyResolver" -> "IPaymentStrategy" [dir=both arrowtail=odiamond arrowhead=vee headlabel="5" label=" registered in DI"];',
        real("IPaymentStrategy", "MoMoStrategy"), real("IPaymentStrategy", "VnPayStrategy"),
        real("IPaymentStrategy", "CashOnDeliveryStrategy"), real("IPaymentStrategy", "ApplePayStrategy"),
        real("IPaymentStrategy", "PayPalSandboxStrategy"),
        'note1 [shape=note style=filled fillcolor="#FFF8E6" color="#E9A23B" fontsize=13 label="All pricing rules BR1–BR14 live in\\nPricingService (business layer):\\nfixed BR10 order, one rounding (BR11).\\nControllers and views never compute prices."];',
        'note2 [shape=note style=filled fillcolor="#FFF8E6" color="#E9A23B" fontsize=13 label="Strategy pattern (BR13, NFR2)\\nLocal: MoMo · VNPay · COD\\nTourist: Apple Pay · PayPal · COD\\nNew method = 1 new class + 1 DI line,\\n0 edits to existing payment classes."];',
        '"PricingService" -> note1 [style=dashed arrowhead=none color="#E9A23B"];',
        '"IPaymentStrategy" -> note2 [style=dashed arrowhead=none color="#E9A23B" constraint=false];',
        '{rank=same; "IPricingService"; "IHubLoadService"; "IOrderStateMachine"; "IPaymentStrategyResolver"}',
    ]
    lg = legend([("controller", "controller"), ("interface", "interface"), ("service", "service"), ("strategy", "concrete strategy")])
    dot = f"""digraph G {{ graph [{GRAPH} rankdir=TB nodesep=0.3 ranksep=0.55 splines=spline]; node [{NODE}]; edge [{EDGE}];
{chr(10).join(n)}
{chr(10).join(e)}
{lg}
}}"""
    render("class_business", dot)


# ---------------------------------------------------------------- use case
def actor(nid, label, abstract=False, system=False):
    if system:
        return (f'{nid} [shape=box style="rounded,dashed" color="{AMBER}" fontcolor="{INK}" '
                f'label=<<FONT POINT-SIZE="9" COLOR="{SLATE}">«system»</FONT><BR/><B>{label}</B>>];')
    name = f"<I>{label}</I>" if abstract else label
    return (f'{nid} [shape=plain label=<<TABLE BORDER="0" CELLSPACING="0" CELLPADDING="1">'
            f'<TR><TD><IMG SRC="{ACTOR}"/></TD></TR><TR><TD><FONT POINT-SIZE="11"><B>{name}</B></FONT></TD></TR></TABLE>>];')


def uc(nid, label, kind="normal"):
    styles = {
        "normal": 'fillcolor="white" color="#12263A"',
        "uc1": f'fillcolor="#FFF1EC" color="{CHILI}" penwidth=2',
        "uc2": f'fillcolor="#EAF3FB" color="{BLUE}" penwidth=2',
        "tier4": f'fillcolor="#FFF8E6" color="{AMBER}" penwidth=1.6',
        "inc": 'fillcolor="#F7F9FB" color="#5B6B7A"',
    }
    return f'{nid} [shape=ellipse style=filled {styles[kind]} margin="0.08,0.04" label=<{label}>];'


def usecase():
    n = [
        actor("LC", "Local Customer"), actor("FT", "Foreign Tourist"), actor("CU", "Customer", abstract=True),
        actor("KS", "Kitchen Staff"), actor("SH", "Shipper"), actor("AD", "System Admin"),
        actor("PP", "PayPal Sandbox", system=True),
    ]
    ucs = [
        uc("REG", "Register Account<BR/><FONT POINT-SIZE='9'>phone + OTP / passport + email</FONT>"),
        uc("BROWSE", "Browse Hubs, Brands<BR/>and Menus"),
        uc("UC1", "<B>UC1 · Place and Manage Orders</B><BR/><FONT POINT-SIZE='9'>place · track · edit · cancel</FONT>", "uc1"),
        uc("CALC", "Calculate Price<BR/><FONT POINT-SIZE='9'>BR1–BR12</FONT>", "inc"),
        uc("PAYSEL", "Select Payment<BR/>Method <FONT POINT-SIZE='9'>(BR13, BR14)</FONT>", "inc"),
        uc("PAYPAL", "Pay with PayPal<BR/>Sandbox <FONT POINT-SIZE='9'>(Tier 4)</FONT>", "tier4"),
        uc("PROC", "Process Orders<BR/><FONT POINT-SIZE='9'>confirm · reject · prepare · ready</FONT>"),
        uc("DELIV", "Deliver Orders<BR/><FONT POINT-SIZE='9'>pick up · confirm cash · fail</FONT>"),
        uc("UC2", "<B>UC2 · Manage Hubs &amp; Capacity</B><BR/><FONT POINT-SIZE='9'>create · view · edit · deactivate</FONT>", "uc2"),
        uc("LOAD", "View Hub Load<BR/><FONT POINT-SIZE='9'>BR7, BR8</FONT>", "inc"),
        uc("MENU", "Manage Menu<BR/>&amp; Brands"),
        uc("VOUCH", "Manage Vouchers"),
        uc("ACCT", "Manage User<BR/>Accounts"),
        uc("ASSIGN", "Assign Shipper<BR/><FONT POINT-SIZE='9'>A-01</FONT>"),
        uc("RAIN", "Set Heavy-Rain<BR/>Flag"),
        uc("R1", "View Revenue<BR/>Report R1"),
        uc("R2", "View Hub Utilization<BR/>Report R2"),
        uc("DASH", "Use Admin Dashboard<BR/><FONT POINT-SIZE='9'>(Tier 4)</FONT>", "tier4"),
    ]
    inc = 'style=dashed arrowhead=vee fontsize=9 label="«include»"'
    ext = 'style=dashed arrowhead=vee fontsize=9 label="«extend»"'
    e = [
        'LC -> CU [arrowhead=empty arrowsize=1.1];', 'FT -> CU [arrowhead=empty arrowsize=1.1];',
        'CU -> REG [arrowhead=none];', 'CU -> BROWSE [arrowhead=none];', 'CU -> UC1 [arrowhead=none penwidth=1.6];',
        f'UC1 -> CALC [{inc}];', f'UC1 -> PAYSEL [{inc}];', f'PAYPAL -> PAYSEL [{ext} constraint=false];',
        'PAYSEL -> PAYPAL [style=invis];',
        'PAYPAL -> PP [arrowhead=none];',
        'PROC -> KS [arrowhead=none];', 'DELIV -> SH [arrowhead=none];',
        'UC2 -> AD [arrowhead=none penwidth=1.6];', f'UC2 -> LOAD [{inc}];',
        'MENU -> AD [arrowhead=none];', 'VOUCH -> AD [arrowhead=none];', 'ACCT -> AD [arrowhead=none];',
        'ASSIGN -> AD [arrowhead=none];', 'RAIN -> AD [arrowhead=none];', 'R1 -> AD [arrowhead=none];',
        'R2 -> AD [arrowhead=none];', 'DASH -> AD [arrowhead=none];',
        f'DASH -> R1 [{inc} constraint=false];', f'DASH -> R2 [{inc} constraint=false];',
        'BROWSE -> PROC [style=invis];', 'PROC -> DELIV [style=invis];',
    ]
    leg = (f'legend [shape=plain label=<<TABLE BORDER="0" CELLSPACING="5"><TR>'
           f'<TD BGCOLOR="#FFF1EC" WIDTH="14" STYLE="rounded"></TD><TD ALIGN="LEFT"><FONT POINT-SIZE="10">UC1 owner: Lê Xuân Khánh (524H0055)</FONT></TD>'
           f'<TD BGCOLOR="#EAF3FB" WIDTH="14"></TD><TD ALIGN="LEFT"><FONT POINT-SIZE="10">UC2 owner: Ngô Bình Minh (524H0169)</FONT></TD>'
           f'<TD BGCOLOR="#FFF8E6" WIDTH="14"></TD><TD ALIGN="LEFT"><FONT POINT-SIZE="10">Tier 4 extension</FONT></TD>'
           f'<TD BGCOLOR="#F7F9FB" WIDTH="14"></TD><TD ALIGN="LEFT"><FONT POINT-SIZE="10">included use case</FONT></TD></TR></TABLE>>];')
    dot = f"""digraph UC {{ graph [{GRAPH} rankdir=LR nodesep=0.22 ranksep=0.75 splines=spline newrank=true compound=true];
node [{NODE}]; edge [{EDGE}];
{chr(10).join(n)}
subgraph cluster_sys {{ label=<<B>SaigonBite Platform</B>> labeljust=l fontsize=14 fontcolor="#12263A" style="rounded,filled" fillcolor="#FBFCFD" color="#12263A" penwidth=1.5 margin=18;
{chr(10).join(ucs)}
}}
{chr(10).join(e)}
{{rank=same; KS; SH; AD; PP}}
{leg}
}}"""
    render("usecase_overview", dot)


# ---------------------------------------------------------------- state
def state():
    def st(nid, label, kind="normal"):
        col = {"normal": NAVY, "ok": GREEN, "bad": RED}[kind]
        fill = {"normal": "white", "ok": "#E8F5EE", "bad": "#FDECEA"}[kind]
        return f'{nid} [shape=box style="rounded,filled" fillcolor="{fill}" color="{col}" penwidth=1.6 fontsize=12 margin="0.18,0.08" label=<<B>{label}</B>>];'
    n = [
        'init [shape=circle style=filled fillcolor="#12263A" width=0.22 label=""];',
        st("Placed", "Placed"), st("Confirmed", "Confirmed"), st("Preparing", "Preparing"), st("Ready", "Ready"),
        st("OFD", "Out for Delivery"), st("Delivered", "Delivered", "ok"), st("Cancelled", "Cancelled", "bad"), st("Failed", "Failed", "bad"),
        'fin1 [shape=doublecircle style=filled fillcolor="#12263A" width=0.16 label=""];',
        'fin2 [shape=doublecircle style=filled fillcolor="#12263A" width=0.16 label=""];',
        'fin3 [shape=doublecircle style=filled fillcolor="#12263A" width=0.16 label=""];',
    ]
    L = lambda ev, guard="", actor="": f'label=<<FONT POINT-SIZE="10"><B>{ev}</B>{"<BR/>[" + guard + "]" if guard else ""}{"<BR/><I>" + actor + "</I>" if actor else ""}</FONT>>'
    e = [
        f'init -> Placed [{L("place order", "BR1, BR2, BR8, BR12, BR13 pass", "Customer")}];',
        f'Placed -> Confirmed [{L("confirm", "staff of the order’s hub", "Kitchen Staff")} weight=4];',
        f'Confirmed -> Preparing [{L("start cooking", "", "Kitchen Staff")} weight=4];',
        f'Preparing -> Ready [{L("mark ready", "", "Kitchen Staff")} weight=4];',
        f'Ready -> OFD [{L("pick up", "assigned shipper – A-01", "Shipper")} weight=4];',
        f'OFD -> Delivered [{L("deliver", "COD: cash confirmed – BR14", "Shipper")} weight=4];',
        f'Placed -> Cancelled [{L("cancel / reject", "kitchen must give a reason", "Customer · Kitchen Staff")}];',
        f'Confirmed -> Cancelled [{L("cancel", "", "Customer · Admin")}];',
        f'OFD -> Failed [{L("report failure", "customer unreachable", "Shipper")}];',
        'Delivered -> fin1;', 'Cancelled -> fin2;', 'Failed -> fin3;',
        'n1 [shape=note style=filled fillcolor="#FFF8E6" color="#E9A23B" fontsize=10 label="Cancelled\\nentry / full simulated refund\\nif paid online (BR16)"];',
        'n2 [shape=note style=filled fillcolor="#FFF8E6" color="#E9A23B" fontsize=10 label="Failed\\nentry / online: full refund\\nCOD: nothing collected (A-02)"];',
        'n3 [shape=note style=filled fillcolor="#FFF8E6" color="#E9A23B" fontsize=10 label="Enforced by OrderStateMachine in the business layer (BR15):\\nevery accepted transition writes OrderStatusHistory\\n(old state, new state, actor, Vietnam time – NFR6);\\nany transition not drawn here is rejected."];',
        'Cancelled -> n1 [style=dashed arrowhead=none color="#E9A23B"];',
        'Failed -> n2 [style=dashed arrowhead=none color="#E9A23B"];',
        'init -> n3 [style=invis];',
        '{rank=same; Placed; n3}',
        '{rank=same; Preparing; Cancelled}',
        '{rank=same; Delivered; Failed}',
    ]
    dot = f"""digraph S {{ graph [{GRAPH} rankdir=LR nodesep=0.55 ranksep=0.42 splines=spline]; node [{NODE}]; edge [{EDGE}];
{chr(10).join(n)}
{chr(10).join(e)}
}}"""
    render("state_order", dot)


# ---------------------------------------------------------------- ERD
def table(name, cols):
    rows = [f'<TR><TD COLSPAN="3" BGCOLOR="{NAVY}" CELLPADDING="5"><FONT COLOR="white" POINT-SIZE="15"><B>{name}</B></FONT></TD></TR>']
    for c in cols:
        cname, ctype, key = (c + ("",))[:3] if isinstance(c, tuple) else (c, "", "")
        badge = ""
        if key:
            colr = {"PK": "#E9A23B", "FK": BLUE, "UK": GREEN, "PK,FK": "#E9A23B"}[key]
            badge = f'<FONT COLOR="{colr}" POINT-SIZE="12"><B>{key}</B></FONT>'
        cn = f"<B>{cname}</B>" if "PK" in key else cname
        rows.append(f'<TR><TD ALIGN="LEFT" PORT="{cname}" CELLPADDING="3">{badge}</TD><TD ALIGN="LEFT" CELLPADDING="3"><FONT FACE="Consolas" POINT-SIZE="13.5">{cn}</FONT></TD>'
                    f'<TD ALIGN="LEFT" CELLPADDING="3"><FONT FACE="Consolas" POINT-SIZE="12" COLOR="{SLATE}">{escape(ctype)}</FONT></TD></TR>')
    return (f'{name} [shape=plain label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" COLOR="#9AA5B1" BGCOLOR="white">'
            + "".join(rows) + "</TABLE>>];")


def erd():
    T = [
        table("Users", [("Id", "int", "PK"), ("Email", "nvarchar(256)", "UK"), ("PasswordHash", "nvarchar(max)"), ("Role", "tinyint"), ("CustomerType", "tinyint null"), ("IsActive", "bit"), ("CreatedAtUtc", "datetime2")]),
        table("LocalCustomerProfiles", [("UserId", "int", "PK,FK"), ("PhoneNumber", "char(10)", "UK"), ("PhoneVerifiedAt", "datetime2 null")]),
        table("TouristProfiles", [("UserId", "int", "PK,FK"), ("PassportNumber", "nvarchar(9)", "UK"), ("Nationality", "nvarchar(64)"), ("EmailVerifiedAt", "datetime2 null")]),
        table("StaffProfiles", [("UserId", "int", "PK,FK"), ("HubId", "int null", "FK"), ("IsAvailable", "bit")]),
        table("Hubs", [("Id", "int", "PK"), ("Name", "nvarchar(100)"), ("Address", "nvarchar(256)"), ("Latitude", "float"), ("Longitude", "float"), ("KitchenCapacity", "int > 0"), ("IsActive", "bit")]),
        table("Brands", [("Id", "int", "PK"), ("Name", "nvarchar(100)"), ("Category", "nvarchar(50)"), ("IsActive", "bit")]),
        table("HubBrands", [("HubId", "int", "PK,FK"), ("BrandId", "int", "PK,FK")]),
        table("MenuItems", [("Id", "int", "PK"), ("BrandId", "int", "FK"), ("Name", "nvarchar(120)"), ("Price", "decimal(12,0)"), ("IsAvailable", "bit"), ("IsDeleted", "bit")]),
        table("Vouchers", [("Id", "int", "PK"), ("Code", "nvarchar(32)", "UK"), ("Type", "tinyint"), ("Value", "decimal(12,2)"), ("MaxDiscount", "decimal(12,0)"), ("MinSubtotal", "decimal(12,0)"), ("ValidFrom", "date"), ("ValidTo", "date"), ("IsActive", "bit")]),
        table("Orders", [("Id", "int", "PK"), ("CustomerId", "int", "FK"), ("HubId", "int", "FK"), ("ShipperId", "int null", "FK"), ("VoucherId", "int null", "FK"), ("Status", "tinyint"), ("DeliveryAddress", "nvarchar(256)"), ("DistanceKm", "decimal(4,2)"),
                         ("SnapPlacedAtLocal", "datetime2"), ("SnapHubLoadPct", "decimal(6,3)"), ("SnapHeavyRain", "bit"), ("S, Q, V", "decimal(12,0)"), ("D, R, R2", "decimal(12,0)"), ("Total", "decimal(12,0)"), ("PaymentMethod", "tinyint"), ("RowVersion", "rowversion")]),
        table("OrderLines", [("Id", "int", "PK"), ("OrderId", "int", "FK"), ("MenuItemId", "int", "FK"), ("UnitPrice", "decimal(12,0)"), ("Quantity", "int 1–20")]),
        table("OrderStatusHistory", [("Id", "bigint", "PK"), ("OrderId", "int", "FK"), ("FromStatus", "tinyint null"), ("ToStatus", "tinyint"), ("ActorUserId", "int", "FK"), ("ChangedAtLocal", "datetime2"), ("Reason", "nvarchar(256) null")]),
        table("Payments", [("Id", "int", "PK"), ("OrderId", "int", "FK"), ("Method", "tinyint"), ("Amount", "decimal(12,0)"), ("Status", "tinyint"), ("ProviderRef", "nvarchar(64) null"), ("PaidAt", "datetime2 null"), ("RefundedAt", "datetime2 null")]),
        table("SystemSettings", [("Id", "int", "PK"), ("HeavyRainOn", "bit"), ("UpdatedBy", "int", "FK"), ("UpdatedAtLocal", "datetime2")]),
    ]
    one_many = 'dir=both arrowtail=teetee arrowhead=crowodot'
    one_one = 'dir=both arrowtail=teetee arrowhead=teeodot'
    zero_many = 'dir=both arrowtail=teeodot arrowhead=crowodot'
    one_onemany = 'dir=both arrowtail=teetee arrowhead=crowtee'
    E = [
        f'Users:Id -> LocalCustomerProfiles:UserId [{one_one}];',
        f'Users:Id -> TouristProfiles:UserId [{one_one}];',
        f'Users:Id -> StaffProfiles:UserId [{one_one}];',
        f'Hubs:Id -> StaffProfiles:HubId [{zero_many}];',
        f'Hubs:Id -> HubBrands:HubId [{one_many}];',
        f'Brands:Id -> HubBrands:BrandId [{one_many}];',
        f'Brands:Id -> MenuItems:BrandId [{one_many}];',
        f'Users:Id -> Orders:CustomerId [{one_many}];',
        f'Hubs:Id -> Orders:HubId [{one_many}];',
        f'Vouchers:Id -> Orders:VoucherId [{zero_many}];',
        f'Orders:Id -> OrderLines:OrderId [{one_onemany}];',
        f'MenuItems:Id -> OrderLines:MenuItemId [{one_many}];',
        f'Orders:Id -> OrderStatusHistory:OrderId [{one_onemany}];',
        f'Orders:Id -> Payments:OrderId [{one_one}];',
    ]
    dot = f"""digraph ERD {{ graph [{GRAPH} rankdir=LR nodesep=0.3 ranksep=1.0 splines=spline]; node [{NODE}]; edge [{EDGE} penwidth=1.2];
{chr(10).join(T)}
{chr(10).join(E)}
{{rank=same; Users; Hubs; Brands; Vouchers}}
{{rank=same; LocalCustomerProfiles; TouristProfiles; StaffProfiles; HubBrands; MenuItems; Orders; SystemSettings}}
}}"""
    render("erd", dot)


# ---------------------------------------------------------------- activity
def activity():
    def act(nid, label, kind="normal"):
        col, fill = {"normal": (NAVY, "white"), "bad": (RED, "#FDECEA"), "ok": (GREEN, "#E8F5EE"), "calc": (NAVY, "#F7F9FB")}[kind]
        return f'{nid} [shape=box style="rounded,filled" fillcolor="{fill}" color="{col}" penwidth=1.3 fontsize=11 margin="0.16,0.07" label=<{label}>];'
    dec = lambda nid: f'{nid} [shape=diamond style=filled fillcolor="#FFF8E6" color="#C98A1E" width=0.32 height=0.32 label="" fixedsize=true];'
    n = [
        'start [shape=circle style=filled fillcolor="#12263A" width=0.22 label=""];',
        act("val", "Validate request<BR/><FONT POINT-SIZE='9'>S, distance, lines, availability</FONT>"), dec("d1"),
        act("rej1", "Reject: show the failed rule<BR/><FONT POINT-SIZE='9'>BR1 · BR2 · BR12</FONT>", "bad"),
        act("load", "Read hub load (snapshot)<BR/><FONT POINT-SIZE='9'>Confirmed + Preparing ÷ capacity</FONT>"), dec("d2"),
        act("rej2", "Reject: offer hubs &lt; 90%<BR/>within 8 km <FONT POINT-SIZE='9'>(BR8, A-04)</FONT>", "bad"),
        act("q", "<B>Q</B> = 10% × S if load &lt; 30%, else 0 <FONT POINT-SIZE='9'>BR7</FONT>", "calc"),
        act("v", "<B>V</B> = voucher on (S − Q), capped <FONT POINT-SIZE='9'>BR9</FONT>", "calc"),
        act("f", "<B>F</B> = S − Q − V", "calc"), dec("d3"),
        act("d0", "<B>D</B> = 0, <B>R</B> = 0 <FONT POINT-SIZE='9'>free delivery BR6</FONT>", "calc"),
        act("d", "<B>D</B> by distance tier <FONT POINT-SIZE='9'>BR3</FONT>", "calc"),
        act("r", "<B>R</B> = 20% × D in [11:00,13:00) or [17:30,19:30) <FONT POINT-SIZE='9'>BR4</FONT>", "calc"),
        'm1 [shape=diamond style=filled fillcolor="#FFF8E6" color="#C98A1E" width=0.32 height=0.32 label="" fixedsize=true];',
        act("r2", "<B>R2</B> = 10,000 if heavy-rain flag <FONT POINT-SIZE='9'>BR5 (snapshotted)</FONT>", "calc"),
        act("raw", "Raw = F + D + R + R2", "calc"),
        act("round", "<B>Total</B> = round once to nearest 1,000 <FONT POINT-SIZE='9'>BR11</FONT>", "calc"), dec("d4"),
        act("rej3", "Ask for another payment method", "bad"),
        act("ok", "Return PriceBreakdown<BR/><FONT POINT-SIZE='9'>S · Q · V · F · D · R · R2 · Total</FONT>", "ok"),
        'end1 [shape=doublecircle style=filled fillcolor="#12263A" width=0.16 label=""];',
        'end2 [shape=doublecircle style=filled fillcolor="#12263A" width=0.16 label=""];',
    ]
    g = lambda t: f'label=<<FONT POINT-SIZE="9.5">[{t}]</FONT>>'
    e = [
        "start -> val;", "val -> d1;", f"d1 -> rej1 [{g('invalid')}];", f"d1 -> load [{g('valid')} weight=5];",
        "load -> d2;", f"d2 -> rej2 [{g('load ≥ 90%')}];", f"d2 -> q [{g('load &lt; 90%')} weight=5];",
        "q -> v [weight=5];", "v -> f [weight=5];", "f -> d3 [weight=5];",
        f"d3 -> d0 [{g('S ≥ 300,000')}];", f"d3 -> d [{g('S &lt; 300,000')} weight=5];", "d -> r [weight=5];",
        "r -> m1 [weight=5];", "d0 -> m1;", "m1 -> r2 [weight=5];", "r2 -> raw [weight=5];", "raw -> round [weight=5];",
        "round -> d4 [weight=5];", f"d4 -> rej3 [{g('COD and Total &gt; 1,000,000 · BR14')}];", f"d4 -> ok [{g('otherwise')} weight=5];",
        "ok -> end1;", "rej1 -> end2;", "rej2 -> end2;", "rej3 -> end2;",
    ]
    dot = f"""digraph A {{ graph [{GRAPH} rankdir=TB nodesep=0.45 ranksep=0.32 splines=spline]; node [{NODE}]; edge [{EDGE}];
{chr(10).join(n)}
{chr(10).join(e)}
}}"""
    render("activity_pricing", dot)


if __name__ == "__main__":
    # This module now only provides the shared Graphviz helpers. The diagrams used in the report are built by
    # structural2.py (class, state, ERD), ucdiag.py (use case) and sequences.py (sequence diagrams).
    print("Use structural2.py, ucdiag.py and sequences.py to build the Part 2 diagrams.")
