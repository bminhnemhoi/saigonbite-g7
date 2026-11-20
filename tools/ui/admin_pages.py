"""Generates the admin screens (10–14) of the prototype with one shared sidebar and head.
Usage: python admin_pages.py <ui_dir>"""
import pathlib
import sys

UI = pathlib.Path(sys.argv[1])
HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SaigonBite Admin – {title}</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/@fontsource/be-vietnam-pro@5.0.8/400.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/@fontsource/be-vietnam-pro@5.0.8/600.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/@fontsource/be-vietnam-pro@5.0.8/700.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/@fontsource/be-vietnam-pro@5.0.8/800.css" rel="stylesheet">
<link href="../assets/app.css" rel="stylesheet"><script src="../assets/mode.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>{css}</style></head><body>
"""
NAV = [("Operations", [("10-admin-dashboard", "bi-speedometer2", "Dashboard", True), ("11-admin-hubs", "bi-shop", "Hubs &amp; capacity", False),
                       ("", "bi-receipt", "Orders", False), ("", "bi-bicycle", "Shipper assignment", False)]),
       ("Catalogue", [("", "bi-collection", "Brands &amp; menu", False), ("", "bi-ticket-perforated", "Vouchers", False)]),
       ("Reports", [("13-report-r1", "bi-graph-up-arrow", "Revenue (R1)", False), ("14-report-r2", "bi-bar-chart-line", "Hub utilization (R2)", False)]),
       ("System", [("", "bi-people", "Users", False), ("", "bi-cloud-rain", "Heavy-rain flag", False)])]


def side(active):
    out = ['<aside class="side"><div class="sb-logo"><img class="mk" src="../assets/brand/mark.svg" alt="SaigonBite"><div>Saigon<span>Bite</span></div></div>']
    for grp, items in NAV:
        out.append(f'<div class="grp">{grp}</div>')
        for target, icon, label, t4 in items:
            on = ' class="on"' if target == active else ""
            goto = f' data-goto="{target}"' if target else ""
            badge = '<span class="t4">TIER 4</span>' if t4 else ""
            out.append(f'<a{on}{goto}><i class="bi {icon}"></i>{label}{badge}</a>')
    out.append('<div style="position:absolute;bottom:20px;left:16px;right:16px" class="d-flex align-items-center gap-2 p-2 rounded-3" >'
               '<div class="sb-avatar" style="width:36px;height:36px;font-size:13px;background:#E4572E">HP</div>'
               '<div style="line-height:1.2"><div class="text-white fw-semibold small">Nguyễn Hoàng Phúc</div><div class="small" style="color:#8FA3B7">System Admin</div></div></div></aside>')
    return "\n".join(out)


def top(title, sub, right=""):
    return (f'<div class="topbar"><div><h1>{title}</h1><div class="small text-slate">{sub}</div></div>'
            f'<div class="ms-auto d-flex align-items-center gap-3">{right}<div class="sb-lang"><span>VI</span><span class="on">EN</span></div>'
            '<div class="sb-icon-btn"><i class="bi bi-bell"></i><span class="sb-badge">3</span></div></div></div>')


CHART_DEFAULTS = """<script>Chart.defaults.font.family='"Be Vietnam Pro","Segoe UI",sans-serif';Chart.defaults.font.size=13;Chart.defaults.color='#5B6B7A';
Chart.defaults.plugins.legend.labels.boxWidth=12;Chart.defaults.plugins.legend.labels.boxHeight=12;Chart.defaults.animation=false;</script>"""


def page(fname, title, active, css, body, scripts=""):
    html = HEAD.format(title=title, css=css) + side(active) + '<div class="main">' + body + "</div>" + CHART_DEFAULTS + scripts + "</body></html>"
    (UI / "screens" / f"{fname}.html").write_text(html, encoding="utf-8")
    print("wrote", fname)


# ------------------------------------------------------------------ 10 dashboard (Tier 4)
dash = top("Operations dashboard", "Thursday 19 Nov 2026 · live at 15:06 (Vietnam time)",
           '<select class="form-select form-select-sm" style="width:150px"><option>Today</option></select>'
           '<select class="form-select form-select-sm" style="width:150px"><option>All hubs</option></select>') + """
