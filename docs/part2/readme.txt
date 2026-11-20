SaigonBite – Team G7 – Part 2: Software Design, Architecture & UI/UX
Introduction to Software Engineering – Sem01_2627 – Instructor: Pham Thai Ky Trung
Technology tier: Tier 4 (approved at Presentation 1)
ASP.NET Core MVC (Code First) + Entity Framework Core + SQL Server + Bootstrap 5
+ (a) live PayPal Developer sandbox, (b) interactive Admin dashboard, (c) Playwright end-to-end tests

------------------------------------------------------------------------
FIGMA (public, anyone with the link can view)
------------------------------------------------------------------------
Clickable prototype – opens in Present mode at flow 1 (the landing page):
https://www.figma.com/proto/ADppt5rvGp5uS6E7Bb8X7G/SaigonBite-%E2%80%93-Team-G7-%E2%80%93-Part-2-UI-UX?node-id=2-603&p=f&scaling=scale-down-width&content-scaling=fixed&page-id=2%3A104&starting-point-node-id=2%3A603&show-proto-sidebar=1

Design file – all pages:
https://www.figma.com/design/ADppt5rvGp5uS6E7Bb8X7G/SaigonBite-%E2%80%93-Team-G7-%E2%80%93-Part-2-UI-UX

How to view: open the prototype link. The three flows are listed in the left panel;
click a flow, then click the buttons on the screen (hot-spots) to move through it:
  1  Local customer – landing -> sign in -> choose a hub -> menu -> checkout (cash, 205,000 VND) -> tracking  (UC1)
  2  Foreign tourist – checkout -> PayPal sandbox payment (269,000 VND) -> tracking  (UC1, Tier 4 a)
  3  Admin – dashboard (Tier 4 b) -> hubs and capacity (UC2) -> Revenue R1 -> Hub Utilization R2
Pages in the design file: "00 · Cover & design system" (brand), "01–04 · Sketch → Wireframe → Mock-up"
(one section per stage: 01 Sketch, 02 Wireframe, 03 Mock-up desktop, 04 Mock-up mobile 390 px)
and "05 · Prototype (stage 4)" (16 screens, 49 click links).

------------------------------------------------------------------------
GITHUB REPOSITORY
------------------------------------------------------------------------
https://github.com/bminhnemhoi/saigonbite-g7
Contains the design sources (UML generators, SVG/PNG diagrams, Bootstrap prototype, Figma
builder, brand assets) and, from Part 3, the source code. Collaborators: bminhnemhoi, khanhle1406.

------------------------------------------------------------------------
USE CASE OWNERSHIP
------------------------------------------------------------------------
UC1  Place and Manage Orders (required use case D, full CRUD)
     Owner: Le Xuan Khanh – 524H0055
     Also: shared pricing and payment module BR1–BR14, Revenue Report R1,
           Manage Deliveries (supporting F), Tier 4 (a) PayPal sandbox (FR36)

UC2  Manage Hubs & Capacity (use case B, full CRUD)
     Owner: Ngo Binh Minh – 524H0169
     Also: Hub Utilization Report R2, user accounts (E), menu & brands (A), vouchers (C),
           heavy-rain flag, Tier 4 (b) interactive Admin dashboard (FR37)

Tier 4 (c) Playwright end-to-end tests (NFR7): both members

------------------------------------------------------------------------
FILES IN THIS SUBMISSION
------------------------------------------------------------------------
TeamG7_Part2_Design.pdf          Report v2.0 with bookmarks: Part 1 updated for Tier 4 (Feedback Log,
                                 FR36, FR37, NFR7) and Part 2 (use case diagram, UC1/UC2 specifications,
                                 sequence and state diagrams, CRC cards, class diagrams with the Strategy
                                 pattern, ERD and database notes, architecture and quality design,
                                 UI/UX design with screenshots)
TeamG7_Part2_Presentation.pptx   Design Review slides (7–10 minutes) with speaker notes
readme.txt                       This file

Shared on Google Drive as well: the updated Team Workbook (G7_SE_Sem01_2627_Team_Workbook.xlsx)
and a 19-second recording of the animated landing page (SaigonBite_landing_motion.mp4).
Photographs: Wikimedia Commons, free licences – full credits in design/credits/IMAGE_CREDITS.md.
