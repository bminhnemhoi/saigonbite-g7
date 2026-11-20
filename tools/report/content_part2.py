"""Text content of Part 2 (and the Tier 4 updates of Part 1) for the Team G7 report."""

COVER_PART = "Part 1 & Part 2: Requirements Engineering · Software Design, Architecture & UI/UX"

ABSTRACT = ("SaigonBite is a delivery-only cloud-kitchen network in Ho Chi Minh City. This report, version 2.0, combines the Part 1 "
            "requirements baseline (37 functional requirements, 7 measurable quality attributes and 8 documented assumptions) with "
            "the Part 2 design: an overall use case diagram with actor generalisation, formal specifications and sequence diagrams for "
            "UC1 Place and Manage Orders and UC2 Manage Hubs & Capacity, the team state diagram of the 8-state order lifecycle, CRC cards, "
            "class diagrams with the payment Strategy pattern, the database design, a three-layer ASP.NET Core MVC architecture linked to "
            "the NFRs, and a responsive Bootstrap UI prototype in Figma. Following the instructor’s approval at Presentation 1 the team "
            "now targets Tier 4: a live PayPal Developer sandbox, an interactive Admin dashboard and Playwright end-to-end tests.")

FEEDBACK_INTRO = ("The table records the feedback received so far and where the report applies it. Instructor answers that arrive later "
                  "will be added here and in the Feedback Log sheet of the Team Workbook.")

FEEDBACK_ROWS = [
    ["Presentation 1", "The instructor approved the team’s request to move from Tier 3 to Tier 4 (live sandbox payment, interactive Admin dashboard, automated end-to-end tests).",
     "Cover table and Abstract set to Tier 4; Section 1.1 technology tier rewritten; FR22 updated; FR36, FR37 (1.3) and NFR7 (1.4) added; Tier 4 parts designed in 2.3.1 (Figure 2.4), 2.4, 2.5 and 2.6; Team Workbook (Team & Tier, Requirements, RTM, Tier Checklist) updated.", "Yes"],
    ["Presentation 1", "Assumptions A-01 (shipper assignment), A-02 (money after a Failed delivery) and A-06 (load rounding) were raised for confirmation.",
     "Assumptions kept as written and used consistently in the design (state diagram, UC1 and UC2 specifications, UI). The written answer will be recorded in 1.5.", "Open"],
    ["Part 1 marking", "Not yet received.", "–", "–"],
    ["Presentation 2", "Not yet held.", "–", "–"],
    ["Part 2 marking", "Not yet received.", "–", "–"],
]

TIER_PARAGRAPH = ("Technology tier. The team targets Tier 4 (maximum 10/10), confirmed by the instructor at Presentation 1: ASP.NET Core MVC "
                  "with Entity Framework Core Code First and migrations, SQL Server and Bootstrap 5, plus all three Tier 4 obligations – "
                  "(a) a live PayPal Developer sandbox integration (FR36), (b) an interactive Admin dashboard (FR37) and (c) automated "
                  "end-to-end tests of the core workflows with Playwright (NFR7). The extensions reuse designed extension points: the "
                  "sandbox is one more payment Strategy class, the dashboard reuses the R1 and R2 queries, and the Playwright suite follows "
                  "the Part 1 test plan. The Tier 3 scope is built first; the team understands that the mark stays within the Tier 3 cap "
                  "if any Tier 4 part is incomplete. Owners: (a) Lê Xuân Khánh, (b) Ngô Bình Minh, (c) both members.")

FR22_OLD = "(simulated in Tier 3)"
FR22_NEW = "(MoMo, VNPay and Apple Pay simulated; PayPal live in the sandbox – FR36)"