<div class="p-4">
 <div class="row g-3 mb-3">
  <div class="col-3"><div class="cardx kpi d-flex justify-content-between"><div><div class="lbl">Orders today</div><div class="val">126</div><div class="dl text-success"><i class="bi bi-arrow-up"></i> 12% vs last Thu</div></div><div class="ic" style="background:#FFF1EC;color:#E4572E"><i class="bi bi-receipt"></i></div></div></div>
  <div class="col-3"><div class="cardx kpi d-flex justify-content-between"><div><div class="lbl">Revenue today</div><div class="val">12.8M ₫</div><div class="dl text-success"><i class="bi bi-arrow-up"></i> 8% vs last Thu</div></div><div class="ic" style="background:#E8F5EE;color:#1E8A5F"><i class="bi bi-cash-stack"></i></div></div></div>
  <div class="col-3"><div class="cardx kpi d-flex justify-content-between"><div><div class="lbl">Avg prep time</div><div class="val">14.9 min</div><div class="dl text-slate">Confirmed → Ready</div></div><div class="ic" style="background:#EAF3FB;color:#2E7DAF"><i class="bi bi-stopwatch"></i></div></div></div>
  <div class="col-3"><div class="cardx kpi d-flex justify-content-between"><div><div class="lbl">Quiet-kitchen orders</div><div class="val">18%</div><div class="dl" style="color:#9A6412">23 of 126 orders</div></div><div class="ic" style="background:#FFF8E6;color:#C98A1E"><i class="bi bi-arrow-down-circle"></i></div></div></div>
 </div>
 <div class="row g-3 mb-3">
  <div class="col-8"><div class="cardx p-4"><div class="d-flex justify-content-between mb-2"><h2 class="section-title" style="font-size:17px">Revenue, last 14 days</h2><span class="text-slate small">million ₫ · Cancelled and Failed excluded</span></div><canvas id="rev" height="112"></canvas></div></div>
  <div class="col-4"><div class="cardx p-4 h-100"><h2 class="section-title mb-3" style="font-size:17px">Live hub load</h2>
   <div class="mb-3"><div class="d-flex justify-content-between small fw-semibold"><span>Hub D1 · Quận 1</span><span class="text-danger">92% · full</span></div><div class="loadbar mt-1"><i class="lb-red" style="width:92%"></i></div></div>
   <div class="mb-3"><div class="d-flex justify-content-between small fw-semibold"><span>Hub Q7 · Phú Mỹ Hưng</span><span style="color:#9A6412">56%</span></div><div class="loadbar mt-1"><i class="lb-amber" style="width:56%"></i></div></div>
   <div class="mb-3"><div class="d-flex justify-content-between small fw-semibold"><span>Hub BT · Bình Thạnh</span><span style="color:#9A6412">47%</span></div><div class="loadbar mt-1"><i class="lb-amber" style="width:47%"></i></div></div>
   <div class="mb-3"><div class="d-flex justify-content-between small fw-semibold"><span>Hub TD · Thủ Đức</span><span class="text-success">20% · quiet</span></div><div class="loadbar mt-1"><i class="lb-green" style="width:20%"></i></div></div>
   <a class="small fw-semibold text-chili" data-goto="11-admin-hubs">Manage hubs <i class="bi bi-arrow-right"></i></a></div></div>
 </div>
 <div class="row g-3">
  <div class="col-4"><div class="cardx p-4 h-100"><h2 class="section-title mb-2" style="font-size:17px">Orders by state now</h2><canvas id="st" height="190"></canvas></div></div>
  <div class="col-4"><div class="cardx p-4 h-100"><h2 class="section-title mb-2" style="font-size:17px">Payment mix today</h2><canvas id="pm" height="190"></canvas></div></div>
  <div class="col-4"><div class="cardx p-4 h-100"><h2 class="section-title mb-3" style="font-size:17px">Heavy-rain flag</h2>
   <div class="d-flex align-items-center gap-3 p-3 rounded-3" style="background:#F5F7FA"><i class="bi bi-cloud-rain-heavy fs-2 text-slate"></i><div class="flex-grow-1"><b>Off</b><div class="small text-slate">New orders get +10,000 ₫ while it is on (BR5)</div></div><div class="switch"></div></div>
   <div class="small text-slate mt-3"><i class="bi bi-info-circle me-1"></i>Changing the flag only affects new orders – placed orders keep their snapshot (BR17).</div>
   <div class="d-flex gap-2 mt-3"><a class="btn btn-soft btn-sm flex-grow-1" data-goto="13-report-r1">Revenue R1</a><a class="btn btn-soft btn-sm flex-grow-1" data-goto="14-report-r2">Utilization R2</a></div></div></div>
 </div>
