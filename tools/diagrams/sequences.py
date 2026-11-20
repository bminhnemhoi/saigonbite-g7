"""Sequence diagrams for Part 2. Each use case is split into two readable parts joined by a `ref`.
UC1 (author 524H0055): PlaceOrder 1/2 hub check + price, 2/2 payment + persistence.
UC2 (author 524H0169): ManageHubs 1/2 create + list, 2/2 edit + soft-delete.
Tier 4: PayWithPayPal (live sandbox)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seqdiag import Seq  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "."


def uc1_part1():
    s = Seq("PlaceOrder (1/2) – check the hub and quote the price")
    s.p("C", "Customer\n(Local / Tourist)", "actor")
    s.p("CC", "CheckoutController", "boundary")
    s.p("OS", "OrderService", "control")
    s.p("HL", "HubLoadService", "control")
    s.p("PS", "PricingService", "control")
    s.p("DB", "SaigonBiteDbContext", "database")
    s.msg("C", "CC", "POST /checkout (cart, address, voucher, method)").act("CC")
    s.msg("CC", "OS", "PlaceOrder(command, customerId)").act("OS")
    s.msg("OS", "HL", "GetLoad(hubId)").act("HL")
    s.msg("HL", "DB", "count Confirmed + Preparing orders")
    s.reply("HL", "OS", "load = active ÷ capacity (unrounded)").deact("HL")
    s.frag("alt", "load ≥ 90%  (BR8, FR7)")
    s.msg("OS", "HL", "FindAlternatives(address, 8 km)")
    s.reply("HL", "OS", "active hubs below 90% (A-04)")
    s.reply("OS", "CC", "HubFull(alternatives)")
    s.reply("CC", "C", "“This hub is busy – choose another one”")
    s.else_("load < 90%")
    s.msg("OS", "PS", "Quote(lines, km, time, load, rain, voucher)").act("PS")
    s.self_("PS", "check BR1, BR2, BR12")
    s.self_("PS", "S → Q → V → F → D → R → R2, round once (BR10, BR11)")
    s.reply("PS", "OS", "PriceBreakdown").deact("PS")
    s.ref("C", "DB", "PlaceOrder (2/2) – choose payment and save the order")
    s.end().deact("OS").deact("CC")
    return s


def uc1_part2():
    s = Seq("PlaceOrder (2/2) – choose payment and save the order")
    s.p("C", "Customer", "actor")
    s.p("CC", "CheckoutController", "boundary")
    s.p("OS", "OrderService", "control")
    s.p("PR", "PaymentStrategy\nResolver", "control")
    s.p("ST", "IPaymentStrategy", "strategy")
    s.p("SM", "OrderState\nMachine", "control")
    s.p("DB", "SaigonBiteDbContext", "database")
    s.act("CC").act("OS")
    s.msg("OS", "PR", "Resolve(method, customerType)")
    s.frag("alt", "method of the other group, or COD above 1,000,000")
    s.reply("PR", "OS", "rejected (BR13, BR14)")
    s.reply("OS", "CC", "ValidationError")
    s.reply("CC", "C", "show only the allowed methods")
    s.else_("method allowed")
    s.reply("PR", "OS", "strategy")
    s.msg("OS", "DB", "BEGIN TRAN; INSERT Order (Placed, snapshot) + lines")
    s.msg("OS", "SM", "RecordCreated(order)").act("SM")
    s.msg("SM", "DB", "INSERT history (∅ → Placed)").deact("SM")
    s.msg("OS", "ST", "Pay(order)").act("ST")
    s.reply("ST", "OS", "PaymentResult").deact("ST")
    s.frag("alt", "payment failed")
    s.msg("OS", "DB", "ROLLBACK (nothing saved – NFR5)")
    s.reply("OS", "CC", "PaymentFailed")
    s.reply("CC", "C", "“Payment failed, nothing charged”")
    s.else_("paid, pending or approval needed")
    s.msg("OS", "DB", "COMMIT")
    s.reply("OS", "CC", "OrderPlaced(id, breakdown)")
    s.reply("CC", "C", "confirmation + tracking page")
    s.end().end().deact("OS").deact("CC")
    return s


def uc2_part1():
    s = Seq("ManageHubs (1/2) – create a hub and list hubs with load")
    s.p("A", "System Admin", "actor")
    s.p("HC", "HubsController", "boundary")
    s.p("HS", "HubService", "control")
    s.p("HL", "HubLoadService", "control")
    s.p("DB", "SaigonBiteDbContext", "database")
    s.section("Create – FR5, FR28")
    s.msg("A", "HC", "POST /admin/hubs (name, address, capacity, brands)").act("HC")
    s.msg("HC", "HS", "Create(dto)").act("HS")
    s.self_("HS", "validate: capacity is a positive whole number")
    s.frag("alt", "invalid input")
    s.reply("HS", "HC", "field errors")
    s.reply("HC", "A", "form shown again with errors")
    s.else_("valid")
    s.msg("HS", "DB", "INSERT Hub + HubBrands")
    s.reply("HC", "A", "redirect to the hub list")
    s.end().deact("HS").deact("HC")
    s.section("Read – FR6, BR7, BR8")
    s.msg("A", "HC", "GET /admin/hubs").act("HC")
    s.msg("HC", "HS", "ListWithLoad()").act("HS")
    s.frag("loop", "each hub")
    s.msg("HS", "HL", "GetLoad(hubId)")
    s.reply("HL", "HS", "load % (unrounded)")
    s.end()
    s.reply("HS", "HC", "rows with band: Quiet < 30% · Normal · Full ≥ 90%").deact("HS")
    s.reply("HC", "A", "hub table with load bars").deact("HC")
    return s


def uc2_part2():
    s = Seq("ManageHubs (2/2) – edit a hub and deactivate it (soft-delete)")
    s.p("A", "System Admin", "actor")
    s.p("HC", "HubsController", "boundary")
    s.p("HS", "HubService", "control")
    s.p("DB", "SaigonBiteDbContext", "database")
    s.section("Update")
    s.msg("A", "HC", "POST /admin/hubs/{id}/edit (capacity, brands)").act("HC")
    s.msg("HC", "HS", "Update(id, dto)").act("HS")
    s.msg("HS", "DB", "UPDATE Hub, replace HubBrands")
    s.reply("HS", "HC", "ok – load uses the new capacity").deact("HS")
    s.reply("HC", "A", "updated row").deact("HC")
    s.section("Delete = soft-delete – FR5, FR24, A-07")
    s.msg("A", "HC", "POST /admin/hubs/{id}/deactivate").act("HC")
    s.msg("HC", "HS", "Deactivate(id)").act("HS")
    s.msg("HS", "DB", "COUNT active orders (Placed … Out for Delivery)")
    s.frag("alt", "hub still has active orders")
    s.reply("HS", "HC", "Blocked(count)")
    s.reply("HC", "A", "“Hub has N active orders – try later”")
    s.else_("no active order")
    s.msg("HS", "DB", "UPDATE Hub SET IsActive = 0")
    s.reply("HS", "HC", "ok")
    s.reply("HC", "A", "hub shown as Inactive; history and R2 kept")
    s.end().deact("HS").deact("HC")
    return s


def paypal():
    s = Seq("PayWithPayPal – Tier 4 live sandbox (FR36)")
    s.p("T", "Foreign Tourist", "actor")
    s.p("CC", "Checkout /\nPayment Controller", "boundary")
    s.p("OS", "OrderService", "control")
    s.p("PP", "PayPalSandbox\nStrategy", "strategy")
    s.p("API", "PayPal Sandbox\nREST API", "external")
    s.p("DB", "SaigonBiteDbContext", "database")
    s.msg("T", "CC", "Pay with PayPal").act("CC")
    s.msg("CC", "OS", "PlaceOrder(method = PayPal)").act("OS")
    s.msg("OS", "PP", "Pay(order)").act("PP")
    s.msg("PP", "API", "OAuth token, POST /v2/checkout/orders")
    s.reply("API", "PP", "order id + approve link")
    s.reply("PP", "OS", "ApprovalRequired").deact("PP")
    s.msg("OS", "DB", "Order Placed, Payment Pending")
    s.reply("OS", "CC", "approve URL").deact("OS")
    s.reply("CC", "T", "redirect to PayPal sandbox").deact("CC")
    s.msg("T", "API", "approve with the sandbox buyer account")
    s.reply("API", "T", "redirect to /payments/paypal/return")
    s.msg("T", "CC", "GET /payments/paypal/return").act("CC")
    s.msg("CC", "OS", "ConfirmOnlinePayment(token)").act("OS")
    s.msg("OS", "PP", "Capture(payment)").act("PP")
    s.msg("PP", "API", "POST …/orders/{id}/capture")
    s.frag("alt", "COMPLETED")
    s.reply("API", "PP", "capture id")
    s.msg("OS", "DB", "Payment = Paid (capture id stored)")
    s.reply("CC", "T", "payment confirmed → tracking")
    s.else_("declined or cancelled by the buyer")
    s.msg("OS", "DB", "Payment Failed; order Cancelled + history")
    s.reply("CC", "T", "“Not paid – order cancelled”")
    s.end().deact("PP").deact("OS").deact("CC")
    return s


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in [("seq_uc1_place_order_1", uc1_part1), ("seq_uc1_place_order_2", uc1_part2),
                     ("seq_uc2_manage_hubs_1", uc2_part1), ("seq_uc2_manage_hubs_2", uc2_part2),
                     ("seq_tier4_paypal_sandbox", paypal)]:
        w, h = fn().render(os.path.join(OUT, name + ".svg"))
        print(f"{name}: {w:.0f} x {h:.0f}")