NEW_FRS = [
    ["FR36", "The system shall process PayPal payments of Foreign Tourists through the live PayPal Developer sandbox (Orders v2: create, buyer approval, capture), store the PayPal order and capture IDs on the payment record, and refund a cancelled paid order through the sandbox.", "UC1", "BR13, BR16", "–"],
    ["FR37", "The system shall give System Admins an interactive dashboard with today’s orders, revenue, average preparation time and Quiet Kitchen share, live hub load, orders by state and payment mix, date-range and hub filters, and the heavy-rain switch.", "UC2 + ADM", "BR5, BR7, BR8", "R1, R2"],
]
NEW_NFR = ["NFR7", "Testability (Tier 4)", "Automated Playwright end-to-end tests shall cover the core workflows – a Local order with COD, a Tourist order paid in the PayPal sandbox, kitchen and shipper transitions, one rejected invalid transition, and reports R1 and R2 – run headless with one command, and pass 100% on the release build.",
           "Run dotnet test --filter Category=E2E on the release build; keep the HTML report and Playwright traces as Part 3 evidence; any failure blocks the tagged release."]

ASSUMPTION_ANSWERS = {
    "A-01": "Raised at Presentation 1 – kept; written answer pending",
    "A-02": "Raised at Presentation 1 – kept; written answer pending",
    "A-06": "Raised at Presentation 1 – kept; written answer pending",
}
ASSUMPTION_DEFAULT = "Listed at Presentation 1 – kept"

# ----------------------------------------------------------------------------------------------- Part 2
P2_INTRO = ("Part 2 turns the requirements into a design that the team will implement in Part 3. Every artefact keeps the requirement "
            "IDs of Part 1 so that the RTM can link each FR and NFR to a design element. Diagram sources (Python generators, SVG and "
            "PNG files) and the UI prototype are versioned in the GitHub repository; the large diagrams are placed on landscape pages "
            "so that they stay readable when printed.")

UC_OVERVIEW = ("Figure 2.1 shows the system boundary with all actors and use cases. Local Customer and Foreign Tourist specialise the "
               "abstract Customer actor (actor generalisation, BR18): both inherit the association with UC1 and the shared use cases, while "
               "registration and payment options differ. Kitchen Staff and Shipper move orders along the lifecycle, and the System Admin "
               "owns UC2 and the supporting administration use cases. «include» relationships show behaviour that UC1 always performs "
               "(pricing, payment selection) and UC2 always performs (reading the hub load). The PayPal Sandbox is an external system "
               "actor linked to the Tier 4 «extend» use case, which only runs when a tourist selects PayPal.")

UC1_SPEC = {
    "name": "UC1 – Place and Manage Orders (CRUD: place, view and track, edit while Placed, cancel)",
    "actors": "Primary: Customer (Local Customer, Foreign Tourist). Secondary: Kitchen Staff (rejects a Placed order), System Admin (cancels a Confirmed order), PayPal Sandbox (Tier 4).",
    "ids": "FR7–FR23, FR27, FR34–FR36 · BR1–BR17 · NFR1, NFR2, NFR4, NFR5, NFR6 · A-04, A-08",
    "pre": ["The customer is signed in with an active account (FR2–FR4).", "The cart holds items of one active hub; the delivery address and its distance are known (FR34)."],
    "main": [
        "1. Customer opens a hub menu and adds Available items (1–20 per line, at most 30 lines).",
        "2. Customer opens checkout, confirms the address, optionally enters one voucher and chooses a payment method.",
        "3. System reads the hub load (Confirmed + Preparing ÷ capacity, unrounded) and checks that it is below 90% (BR8, FR7).",
        "4. System validates S ≥ 50,000 (BR1), distance ≤ 8.0 km (BR2) and the lines (BR12).",
        "5. System prices the order in the BR10 order – Q (BR7), V (BR9), F, D with the free-delivery waiver (BR3, BR6), R (BR4), R2 (BR5) – rounds once (BR11) and shows every line.",
        "6. System offers only the methods of the customer’s group (BR13) and allows COD only for a total ≤ 1,000,000 (BR14).",
        "7. Customer confirms. System stores the order as Placed with its lines, price snapshot (time, load, rain flag – BR17), payment record and first history row in one transaction (NFR5, NFR6).",
        "8. System runs the payment strategy: COD → Pending; MoMo, VNPay, Apple Pay → simulated Paid; PayPal → sandbox approval (Tier 4, Figure 2.4).",
        "9. System shows the confirmation and the tracking page; the customer can list own orders and open one to see status history, lines, discounts, fees, total and payment status (FR27).",
    ],
    "alt": [
        "A1 Hub at or above 90%: the system lists active hubs below 90% within 8 km; the customer picks one; the cart keeps only items that hub serves (A-04); continue at step 4.",
        "A2 Voucher inactive, expired or below its minimum subtotal: the voucher is refused with the reason and the order is priced without it (BR9).",
        "A3 Edit (Update) while Placed: the system re-prices from the stored snapshot (BR17) and re-checks BR1, BR12 and BR14 (A-08); if COD is no longer allowed, another method must be chosen before saving.",
        "A4 Cancel (Delete) while Placed or Confirmed: the order becomes Cancelled with a history row; an online-paid order receives a full refund (BR16). The record is kept for history and reports.",
        "A5 Tourist chooses PayPal: redirect to the PayPal sandbox; on return the payment is captured and stored (FR36).",
    ],
    "exc": [
        "E1 BR1, BR2 or BR12 violated: no order is created and the message names the failed rule.",
        "E2 Method of the other group, or COD above 1,000,000: rejected (BR13, BR14).",
        "E3 Payment fails or PayPal is declined: the transaction is rolled back or the order cancelled; nothing is charged (NFR5).",
        "E4 Cancel requested after Confirmed: rejected by the state machine (BR15, BR16).",
        "E5 A customer requests another customer’s order: HTTP 403 (FR35, NFR4).",
    ],
    "post": [
        "Success: exactly one Placed order with 1–30 lines, a rounded total equal to the BR10 calculation, an immutable snapshot, a payment record (Pending or Paid) and one history row; hub load changes only when the kitchen confirms.",
        "Cancel: order Cancelled with a history row and, if paid online, a refund record.",
        "Failure: no order, line, payment or history row is stored.",
    ],
}