</div>"""
dash_js = """<script>
new Chart(document.getElementById('rev'),{type:'line',data:{labels:['6','7','8','9','10','11','12','13','14','15','16','17','18','19 Nov'],
datasets:[{data:[9.1,10.4,11.8,12.6,9.7,10.2,10.9,11.3,13.9,14.6,10.8,11.5,12.1,12.8],borderColor:'#E4572E',backgroundColor:'rgba(228,87,46,.10)',fill:true,tension:.35,pointRadius:3,pointBackgroundColor:'#E4572E',borderWidth:2.5}]},
options:{plugins:{legend:{display:false}},scales:{y:{beginAtZero:false,grid:{color:'#EEF1F4'}},x:{grid:{display:false}}}}});
new Chart(document.getElementById('st'),{type:'bar',data:{labels:['Placed','Confirmed','Preparing','Ready','Out for delivery'],datasets:[{data:[6,9,14,4,11],backgroundColor:['#2E7DAF','#2E7DAF','#E4572E','#1E8A5F','#12263A'],borderRadius:6}]},
options:{indexAxis:'y',plugins:{legend:{display:false}},scales:{x:{grid:{color:'#EEF1F4'}},y:{grid:{display:false}}}}});
new Chart(document.getElementById('pm'),{type:'doughnut',data:{labels:['COD','MoMo','VNPay','PayPal','Apple Pay'],datasets:[{data:[39,33,21,19,14],backgroundColor:['#1E8A5F','#A50064','#005BAA','#003087','#5B6B7A'],borderWidth:2}]},
options:{cutout:'62%',plugins:{legend:{position:'right'}}}});
</script>"""
page("10-admin-dashboard", "Dashboard", "10-admin-dashboard", "", dash, dash_js)

# ------------------------------------------------------------------ 11 hubs list (UC2 read)
hubs = top("Hubs &amp; capacity", "UC2 · create, view, edit and deactivate hubs · load = (Confirmed + Preparing) ÷ capacity",
           '<a class="btn btn-primary btn-sm" data-goto="12-admin-hub-edit"><i class="bi bi-plus-lg me-1"></i>New hub</a>') + """
