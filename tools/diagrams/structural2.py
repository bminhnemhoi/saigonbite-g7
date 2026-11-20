"""Readable, focused structural diagrams (split so that every diagram stays legible on an A4/Letter page).
class_users, class_orders, class_services, class_strategy, state_order, erd_accounts_catalogue, erd_orders_payments.
Usage: python structural2.py <out_dir>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from structural import (GRAPH, NODE, EDGE, NAVY, GREEN, RED, cls, gen, real, comp, assoc, dep, legend, render, table)  # noqa: E402

G = lambda extra: f"graph [{GRAPH} {extra}]; node [{NODE}]; edge [{EDGE}];"


def class_users():
    n = [
        cls("User", "abstract", ["+ Id : int", "+ Email : string", "+ PasswordHash : string", "+ Role : Role", "+ IsActive : bool"]),
        cls("Customer", "abstract", ["+ Type : CustomerType", "+ DisplayName : string"]),
        cls("LocalCustomer", "entity", ["+ PhoneNumber : string", "+ PhoneVerifiedAt : DateTime?"]),
        cls("ForeignTourist", "entity", ["+ PassportNumber : string", "+ Nationality : string", "+ EmailVerifiedAt : DateTime?"]),
        cls("KitchenStaff", "entity", ["+ HubId : int"]),
        cls("Shipper", "entity", ["+ IsAvailable : bool"]),
        cls("SystemAdmin", "entity"),
        cls("Hub", "entity", ["+ Name : string", "+ KitchenCapacity : int"]),
    ]
    e = [gen("User", "Customer"), gen("User", "KitchenStaff"), gen("User", "Shipper"), gen("User", "SystemAdmin"),
         gen("Customer", "LocalCustomer"), gen("Customer", "ForeignTourist"),
         '"Hub" -> "KitchenStaff" [dir=both arrowtail=odiamond arrowhead=none taillabel="1" headlabel="*" label="  employs"];',
         'n1 [shape=note style=filled fillcolor="#FFF8E6" color="#E9A23B" fontsize=13 label="One schema (BR18, FR1): a single Users table\\nholds login, password hash and role;\\nLocal and Tourist data live in one profile\\ntable per type (EF Core table-per-type)."];',
         '"Customer" -> n1 [style=dashed arrowhead=none color="#E9A23B"];',
         '{rank=same; "Customer"; "KitchenStaff"; "Shipper"; "SystemAdmin"}',
         '{rank=same; "LocalCustomer"; "ForeignTourist"; n1}']
    render("class_users", f"digraph G {{ {G('rankdir=TB nodesep=0.45 ranksep=0.6 splines=spline')}\n" + "\n".join(n + e) + "\n}")


def class_orders():
    n = [
        cls("Customer", "abstract"),
        cls("Hub", "entity", ["+ KitchenCapacity : int", "+ IsActive : bool"], ["+ LoadPercent(active) : decimal"]),
        cls("Brand", "entity", ["+ Name : string", "+ Category : string"]),
        cls("MenuItem", "entity", ["+ Name : string", "+ Price : decimal", "+ IsAvailable : bool"]),
        cls("Voucher", "entity", ["+ Code : string", "+ Type : PERCENT | FIXED", "+ Value, MaxDiscount : decimal", "+ MinSubtotal : decimal"]),
        cls("Order", "entity", ["+ Status : OrderStatus", "+ DeliveryAddress : string", "+ DistanceKm : decimal", "+ Method : PaymentMethod", "+ Snapshot : PriceSnapshot", "+ Price : PriceBreakdown"]),
        cls("OrderLine", "entity", ["+ UnitPrice : decimal", "+ Quantity : int {1..20}"]),
        cls("PriceSnapshot", "value", ["+ PlacedAtLocal : DateTime", "+ HubLoadPercent : decimal", "+ HeavyRainOn : bool"]),
        cls("PriceBreakdown", "value", ["+ S, Q, V : decimal", "+ D, R, R2 : decimal", "+ Total : decimal"]),
        cls("OrderStatusHistory", "entity", ["+ From, To : OrderStatus", "+ ActorUserId : int", "+ ChangedAtLocal : DateTime"]),
        cls("Payment", "entity", ["+ Method : PaymentMethod", "+ Amount : decimal", "+ Status : PaymentStatus", "+ ProviderRef : string?"]),
    ]
    e = [
        assoc("Customer", "Order", "*", "1", "  places"),
        assoc("Hub", "Order", "*", "1", "  cooks"),
        assoc("Voucher", "Order", "*", "0..1", "  applied to"),
        '"Hub" -> "Brand" [arrowhead=none taillabel="*" headlabel="*" label="  operates"];',
        comp("Brand", "MenuItem", "*", "1", "  offers"),
        comp("Order", "OrderLine", "1..30", "1"),
        assoc("OrderLine", "MenuItem", "1", "*", "", "constraint=false"),
        comp("Order", "PriceSnapshot", "1", "1"), comp("Order", "PriceBreakdown", "1", "1"),
        comp("Order", "OrderStatusHistory", "1..*", "1"), comp("Order", "Payment", "1", "1"),
        '{rank=same; "Customer"; "Hub"; "Voucher"}',
        '{rank=same; "OrderLine"; "PriceSnapshot"; "PriceBreakdown"; "OrderStatusHistory"; "Payment"}',
    ]
    lg = legend([("entity", "entity"), ("value", "value object stored with the order (BR17 snapshot)")])
    render("class_orders", f"digraph G {{ {G('rankdir=LR nodesep=0.25 ranksep=0.8 splines=spline')}\n" + "\n".join(n + e) + f"\n{lg}\n}}")


def class_services():
    n = [
        cls("CheckoutController", "controller", [], ["+ Place(CheckoutVm)"]),
        cls("IOrderService", "interface", [], ["+ PlaceOrder(cmd)", "+ EditItems(id, lines)", "+ Cancel(id, actor, reason)"]),
        cls("OrderService", "service"),
        cls("IPricingService", "interface", [], ["+ Quote(PriceRequest) : PriceBreakdown"]),
        cls("PricingService", "service", ["- clock : IClock (UTC+7)"], ["+ Quote(req)", "- QuietDiscount  BR7", "- Voucher        BR9", "- DeliveryFee    BR3, BR6", "- Rush / Rain    BR4, BR5", "- RoundOnce      BR11"]),
        cls("IHubLoadService", "interface", [], ["+ GetLoad(hubId) : decimal", "+ FindAlternatives(addr, km)"]),
        cls("HubLoadService", "service"),
        cls("IOrderStateMachine", "interface", [], ["+ CanTransition(from, to, role)", "+ Transition(order, to, actor)"]),
        cls("OrderStateMachine", "service", ["- allowed : transition table"]),
        cls("IPaymentStrategyResolver", "interface", [], ["+ Resolve(method, type)"]),
    ]
    e = [
        dep("CheckoutController", "IOrderService"), real("IOrderService", "OrderService"),
        dep("OrderService", "IPricingService"), dep("OrderService", "IHubLoadService"),
        dep("OrderService", "IOrderStateMachine"), dep("OrderService", "IPaymentStrategyResolver"),
        real("IPricingService", "PricingService"), real("IHubLoadService", "HubLoadService"),
        real("IOrderStateMachine", "OrderStateMachine"),
        'n1 [shape=note style=filled fillcolor="#FFF8E6" color="#E9A23B" fontsize=13 label="Pricing rules BR1–BR14 live only in\\nPricingService (business layer),\\nin the BR10 order with one rounding."];',
        '"PricingService" -> n1 [style=dashed arrowhead=none color="#E9A23B"];',
        '{rank=same; "IPricingService"; "IHubLoadService"; "IOrderStateMachine"; "IPaymentStrategyResolver"}',
    ]
    lg = legend([("controller", "controller"), ("interface", "interface"), ("service", "service")])
    render("class_services", f"digraph G {{ {G('rankdir=TB nodesep=0.35 ranksep=0.6 splines=spline')}\n" + "\n".join(n + e) + f"\n{lg}\n}}")


def class_strategy():
    n = [
        cls("OrderService", "service", [], ["+ PlaceOrder(cmd)"]),
        cls("IPaymentStrategyResolver", "interface", [], ["+ AvailableFor(type)", "+ Resolve(method, type)"]),
        cls("PaymentStrategyResolver", "service", ["- strategies : IEnumerable<IPaymentStrategy>"]),
        cls("IPaymentStrategy", "interface", ["+ Method : PaymentMethod", "+ Group : CustomerType?"], ["+ Pay(order) : PaymentResult", "+ Refund(payment) : PaymentResult"]),
        cls("MoMoStrategy", "strategy", ["Local · simulated"]),
        cls("VnPayStrategy", "strategy", ["Local · simulated"]),
        cls("CashOnDeliveryStrategy", "strategy", ["both · Total ≤ 1,000,000"]),
        cls("ApplePayStrategy", "strategy", ["Tourist · simulated"]),
        cls("PayPalSandboxStrategy", "strategy", ["Tourist · live sandbox"], ["+ Capture(payment)"]),
    ]
    e = [
        dep("OrderService", "IPaymentStrategyResolver"), real("IPaymentStrategyResolver", "PaymentStrategyResolver"),
        '"PaymentStrategyResolver" -> "IPaymentStrategy" [dir=both arrowtail=odiamond arrowhead=vee headlabel="5" label="  registered in DI"];',
        real("IPaymentStrategy", "MoMoStrategy"), real("IPaymentStrategy", "VnPayStrategy"),
        real("IPaymentStrategy", "CashOnDeliveryStrategy"), real("IPaymentStrategy", "ApplePayStrategy"),
        real("IPaymentStrategy", "PayPalSandboxStrategy"),
        'n1 [shape=note style=filled fillcolor="#FFF8E6" color="#E9A23B" fontsize=13 label="BR13: Local → MoMo, VNPay, COD\\nTourist → Apple Pay, PayPal, COD\\nNFR2: a new method = 1 new class\\n+ 1 DI line, 0 edits to old classes"];',
        '"PaymentStrategyResolver" -> n1 [style=dashed arrowhead=none color="#E9A23B"];',
        '{rank=same; "PaymentStrategyResolver"; n1}',
    ]
    lg = legend([("interface", "interface"), ("service", "service"), ("strategy", "concrete strategy (one class per method)")])
    render("class_strategy", f"digraph G {{ {G('rankdir=TB nodesep=0.3 ranksep=0.6 splines=spline')}\n" + "\n".join(n + e) + f"\n{lg}\n}}")


def state_order():
    def st(nid, label, kind="normal"):
        col = {"normal": NAVY, "ok": GREEN, "bad": RED}[kind]
        fill = {"normal": "white", "ok": "#E8F5EE", "bad": "#FDECEA"}[kind]
        return f'{nid} [shape=box style="rounded,filled" fillcolor="{fill}" color="{col}" penwidth=2 fontsize=16 width=2.2 height=0.55 label=<<B>{label}</B>>];'
    L = lambda ev, guard="", who="": (f'label=<<FONT POINT-SIZE="13"><B>{ev}</B>' + (f"<BR/>[{guard}]" if guard else "")
                                      + (f'<BR/><FONT COLOR="#E4572E"><I>{who}</I></FONT>' if who else "") + "</FONT>>")
    n = ['init [shape=circle style=filled fillcolor="#12263A" width=0.28 label=""];',
         st("Placed", "Placed"), st("Confirmed", "Confirmed"), st("Preparing", "Preparing"), st("Ready", "Ready"),
         st("OFD", "Out for Delivery"), st("Delivered", "Delivered", "ok"), st("Cancelled", "Cancelled", "bad"), st("Failed", "Failed", "bad"),
         'f1 [shape=doublecircle style=filled fillcolor="#12263A" width=0.2 label=""];',
         'f2 [shape=doublecircle style=filled fillcolor="#12263A" width=0.2 label=""];',
         'f3 [shape=doublecircle style=filled fillcolor="#12263A" width=0.2 label=""];']
    e = [f'init -> Placed [{L("place order", "BR1, BR2, BR8, BR12 pass", "Customer")}];',
         f'Placed -> Confirmed [{L("confirm", "staff of the order’s hub", "Kitchen Staff")} weight=6];',
         f'Confirmed -> Preparing [{L("start cooking", "", "Kitchen Staff")} weight=6];',
         f'Preparing -> Ready [{L("mark ready", "", "Kitchen Staff")} weight=6];',
         f'Ready -> OFD [{L("pick up", "shipper assigned by Admin (A-01)", "Shipper")} weight=6];',
         f'OFD -> Delivered [{L("deliver", "COD: cash confirmed (BR14)", "Shipper")} weight=6];',
         f'Placed -> Cancelled [{L("cancel / reject", "kitchen gives a reason", "Customer · Kitchen Staff")}];',
         f'Confirmed -> Cancelled [{L("cancel", "", "Customer · Admin")}];',
         f'OFD -> Failed [{L("report failure", "customer unreachable", "Shipper")}];',
         'Delivered -> f1;', 'Cancelled -> f2;', 'Failed -> f3;',
         'n1 [shape=note style=filled fillcolor="#FFF8E6" color="#E9A23B" fontsize=13 label="entry / full simulated refund\\nif paid online (BR16)"];',
         'n2 [shape=note style=filled fillcolor="#FFF8E6" color="#E9A23B" fontsize=13 label="entry / online: full refund;\\nCOD: nothing collected (A-02)"];',
         'n3 [shape=note style=filled fillcolor="#F1F4F7" color="#9AA5B1" fontsize=13 label="OrderStateMachine (business layer, BR15)\\n• writes OrderStatusHistory on every\\n  accepted transition (NFR6)\\n• rejects every transition not drawn here"];',
         'Cancelled -> n1 [style=dashed arrowhead=none color="#E9A23B"];', 'Failed -> n2 [style=dashed arrowhead=none color="#E9A23B"];',
         'init -> n3 [style=invis];', '{rank=same; init; n3}', '{rank=same; Preparing; Cancelled}', '{rank=same; Delivered; Failed}',
         'Cancelled -> f2 [style=invis];']
    render("state_order", f"digraph S {{ {G('rankdir=TB nodesep=0.9 ranksep=0.42 splines=spline')}\n" + "\n".join(n + e) + "\n}")


ONE_MANY = 'dir=both arrowtail=teetee arrowhead=crowodot'
ONE_ONE = 'dir=both arrowtail=teetee arrowhead=teeodot'
ZERO_MANY = 'dir=both arrowtail=teeodot arrowhead=crowodot'
ONE_ONEMANY = 'dir=both arrowtail=teetee arrowhead=crowtee'


def erd_accounts():
    T = [table("Users", [("Id", "int", "PK"), ("Email", "nvarchar(256)", "UK"), ("PasswordHash", "nvarchar(max)"), ("Role", "tinyint"), ("CustomerType", "tinyint null"), ("IsActive", "bit")]),
         table("LocalCustomerProfiles", [("UserId", "int", "PK,FK"), ("PhoneNumber", "char(10)", "UK"), ("PhoneVerifiedAt", "datetime2")]),
         table("TouristProfiles", [("UserId", "int", "PK,FK"), ("PassportNumber", "nvarchar(9)", "UK"), ("Nationality", "nvarchar(64)"), ("EmailVerifiedAt", "datetime2")]),
         table("StaffProfiles", [("UserId", "int", "PK,FK"), ("HubId", "int null", "FK"), ("IsAvailable", "bit")]),
         table("Hubs", [("Id", "int", "PK"), ("Name", "nvarchar(100)"), ("Address", "nvarchar(256)"), ("KitchenCapacity", "int > 0"), ("IsActive", "bit")]),
         table("HubBrands", [("HubId", "int", "PK,FK"), ("BrandId", "int", "PK,FK")]),
         table("Brands", [("Id", "int", "PK"), ("Name", "nvarchar(100)"), ("Category", "nvarchar(50)"), ("IsActive", "bit")]),
         table("MenuItems", [("Id", "int", "PK"), ("BrandId", "int", "FK"), ("Name", "nvarchar(120)"), ("Price", "decimal(12,0)"), ("IsAvailable", "bit"), ("IsDeleted", "bit")])]
    E = [f'Users:Id -> LocalCustomerProfiles:UserId [{ONE_ONE}];', f'Users:Id -> TouristProfiles:UserId [{ONE_ONE}];',
         f'Users:Id -> StaffProfiles:UserId [{ONE_ONE}];', f'Hubs:Id -> StaffProfiles:HubId [{ZERO_MANY}];',
         f'Hubs:Id -> HubBrands:HubId [{ONE_MANY}];', f'Brands:Id -> HubBrands:BrandId [{ONE_MANY}];',
         f'Brands:Id -> MenuItems:BrandId [{ONE_MANY}];',
         '{rank=same; Users; Hubs; Brands}']
    render("erd_accounts_catalogue", f"digraph E {{ {G('rankdir=LR nodesep=0.35 ranksep=1.1 splines=spline')}\n" + "\n".join(T + E) + "\n}")


def erd_orders():
    T = [table("Users", [("Id", "int", "PK")]), table("Hubs", [("Id", "int", "PK")]), table("MenuItems", [("Id", "int", "PK")]),
         table("Vouchers", [("Id", "int", "PK"), ("Code", "nvarchar(32)", "UK"), ("Type", "tinyint"), ("Value", "decimal"), ("MaxDiscount", "decimal"), ("MinSubtotal", "decimal"), ("ValidFrom, ValidTo", "date"), ("IsActive", "bit")]),
         table("Orders", [("Id", "int", "PK"), ("CustomerId", "int", "FK"), ("HubId", "int", "FK"), ("ShipperId", "int null", "FK"), ("VoucherId", "int null", "FK"), ("Status", "tinyint"), ("DistanceKm", "decimal(4,2)"),
                          ("SnapPlacedAtLocal", "datetime2"), ("SnapHubLoadPct", "decimal(6,3)"), ("SnapHeavyRain", "bit"), ("S, Q, V, D, R, R2", "decimal(12,0)"), ("Total", "decimal(12,0)"), ("PaymentMethod", "tinyint")]),
         table("OrderLines", [("Id", "int", "PK"), ("OrderId", "int", "FK"), ("MenuItemId", "int", "FK"), ("UnitPrice", "decimal(12,0)"), ("Quantity", "int 1–20")]),
         table("OrderStatusHistory", [("Id", "bigint", "PK"), ("OrderId", "int", "FK"), ("FromStatus", "tinyint null"), ("ToStatus", "tinyint"), ("ActorUserId", "int", "FK"), ("ChangedAtLocal", "datetime2")]),
         table("Payments", [("Id", "int", "PK"), ("OrderId", "int", "FK"), ("Method", "tinyint"), ("Amount", "decimal(12,0)"), ("Status", "tinyint"), ("ProviderRef", "nvarchar(64) null")])]
    E = [f'Users:Id -> Orders:CustomerId [{ONE_MANY}];', f'Hubs:Id -> Orders:HubId [{ONE_MANY}];',
         f'Vouchers:Id -> Orders:VoucherId [{ZERO_MANY}];', f'Orders:Id -> OrderLines:OrderId [{ONE_ONEMANY}];',
         f'MenuItems:Id -> OrderLines:MenuItemId [{ONE_MANY}];', f'Orders:Id -> OrderStatusHistory:OrderId [{ONE_ONEMANY}];',
         f'Orders:Id -> Payments:OrderId [{ONE_ONE}];',
         '{rank=same; Users; Hubs; Vouchers}', '{rank=same; OrderLines; OrderStatusHistory; Payments}']
    render("erd_orders_payments", f"digraph E {{ {G('rankdir=LR nodesep=0.3 ranksep=1.0 splines=spline')}\n" + "\n".join(T + E) + "\n}")


if __name__ == "__main__":
    for fn in (class_users, class_orders, class_services, class_strategy, state_order, erd_accounts, erd_orders):
        fn()