UC2_SPEC = {
    "name": "UC2 – Manage Hubs & Capacity (CRUD: create, view with live load, edit, deactivate)",
    "actors": "Primary: System Admin. Affected: Customer (sees hub status and Quiet Kitchen discount), Kitchen Staff (works within the hub capacity).",
    "ids": "FR5, FR6, FR7, FR15, FR24, FR26, FR28, FR37 · BR7, BR8, BR12, BR15 · NFR3, NFR4 · A-04, A-06, A-07",
    "pre": ["The user is signed in with the Admin role (NFR4).", "Brands to be assigned exist and are active (FR28)."],
    "main": [
        "1. Admin opens Hubs & capacity and selects New hub.",
        "2. Admin enters name, district, address, kitchen capacity and the brands the hub operates.",
        "3. System validates the fields: capacity is a positive whole number, at least one active brand.",
        "4. System stores the hub as Active with its HubBrands and returns to the list.",
        "5. System lists all hubs with capacity, active-order count, load % (Confirmed + Preparing ÷ capacity, unrounded – A-06) and band: Quiet < 30%, Normal, Full ≥ 90%; inactive hubs are labelled Inactive.",
        "6. Admin opens a hub to edit capacity, brands or status; the system validates and saves; the load is recomputed with the new capacity.",
        "7. Admin selects Deactivate; the system counts orders in Placed, Confirmed, Preparing, Ready and Out for Delivery; with none it sets IsActive = false (soft-delete).",
    ],
    "alt": [
        "A1 Capacity reduced below the active-order count: the load can exceed 90%; the hub shows Full and refuses new orders (BR8) until the load drops.",
        "A2 Reactivate an inactive hub: IsActive = true; it appears to customers again.",
        "A3 Remove a brand from a hub: existing orders are unaffected; new orders at this hub can no longer contain that brand’s items (BR12).",
    ],
    "exc": [
        "E1 Capacity 0, negative, decimal or text: field error, nothing saved.",
        "E2 Deactivate while active orders exist: blocked with the count of active orders (A-07).",
        "E3 A non-admin calls an admin route: HTTP 403 (NFR4).",
    ],
    "post": [
        "Create: a new Active hub is offered to customers within 8 km.",
        "Update: the new capacity and brands are used immediately by load, Quiet Kitchen discount and protection rules (BR7, BR8).",
        "Deactivate: the hub takes no new orders but stays in order history and in R2 (FR24, FR26).",
        "The load shown always equals (Confirmed + Preparing) ÷ capacity at the time of the request.",
    ],
}