<div class="p-4">
 <div class="d-flex gap-2 mb-3"><span class="pill pill-green">Quiet &lt; 30% · 10% discount</span><span class="pill pill-amber">Normal 30–89%</span><span class="pill pill-red">Full ≥ 90% · no new orders</span><span class="ms-auto small text-slate">Load is compared unrounded (A-06)</span></div>
 <div class="cardx overflow-hidden">
 <table class="sb"><thead><tr><th>Hub</th><th>Brands</th><th>Capacity</th><th>Active</th><th style="width:240px">Current load</th><th>Status</th><th class="text-end">Actions</th></tr></thead><tbody>
 <tr><td><b>Hub D1 · Quận 1</b><div class="small text-slate">72 Lê Thánh Tôn, Bến Nghé</div></td><td><span class="pill pill-gray">PE</span> <span class="pill pill-gray">BC</span> <span class="pill pill-gray">GB</span></td><td>25</td><td>23</td><td><div class="d-flex align-items-center gap-2"><div class="loadbar flex-grow-1"><i class="lb-red" style="width:92%"></i></div><b class="text-danger">92%</b></div></td><td><span class="pill pill-red">Full</span></td><td class="text-end"><a class="btn btn-soft btn-sm" data-goto="12-admin-hub-edit">Edit</a></td></tr>
 <tr><td><b>Hub Q7 · Phú Mỹ Hưng</b><div class="small text-slate">23 Nguyễn Lương Bằng, Tân Phú</div></td><td><span class="pill pill-gray">PE</span> <span class="pill pill-gray">GB</span></td><td>18</td><td>10</td><td><div class="d-flex align-items-center gap-2"><div class="loadbar flex-grow-1"><i class="lb-amber" style="width:56%"></i></div><b style="color:#9A6412">56%</b></div></td><td><span class="pill pill-amber">Normal</span></td><td class="text-end"><a class="btn btn-soft btn-sm">Edit</a></td></tr>
 <tr><td><b>Hub BT · Bình Thạnh</b><div class="small text-slate">208 Điện Biên Phủ, P.17</div></td><td><span class="pill pill-gray">PE</span> <span class="pill pill-gray">BC</span></td><td>19</td><td>9</td><td><div class="d-flex align-items-center gap-2"><div class="loadbar flex-grow-1"><i class="lb-amber" style="width:47%"></i></div><b style="color:#9A6412">47%</b></div></td><td><span class="pill pill-amber">Normal</span></td><td class="text-end"><a class="btn btn-soft btn-sm">Edit</a></td></tr>
 <tr><td><b>Hub TD · Thủ Đức</b><div class="small text-slate">15 Võ Văn Ngân, Linh Chiểu</div></td><td><span class="pill pill-gray">PE</span> <span class="pill pill-gray">BC</span> <span class="pill pill-gray">GB</span></td><td>20</td><td>4</td><td><div class="d-flex align-items-center gap-2"><div class="loadbar flex-grow-1"><i class="lb-green" style="width:20%"></i></div><b class="text-success">20%</b></div></td><td><span class="pill pill-green">Quiet</span></td><td class="text-end"><a class="btn btn-soft btn-sm">Edit</a></td></tr>
 <tr style="background:#FAFBFC"><td><b class="text-mute">Hub GV · Gò Vấp</b><div class="small text-mute">Deactivated 02 Nov 2026 – kept for history and R2</div></td><td><span class="pill pill-gray">BC</span></td><td class="text-mute">15</td><td class="text-mute">0</td><td class="text-mute small">not accepting orders</td><td><span class="pill pill-gray">Inactive</span></td><td class="text-end"><a class="btn btn-soft btn-sm">Reactivate</a></td></tr>
 </tbody></table></div>
 <div class="row g-3 mt-1">
  <div class="col-6"><div class="cardx p-4 h-100 d-flex gap-3"><i class="bi bi-shield-check fs-3 text-success"></i><div><b>Protection rule (BR8)</b><div class="small text-slate">Hub D1 is at 92%, so customers see it as “Full” and are offered active hubs below 90% within 8 km (A-04).</div></div></div></div>
  <div class="col-6"><div class="cardx p-4 h-100 d-flex gap-3"><i class="bi bi-archive fs-3 text-slate"></i><div><b>Delete = deactivate (A-07)</b><div class="small text-slate">A hub can be deactivated only when it has no order in Placed … Out for Delivery. Its history stays in reports.</div></div></div></div>
 </div>
</div>"""
page("11-admin-hubs", "Hubs", "11-admin-hubs", "", hubs)

# ------------------------------------------------------------------ 12 hub edit + deactivate (UC2 create/update/delete)
edit = top("Edit hub · Hub D1 · Quận 1", "UC2 · update capacity and brands, or deactivate (soft-delete)",
           '<a class="btn btn-soft btn-sm" data-goto="11-admin-hubs"><i class="bi bi-arrow-left me-1"></i>Back to hubs</a>') + """
<div class="p-4"><div class="row g-4">
 <div class="col-7"><div class="cardx p-4">
  <div class="row g-3">
   <div class="col-6"><label class="form-label">Hub name</label><input class="form-control" value="Hub D1 · Quận 1"></div>
   <div class="col-6"><label class="form-label">District</label><select class="form-select"><option>Quận 1</option></select></div>
   <div class="col-12"><label class="form-label">Address</label><input class="form-control" value="72 Lê Thánh Tôn, Bến Nghé, Quận 1"></div>
   <div class="col-6"><label class="form-label">Kitchen capacity <span class="text-slate fw-normal">(concurrent orders)</span></label><input class="form-control is-invalid" value="0"><div class="invalid-feedback d-block">Capacity must be a positive whole number (FR5).</div></div>
   <div class="col-6"><label class="form-label">Status</label><select class="form-select"><option>Active – accepting orders</option></select></div>
   <div class="col-12"><label class="form-label">Brands operated</label>
    <div class="d-flex gap-2 flex-wrap">
     <span class="brand-tab on" style="padding:7px 12px"><i class="bi bi-check2"></i>Pho Express</span>
     <span class="brand-tab on" style="padding:7px 12px"><i class="bi bi-check2"></i>Banh Mi Corner</span>
     <span class="brand-tab on" style="padding:7px 12px"><i class="bi bi-check2"></i>Green Bowl</span>
     <span class="brand-tab" style="padding:7px 12px;color:#8A97A5"><i class="bi bi-plus"></i>Add brand</span></div></div>
  </div>
  <hr class="my-4"><div class="d-flex justify-content-end gap-2"><span class="btn btn-soft">Cancel</span><span class="btn btn-primary px-4">Save changes</span></div>
 </div></div>
 <div class="col-5 d-flex flex-column gap-4">
  <div class="cardx p-4"><div class="eyebrow mb-2">Live load</div><div class="d-flex align-items-end gap-2"><div class="fw-800 text-danger" style="font-size:40px;line-height:1">92%</div><div class="text-slate mb-1">23 active ÷ 25 capacity</div></div><div class="loadbar mt-3" style="height:12px"><i class="lb-red" style="width:92%"></i></div>
   <div class="d-flex justify-content-between small text-slate mt-1"><span>0</span><span>30% quiet</span><span>90% full</span><span>100%</span></div></div>
  <div class="cardx p-4" style="border-color:#E7B3AC"><div class="eyebrow mb-2" style="color:var(--sb-red)">Danger zone</div>
   <div class="fw-bold mb-1">Deactivate this hub</div><div class="small text-slate mb-3">Deactivation is a soft-delete: the hub stops taking orders but stays in order history and in R2.</div>
   <div class="p-3 rounded-3 d-flex gap-2 mb-3" style="background:var(--sb-red-50)"><i class="bi bi-exclamation-octagon-fill text-danger fs-5"></i><div class="small"><b>Cannot deactivate now.</b> Hub D1 still has <b>23 active orders</b> (Placed → Out for Delivery). Try again when they are finished (A-07).</div></div>
   <button class="btn w-100" style="border:1.5px solid #E7B3AC;color:#C0392B" disabled>Deactivate hub</button></div>
 </div>
</div></div>"""
page("12-admin-hub-edit", "Edit hub", "11-admin-hubs", "", edit)

# ------------------------------------------------------------------ 13 Revenue R1
r1 = top("Revenue report (R1)", "Revenue by brand category and payment method · Cancelled and Failed orders excluded",
         '<div class="d-flex align-items-center gap-2 small"><input class="form-control form-control-sm" style="width:132px" value="01/11/2026"><span>–</span><input class="form-control form-control-sm" style="width:132px" value="19/11/2026"></div>'
         '<span class="btn btn-navy btn-sm">Apply</span><span class="btn btn-soft btn-sm"><i class="bi bi-download me-1"></i>CSV</span>') + """