SEQ_TEXT_UC1 = ("UC1 is shown in two parts joined by a ref fragment. Part 1 (Figure 2.2) checks the hub load and asks PricingService "
                "for the quote; part 2 (Figure 2.3) resolves the payment strategy and stores everything in one transaction. Figure 2.4 "
                "details the Tier 4 PayPal sandbox flow: only PayPalSandboxStrategy talks to PayPal, so no other class changes when the "
                "live API is added.")
SEQ_TEXT_UC2 = ("UC2 is shown in two parts. Figure 2.5 covers Create and Read (listing hubs with their computed load); Figure 2.6 covers "
                "Update and Delete, where deactivation is refused while the hub still has active orders (A-07).")
STATE_TEXT = ("The team state diagram (Figure 2.7) matches Section C of the specification: 8 states, the allowed transitions, the actor "
              "who may trigger each one and the guard conditions. The diagram is implemented as a transition table inside "
              "OrderStateMachine, which is the only class allowed to change Order.Status. It writes an OrderStatusHistory row for every "
              "accepted transition (NFR6) and rejects any other transition with an error, independent of the UI (BR15). The 15 invalid "
              "transitions planned in the workbook (S-01…S-15) test this table.")

CRC_INTRO = ("The CRC cards were written before the class diagrams to agree how responsibilities are split. Controllers only coordinate; "
             "services own the rules; entities hold data and simple invariants.")
CRC = [
    ["CheckoutController", "Receive the checkout form; ask OrderService to place the order; show the price breakdown and the allowed payment methods; redirect to tracking or to PayPal approval.", "IOrderService, IPaymentStrategyResolver, Razor views"],
    ["OrderService", "Coordinate place, edit and cancel; run each operation in one transaction; ask for load, price and payment; let the state machine record history.", "IHubLoadService, IPricingService, IPaymentStrategyResolver, IOrderStateMachine, SaigonBiteDbContext"],
    ["PricingService", "Validate BR1, BR2, BR12; compute S, Q, V, F, D, R, R2 in the BR10 order; round once (BR11); re-price from a snapshot.", "IClock, Voucher, PriceRequest, PriceBreakdown"],
    ["HubLoadService", "Count Confirmed + Preparing orders; return the unrounded load; decide whether a hub can accept; find alternative hubs within 8 km.", "SaigonBiteDbContext, Hub"],
    ["OrderStateMachine", "Hold the allowed transitions (from, to, roles, guard); reject all others; append OrderStatusHistory.", "Order, OrderStatusHistory, current user role"],
    ["PaymentStrategyResolver", "Know the registered strategies; list the methods of a customer type; resolve one strategy; refuse a method of the other group.", "IPaymentStrategy (5 implementations)"],
    ["MoMo / VnPay / CashOnDelivery / ApplePay / PayPalSandbox Strategy", "Pay and refund with one method; COD stays Pending until the shipper confirms cash; PayPal creates, captures and refunds through the sandbox.", "Payment, PayPalClient (PayPal only)"],
    ["HubService (UC2)", "Create, update, list and deactivate hubs; validate capacity; block deactivation while orders are active.", "SaigonBiteDbContext, IHubLoadService"],
    ["ReportService", "Build R1 (revenue by brand category and payment method, Cancelled and Failed excluded) and R2 (orders, average preparation time, load, Quiet Kitchen discounts).", "SaigonBiteDbContext, OrderStatusHistory"],
    ["DashboardService (Tier 4)", "Provide today’s KPIs, live hub load, orders by state, payment mix and the heavy-rain switch for the dashboard.", "ReportService, IHubLoadService, SystemSetting"],
    ["Order (entity)", "Hold status, lines, price snapshot, price breakdown and payment; belong to one customer and one hub.", "OrderLine, PriceSnapshot, PriceBreakdown, Payment, OrderStatusHistory"],
    ["Hub (entity)", "Hold capacity, operated brands and the active flag; compute the load from an active-order count.", "Brand, Order, KitchenStaff"],
]

CLASS_TEXT = ("The class design is split into four diagrams so that each stays readable. Figure 2.8 shows how Local Customers and Foreign "
              "Tourists share one user schema; Figure 2.9 the ordering model with the value objects that freeze the price; Figure 2.10 "
              "the business services behind interfaces; Figure 2.11 the payment Strategy pattern – one interface, one class per method, "
              "and a resolver that selects strategies by customer type (BR13).")

DB_NOTES = [
    ["One schema for both customer types", "EF Core table-per-type mapping: one Users table (login, salted PBKDF2 hash, role, customer type) and one profile table per type – LocalCustomerProfiles (phone, OTP verification) and TouristProfiles (passport, nationality, email verification). Unique indexes on Email, PhoneNumber and PassportNumber enforce BR18."],
    ["Soft-delete for referenced data", "Hubs, Brands, MenuItems, Users and Vouchers are never deleted once an order refers to them. IsActive / IsDeleted flags hide them from new orders through global query filters, while reports read them with IgnoreQueryFilters so R1 and R2 stay correct (FR24, A-07)."],
    ["Reproducible prices", "Each order stores its snapshot (Vietnam-time placement, hub load, rain flag – BR17) and its full breakdown S, Q, V, D, R, R2 and Total; OrderLines copy the unit price at placement, so later menu or rule changes never alter an existing order."],
    ["Audit and concurrency", "OrderStatusHistory is append-only (no update or delete path in the code; NFR6). Orders carry a RowVersion so two staff members cannot move the same order at once; every operation runs in one transaction (NFR5)."],
    ["Load and reporting indexes", "Index Orders(HubId, Status) keeps the load count fast for every checkout; Orders(PlacedAtLocal) and OrderStatusHistory(OrderId, ToStatus) serve R1, R2 and the dashboard."],
    ["Money and time", "Amounts are decimal(12,0) VND; the PayPal sandbox receives USD at a fixed demo rate shown to the tourist. Business times use IClock in UTC+7; technical timestamps are stored in UTC."],
]

ARCH_TEXT = ("SaigonBite uses ASP.NET Core MVC in three layers (Figure 2.14). The Presentation layer contains Razor views with the "
             "Bootstrap 5 grid, controllers and view models; it handles HTTP, authorisation attributes and rendering only. The Business "
             "layer contains the services that implement BR1–BR18. The Data layer contains the EF Core DbContext, migrations and SQL "
             "Server. Figure 2.15 follows one “place order” request through the layers, and Figure 2.16 shows the pricing pipeline that "
             "PricingService implements.")

PRINCIPLES = [
    ["Separation of concerns", "Controllers (CheckoutController, Admin/HubsController) bind input and choose a view; services decide; SaigonBiteDbContext persists. The PayPal REST client is hidden inside PayPalSandboxStrategy, so no controller knows about PayPal."],
    ["High cohesion, low coupling", "Each service has one job: PricingService prices, HubLoadService measures load, OrderStateMachine changes status, ReportService builds R1 and R2. Classes depend on small interfaces registered in the DI container, never on concrete classes of other layers."],
    ["SOLID (S, O, L, I, D)", "S – PricingService and OrderStateMachine each change for one reason. O – a new payment method is a new IPaymentStrategy class plus one DI line, ready for the Week 5 Change Request. L – every strategy honours the Pay/Refund contract (COD returns Pending). I – IPricingService, IHubLoadService, IOrderStateMachine and IPaymentStrategyResolver instead of one large service. D – OrderService and controllers depend on abstractions; IClock is injected so tests can fix the time."],
    ["Location of the pricing rules (BR1 to BR14)", "Only in PricingService (SaigonBite.Business), called by OrderService when an order is placed or edited. Views and controllers never compute money. Reason: one place to unit-test every threshold with EP/BVA, prices reproducible from the snapshot, and rule changes stay local."],
    ["Link to NFRs", "NFR1 – pricing is pure in-memory calculation over at most 30 lines. NFR2 – Strategy pattern and a single pricing service. NFR3 – Bootstrap grid and EN/VI resources. NFR4 – ASP.NET Core Identity (PBKDF2), [Authorize(Roles)] and ownership checks in services. NFR5 – one transaction per operation plus RowVersion. NFR6 – OrderStateMachine is the only writer of status and history. NFR7 – Playwright suite in the test project."],
]