<div class="p-4">
 <div class="row g-3 mb-3">
  <div class="col-3"><div class="cardx kpi"><div class="lbl">Revenue</div><div class="val">186.4M ₫</div><div class="dl text-slate">1–19 Nov 2026 (UTC+7)</div></div></div>
  <div class="col-3"><div class="cardx kpi"><div class="lbl">Orders counted</div><div class="val">1,862</div><div class="dl text-slate">Delivered orders only</div></div></div>
  <div class="col-3"><div class="cardx kpi"><div class="lbl">Average order</div><div class="val">100,118 ₫</div><div class="dl text-slate">after discounts and fees</div></div></div>
  <div class="col-3"><div class="cardx kpi"><div class="lbl">Excluded</div><div class="val">74</div><div class="dl text-slate">61 cancelled · 13 failed</div></div></div>
 </div>
 <div class="row g-3">
  <div class="col-7"><div class="cardx p-4"><h2 class="section-title mb-3" style="font-size:17px">By brand category</h2><canvas id="cat" height="150"></canvas>
   <table class="sb mt-3"><thead><tr><th>Category</th><th>Brand</th><th class="text-end">Orders</th><th class="text-end">Revenue</th><th class="text-end">Share</th></tr></thead><tbody>
   <tr><td>Noodles &amp; soups</td><td>Pho Express</td><td class="text-end">781</td><td class="text-end">82,100,000 ₫</td><td class="text-end">44.0%</td></tr>
   <tr><td>Healthy bowls</td><td>Green Bowl</td><td class="text-end">463</td><td class="text-end">52,700,000 ₫</td><td class="text-end">28.3%</td></tr>
   <tr><td>Street food</td><td>Banh Mi Corner</td><td class="text-end">618</td><td class="text-end">51,600,000 ₫</td><td class="text-end">27.7%</td></tr>
   </tbody></table></div></div>
  <div class="col-5"><div class="cardx p-4 h-100"><h2 class="section-title mb-3" style="font-size:17px">By payment method</h2><canvas id="pay" height="210"></canvas>
   <table class="sb mt-3"><tbody>
   <tr><td><span class="pill pill-green">COD</span></td><td class="text-end">58,200,000 ₫</td></tr><tr><td><span class="pill" style="background:#F7E3EF;color:#A50064">MoMo</span></td><td class="text-end">49,400,000 ₫</td></tr>
   <tr><td><span class="pill pill-blue">VNPay</span></td><td class="text-end">31,100,000 ₫</td></tr><tr><td><span class="pill" style="background:#E6ECF5;color:#003087">PayPal</span></td><td class="text-end">27,500,000 ₫</td></tr>
   <tr><td><span class="pill pill-gray">Apple Pay</span></td><td class="text-end">20,200,000 ₫</td></tr></tbody></table></div></div>
 </div>
</div>"""
r1_js = """<script>
new Chart(document.getElementById('cat'),{type:'bar',data:{labels:['Noodles & soups','Healthy bowls','Street food'],datasets:[{data:[82.1,52.7,51.6],backgroundColor:['#C0392B','#1E8A5F','#E9A23B'],borderRadius:8,barThickness:34}]},
options:{indexAxis:'y',plugins:{legend:{display:false}},scales:{x:{title:{display:true,text:'million ₫'},grid:{color:'#EEF1F4'}},y:{grid:{display:false}}}}});
new Chart(document.getElementById('pay'),{type:'doughnut',data:{labels:['COD','MoMo','VNPay','PayPal','Apple Pay'],datasets:[{data:[58.2,49.4,31.1,27.5,20.2],backgroundColor:['#1E8A5F','#A50064','#005BAA','#003087','#5B6B7A'],borderWidth:2}]},
options:{cutout:'60%',plugins:{legend:{position:'right'}}}});
</script>"""
page("13-report-r1", "Revenue R1", "13-report-r1", "", r1, r1_js)

# ------------------------------------------------------------------ 14 Hub utilization R2
r2 = top("Hub utilization report (R2)", "Orders handled, average preparation time (Confirmed → Ready), current load and Quiet Kitchen discounts",
         '<div class="d-flex align-items-center gap-2 small"><input class="form-control form-control-sm" style="width:132px" value="01/11/2026"><span>–</span><input class="form-control form-control-sm" style="width:132px" value="19/11/2026"></div>'
         '<span class="btn btn-navy btn-sm">Apply</span><span class="btn btn-soft btn-sm"><i class="bi bi-download me-1"></i>CSV</span>') + """