TIER4_TEXT = [
    ("(a) Live PayPal sandbox (FR36, owner Lê Xuân Khánh). ", "PayPalSandboxStrategy uses the PayPal REST API with OAuth2 client credentials: create order (intent CAPTURE), redirect the tourist to approve, capture on return, and refund a cancelled paid order. Client ID and secret live in user secrets, never in Git. The existing strategies are not edited."),
    ("(b) Interactive Admin dashboard (FR37, owner Ngô Bình Minh). ", "DashboardService reuses the R1 and R2 queries and adds today’s KPIs, orders by state and live hub load; the page uses Chart.js with date and hub filters and hosts the heavy-rain switch (Figure 2.26)."),
    ("(c) Playwright end-to-end tests (NFR7, both members). ", "A separate test project drives the running app headless: Local order with COD, Tourist order through the PayPal sandbox buyer, kitchen and shipper transitions, one invalid transition rejected, and R1/R2 pages; traces and the HTML report are kept as evidence."),
]

UI_TEXT = ("The UI was designed in four stages – sketch, wireframe, high-fidelity mock-up and interactive prototype (Figure 2.17) – on a "
           "responsive Bootstrap 5 grid. Customer screens are shown in Vietnamese for a Local Customer and in English for a Foreign "
           "Tourist to demonstrate the EN/VI toggle (NFR3). The mock-ups use real dishes and the exact worked examples of the "
           "specification, so the checkout totals in the prototype match the pricing rules: 205,000 ₫ for the Local order (Figure "
           "2.20) and 269,000 ₫ for the Tourist order with voucher, rain surcharge and free delivery (Figure 2.21). The prototype opens on "
           "a landing page built around real night photographs of Ho Chi Minh City (Figure 2.32): a slow Ken Burns zoom on the hero, "
           "counting statistics, scroll-triggered reveals, a moving dish carousel and animated hub-load bars; a 19-second screen "
           "recording (design/ui/out/landing_motion.mp4) shows the motion, which a static PDF cannot.")

UI_MAP = [
    ["Hub selection with load bands, menu and brand browsing", "FR6, FR7, FR8, BR2, BR7, BR8, BR12", "Figures 2.18, 2.19"],
    ["Checkout with price breakdown and the five payment buttons", "FR9–FR19, BR10, BR11, BR13, BR14", "Figures 2.20, 2.21"],
    ["PayPal sandbox confirmation (Tier 4)", "FR36", "Figure 2.22"],
    ["Order tracking with status history and snapshot", "FR20, FR21, FR22, FR27", "Figure 2.23"],
    ["Registration for Local Customer and Foreign Tourist", "FR1–FR4, BR18", "Figure 2.24"],
    ["Kitchen board and shipper screen", "FR20, FR33, BR14, BR15, A-01", "Figures 2.25, 2.29"],
    ["Admin dashboard (Tier 4)", "FR37", "Figure 2.26"],
    ["UC2 hub list and hub edit / deactivate", "FR5, FR6, FR24, A-07", "Figures 2.27, 2.28"],
    ["Reports R1 and R2", "FR25, FR26", "Figures 2.30, 2.31"],
    ["Landing page with motion and sign-in (entry of the prototype)", "FR2–FR4, NFR3, BR7 (Quiet Kitchen message)", "Figures 2.32, 2.33"],
]

EXTRA_REFS = [
    "8. Microsoft, ASP.NET Core MVC and Entity Framework Core documentation, learn.microsoft.com, accessed November 2026.",
    "9. PayPal, PayPal REST APIs – Orders v2 and sandbox testing guide, developer.paypal.com, accessed November 2026.",
    "10. Microsoft, Playwright for .NET documentation, playwright.dev/dotnet, accessed November 2026.",
    "11. E. Gamma, R. Helm, R. Johnson and J. Vlissides, Design Patterns: Elements of Reusable Object-Oriented Software. Addison-Wesley, 1994 (Strategy pattern).",
    "12. Photographs of dishes and Ho Chi Minh City used in the prototype: Wikimedia Commons contributors, free licences (CC BY, CC BY-SA, public domain); full list in design/credits/IMAGE_CREDITS.md of the repository.",
]

# Appendix B – Generative AI usage for Part 2. The team must check these rows against what it really did before submitting.
AI_ROWS = [
    ["Claude (Anthropic), 20 Nov 2026", "Part 2 UML diagrams",
     "Generate use case, sequence, state, class and ER diagrams from our FR list, BR1–BR18 and the Part 1 assumptions",
     "Kept the structure; messages, guards and multiplicities checked against the specification",
     "Compared with BR1–BR18, Section C of the specification and the Part 1 FR table; each rendered diagram reviewed"],
    ["Claude (Anthropic), 20 Nov 2026", "UI prototype and Figma import plugin",
     "Build Bootstrap screens with openly licensed photos and the specification worked examples; script that assembles the Figma file",
     "Kept the screens; totals recalculated by hand (205,000 ₫ and 269,000 ₫); image credits listed in the repository",
     "Recalculated prices with BR10 and BR11; layouts checked at 390 px and 1440 px"],
    ["Claude (Anthropic), 20 Nov 2026", "Report v2.0 and Design Review slides",
     "Draft Part 2 text, use case specifications, CRC cards, database notes and the Presentation 2 slides",
     "Draft used as the starting point; wording and decisions reviewed by both members",
     "Read against the Part 2 checklist and rubric; IDs cross-checked with the Team Workbook"],
]

# ----------------------------------------------------------------------------------------------- Part 1 resubmission (v1.1)
ABSTRACT_P1 = ("SaigonBite is a delivery-only cloud-kitchen network in Ho Chi Minh City. This Part 1 report, version 1.1, turns business "
               "rules BR1–BR18 into a traceable requirements baseline: 37 functional requirements with IDs mapped to the two owned use "
               "cases (UC1 Place and Manage Orders, UC2 Manage Hubs & Capacity), the supporting functions and the two reports, 7 "
               "measurable quality attributes and 8 documented assumptions. Version 1.1 applies the instructor’s approval at "
               "Presentation 1: the team now targets Tier 4 – a live PayPal Developer sandbox (FR36), an interactive Admin dashboard "
               "(FR37) and Playwright end-to-end tests (NFR7) – on ASP.NET Core MVC, Entity Framework Core, SQL Server and Bootstrap.")

FEEDBACK_ROWS_P1 = [
    ["Presentation 1", "The instructor approved the team’s request to move from Tier 3 to Tier 4 (live sandbox payment, interactive Admin dashboard, automated end-to-end tests).",
     "Cover table and Abstract set to Tier 4; Section 1.1 technology tier rewritten; FR22 updated; FR36, FR37 (1.3) and NFR7 (1.4) added; Team Workbook (Team & Tier, Requirements, RTM, Tier Checklist, Feedback Log) and Marking Sheet updated.", "Yes"],
    ["Presentation 1", "Assumptions A-01 (shipper assignment), A-02 (money after a Failed delivery) and A-06 (load rounding) were raised for confirmation.",
     "Assumptions kept as written; the written answer will be recorded in 1.5 and in the Team Workbook.", "Open"],
    ["Part 1 marking", "Not yet received.", "–", "–"],
    ["Presentation 2", "Not yet held.", "–", "–"],
    ["Part 2 marking", "Not yet received.", "–", "–"],
]

AI_ROWS_P1 = [
    ["Claude (Anthropic), 20 Nov 2026", "Tier 4 revision of the Part 1 documents",
     "Update cover, Section 1.1, FR22, FR36, FR37, NFR7, the Feedback Log and the Team Workbook after the Tier 4 approval",
     "Kept all existing IDs and wording; only tier-related text and the three new requirements were added",
     "Cross-checked the new IDs between the report, the Team Workbook and the Marking Sheet"],
]