<div class="p-4">
 <div class="cardx overflow-hidden mb-3">
 <table class="sb"><thead><tr><th>Hub</th><th class="text-end">Orders handled</th><th class="text-end">Avg prep (Confirmed → Ready)</th><th style="width:260px">Current load</th><th class="text-end">Quiet Kitchen discounts</th><th>Reading</th></tr></thead><tbody>
 <tr><td><b>Hub D1 · Quận 1</b></td><td class="text-end">712</td><td class="text-end">18.6 min</td><td><div class="d-flex align-items-center gap-2"><div class="loadbar flex-grow-1"><i class="lb-red" style="width:92%"></i></div><b class="text-danger">92%</b></div></td><td class="text-end">9</td><td><span class="pill pill-red">Overloaded – add capacity</span></td></tr>
 <tr><td><b>Hub BT · Bình Thạnh</b></td><td class="text-end">538</td><td class="text-end">15.2 min</td><td><div class="d-flex align-items-center gap-2"><div class="loadbar flex-grow-1"><i class="lb-amber" style="width:47%"></i></div><b style="color:#9A6412">47%</b></div></td><td class="text-end">41</td><td><span class="pill pill-amber">Healthy</span></td></tr>
 <tr><td><b>Hub TD · Thủ Đức</b></td><td class="text-end">384</td><td class="text-end">12.4 min</td><td><div class="d-flex align-items-center gap-2"><div class="loadbar flex-grow-1"><i class="lb-green" style="width:20%"></i></div><b class="text-success">20%</b></div></td><td class="text-end">176</td><td><span class="pill pill-green">Quiet – discounts pull demand</span></td></tr>
 <tr><td><b>Hub Q7 · Phú Mỹ Hưng</b></td><td class="text-end">228</td><td class="text-end">14.1 min</td><td><div class="d-flex align-items-center gap-2"><div class="loadbar flex-grow-1"><i class="lb-amber" style="width:56%"></i></div><b style="color:#9A6412">56%</b></div></td><td class="text-end">22</td><td><span class="pill pill-amber">Healthy</span></td></tr>
 <tr style="background:#FAFBFC"><td><b>All hubs</b></td><td class="text-end"><b>1,862</b></td><td class="text-end"><b>15.6 min</b></td><td class="small text-slate">weighted by orders</td><td class="text-end"><b>248</b></td><td></td></tr>
 </tbody></table></div>
 <div class="row g-3">
  <div class="col-6"><div class="cardx p-4"><h2 class="section-title mb-3" style="font-size:17px">Orders handled vs Quiet Kitchen discounts</h2><canvas id="hb" height="170"></canvas></div></div>
  <div class="col-6"><div class="cardx p-4"><h2 class="section-title mb-3" style="font-size:17px">Average preparation time (min)</h2><canvas id="pt" height="170"></canvas></div></div>
 </div>
</div>"""
r2_js = """<script>
new Chart(document.getElementById('hb'),{type:'bar',data:{labels:['D1','BT','TD','Q7'],datasets:[{label:'Orders handled',data:[712,538,384,228],backgroundColor:'#12263A',borderRadius:6},{label:'Quiet Kitchen discounts',data:[9,41,176,22],backgroundColor:'#1E8A5F',borderRadius:6}]},
options:{plugins:{legend:{position:'bottom'}},scales:{y:{grid:{color:'#EEF1F4'}},x:{grid:{display:false}}}}});
new Chart(document.getElementById('pt'),{type:'bar',data:{labels:['D1','BT','TD','Q7'],datasets:[{data:[18.6,15.2,12.4,14.1],backgroundColor:['#C0392B','#E9A23B','#1E8A5F','#E9A23B'],borderRadius:6,barThickness:42}]},
options:{plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,grid:{color:'#EEF1F4'}},x:{grid:{display:false}}}}});
</script>"""
page("14-report-r2", "Hub utilization R2", "14-report-r2", "", r2, r2_js)
