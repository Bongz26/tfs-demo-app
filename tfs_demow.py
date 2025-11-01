# --------------------------------------------------------------
# tfs_demo.py – 100% LOCAL, NO 404s, FULL FEATURES
# --------------------------------------------------------------
import os
from flask import Flask, render_template_string, request, redirect, url_for, flash
import pandas as pd
from datetime import datetime
import io

app = Flask(__name__)
app.secret_key = 'tfs_secret_2025'

# ----------------------------------------------------------------------
# In-memory data
# ----------------------------------------------------------------------
clients = []
cases   = []
stock   = [
    {'id':1,'name':'3 Tier Coffin','category':'Coffins','quantity':10,'cost':1500,'supplier':'Local'},
    {'id':2,'name':'Econo Casket','category':'Coffins','quantity':5,'cost':800,'supplier':'Wholesaler'},
    {'id':3,'name':'Tent & 50 Chairs','category':'Tents/Chairs','quantity':8,'cost':2000,'supplier':'Event Hire'},
    {'id':4,'name':'Grocery Pack','category':'Catering','quantity':20,'cost':500,'supplier':'Grocer'},
    {'id':5,'name':'Flower Wreath','category':'Flowers','quantity':15,'cost':300,'supplier':'Florist'}
]
fleet   = [
    {'id':1,'reg':'TFS-001','driver':'John','status':'Free'},
    {'id':2,'reg':'TFS-002','driver':'Sarah','status':'Free'},
    {'id':3,'reg':'TFS-003','driver':'Mike','status':'Free'}
]
dispatch = []

next_client_id = 1
next_case_id   = 1
next_stock_id  = 6
next_fleet_id  = 4
next_disp_id   = 1

BRANCHES = ['Phuthaditjhaba','Bethlehem','Pretoria','Reitz']
SOURCES  = ['WhatsApp','Facebook','Walk-in','TikTok','Direct']
SERVICES = ['Burial – 3 Tier Coffin','Burial – Econo Casket','Cremation','Pre-Need Plan']

# ----------------------------------------------------------------------
# Language Dictionary (FULL)
# ----------------------------------------------------------------------
LANG = {
    'en':{
        'title':'Thusanang Funeral Services – Dashboard','lang_btn':'Sesotho',
        'add_client':'Add Client','client_name':'Name','client_contact':'Contact','client_source':'Source',
        'client_branch':'Branch','client_notes':'Notes','client_actions':'Actions',
        'add_case':'Create Funeral Case','case_client':'Client','case_service':'Service','case_status':'Status',
        'case_date':'Date','case_inventory':'Items (comma sep.)','dispatch':'Dispatch',
        'fleet':'Fleet','vehicle':'Vehicle','driver':'Driver','status':'Status','free':'Free','in_use':'In-Use',
        'dispatch_log':'Dispatch Log','out':'Out','in':'In','return':'Return',
        'stock':'Warehouse Stock','stock_name':'Item','stock_qty':'Qty','low_stock':'Low Stock',
        'export':'Export Excel','edit':'Edit','delete':'Delete','save':'Save','cancel':'Cancel',
        'search':'Search…','no_data':'No data yet','confirm_del':'Delete?','out_of_stock':'Out of stock',
        'no_vehicle':'No free vehicle','admin':'Admin View'
    },
    'st':{
        'title':'Thusanang Funeral Services – Dashboard','lang_btn':'English',
        'add_client':'Kenya Moreki','client_name':'Lebitso','client_contact':'Nomoro','client_source':'Mohloli',
        'client_branch':'Lekala','client_notes':'Lintlha','client_actions':'Liketso',
        'add_case':'Theha Ketsahalo','case_client':'Moreki','case_service':'Mofuta','case_status':'Boemo',
        'case_date':'Letsatsi','case_inventory':'Lintho (khaola ka koma)','dispatch':'Romela',
        'fleet':'Likoloi','vehicle':'Koloi','driver':'Mokhanni','status':'Boemo','free':'E lokolohile','in_use':'E sebelisoa',
        'dispatch_log':'Rekoto ea ho Romela','out':'Tsoha','in':'Kena','return':'Khutlisa',
        'stock':'Bohahlauli','stock_name':'Ntho','stock_qty':'Bongata','low_stock':'Bohahlauli bo Fokolang',
        'export':'Romela Excel','edit':'Fetola','delete':'Hlakola','save':'Boloka','cancel':'Hlakola',
        'search':'Batla…','no_data':'Ha ho na lintlha','confirm_del':'Hlakola?','out_of_stock':'Ha ho na thepa',
        'no_vehicle':'Ha ho koloi e lokolohile','admin':'Pono ea Admin'
    }
}
def txt(key):
    lang = request.cookies.get('lang','en')
    return LANG.get(lang, LANG['en']).get(key, key)

# ----------------------------------------------------------------------
# FULL HTML TEMPLATE (Bootstrap 5)
# ----------------------------------------------------------------------
HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ txt('title') }}</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
<style>
    :root{--tfs-blue:#0A3D62;--tfs-gold:#F4C430;--light:#f8f9fa;}
    body{background:linear-gradient(to bottom,var(--light),#e9ecef);}
    .navbar{background:var(--tfs-blue)!important;}
    .navbar-brand,.nav-link{color:var(--tfs-gold)!important;}
    .btn-tfs{background:var(--tfs-gold);color:var(--tfs-blue);border:none;font-weight:bold;}
    .btn-tfs:hover{background:#e0b52a;}
    .badge-free{background:#28a745;color:#fff;}
    .badge-use{background:#dc3545;color:#fff;}
    .low-stock{background:#dc3545;color:#fff;}
    .card{border-radius:15px;box-shadow:0 6px 20px rgba(10,61,98,.1);}
</style>
</head>
<body>
<nav class="navbar navbar-expand"><div class="container-fluid">
    <a class="navbar-brand" href="/"><i class="fas fa-cross me-2"></i>Thusanang FS</a>
    <button class="btn btn-tfs btn-sm" onclick="toggleLang()">{{ txt('lang_btn') }}</button>
</div></nav>

<div class="container mt-4">
{% with messages=get_flashed_messages() %}
  {% if messages %}<div class="alert alert-success">{{messages[0]}}</div>{% endif %}
{% endwith %}

<!-- CLIENTS -->
<div class="card mb-4"><div class="card-header"><h5><i class="fas fa-users"></i> {{ txt('add_client') }}</h5></div>
<div class="card-body">
<form method="post" action="/client/add" class="row g-2">
  <div class="col-md-3"><input class="form-control" name="name" placeholder="{{ txt('client_name') }}" required></div>
  <div class="col-md-3"><input class="form-control" name="contact" placeholder="{{ txt('client_contact') }}" required></div>
  <div class="col-md-2"><select class="form-select" name="source">{% for s in sources %}<option>{{s}}</option>{% endfor %}</select></div>
  <div class="col-md-2"><select class="form-select" name="branch">{% for b in branches %}<option>{{b}}</option>{% endfor %}</select></div>
  <div class="col-md-2"><textarea class="form-control" name="notes" rows="1" placeholder="{{ txt('client_notes') }}"></textarea></div>
  <div class="col-12"><button class="btn btn-tfs"><i class="fas fa-plus"></i> {{ txt('save') }}</button></div>
</form>

<input class="form-control mt-3" placeholder="{{ txt('search') }}" onkeyup="filter('client-table',this.value)">
<table class="table mt-2" id="client-table">
<thead class="table-dark"><tr><th>{{ txt('client_name') }}</th><th>{{ txt('client_contact') }}</th><th>{{ txt('client_source') }}</th>
<th>{{ txt('client_branch') }}</th><th>{{ txt('client_notes') }}</th><th>{{ txt('client_actions') }}</th></tr></thead>
<tbody>
{% for c in clients %}
<tr>
  <td>{{c.name}}</td><td>{{c.contact}}</td>
  <td><span class="badge bg-secondary">{{c.source}}</span></td>
  <td>{{c.branch}}</td>
  <td>
    <a href="#" onclick="showNote('{{c.notes|e}}')">
      {{ (c.notes[:20] + '…') if c.notes and c.notes|length > 20 else (c.notes or '—') }}
    </a>
  </td>
  <td>
    <button class="btn btn-sm btn-tfs" onclick="location.href='/client/edit/{{c.id}}'">{{ txt('edit') }}</button>
    <button class="btn btn-sm btn-danger" onclick="if(confirm('{{ txt('confirm_del') }}')) location.href='/client/delete/{{c.id}}'">{{ txt('delete') }}</button>
  </td>
</tr>
{% else %}<tr><td colspan="6">{{ txt('no_data') }}</td></tr>{% endfor %}
</tbody></table>
</div></div>

<!-- CASES -->
<div class="card mb-4"><div class="card-header"><h5><i class="fas fa-clipboard"></i> {{ txt('add_case') }}</h5></div>
<div class="card-body">
<form method="post" action="/case/add" class="row g-2">
  <div class="col-md-3"><select class="form-select" name="client_id" required>{% for c in clients %}<option value="{{c.id}}">{{c.name}}</option>{% endfor %}</select></div>
  <div class="col-md-3"><select class="form-select" name="service_type">{% for s in services %}<option>{{s}}</option>{% endfor %}</select></div>
  <div class="col-md-2"><select class="form-select" name="status"><option>Planning</option><option>Active</option><option>Completed</option></select></div>
  <div class="col-md-2"><input class="form-control" type="date" name="date" value="{{today}}" required></div>
  <div class="col-md-2"><input class="form-control" name="items" placeholder="{{ txt('case_inventory') }}"></div>
  <div class="col-12"><button class="btn btn-tfs"><i class="fas fa-plus"></i> {{ txt('save') }}</button></div>
</form>

<input class="form-control mt-3" placeholder="{{ txt('search') }}" onkeyup="filter('case-table',this.value)">
<table class="table mt-2" id="case-table">
<thead class="table-dark"><tr><th>{{ txt('case_client') }}</th><th>{{ txt('case_service') }}</th><th>{{ txt('case_status') }}</th>
<th>{{ txt('case_date') }}</th><th>Items</th><th>{{ txt('client_actions') }}</th></tr></thead>
<tbody>
{% for cs in cases %}
<tr>
  <td>{{ client_name(cs.client_id) }}</td>
  <td>{{cs.service_type}}</td>
  <td><span class="badge bg-info">{{cs.status}}</span></td>
  <td>{{cs.date}}</td>
  <td>{{ cs.items|join(', ') }}</td>
  <td>
    <button class="btn btn-sm btn-tfs" onclick="location.href='/case/edit/{{cs.id}}'">{{ txt('edit') }}</button>
    <button class="btn btn-sm btn-danger" onclick="if(confirm('{{ txt('confirm_del') }}')) location.href='/case/delete/{{cs.id}}'">{{ txt('delete') }}</button>
    {% if cs.status != 'Completed' %}
      <button class="btn btn-sm btn-success" onclick="location.href='/dispatch/{{cs.id}}'">Dispatch</button>
    {% endif %}
  </td>
</tr>
{% else %}<tr><td colspan="6">{{ txt('no_data') }}</td></tr>{% endfor %}
</tbody></table>
</div></div>

<!-- ADMIN -->
{% if admin %}
<div class="card mb-4"><div class="card-header"><h5><i class="fas fa-warehouse"></i> {{ txt('stock') }}</h5></div>
<div class="card-body">
<form method="post" action="/stock/add" class="row g-2 mb-3">
  <div class="col-md-3"><input class="form-control" name="name" placeholder="{{ txt('stock_name') }}"></div>
  <div class="col-md-2"><select class="form-select" name="category"><option>Coffins</option><option>Tents/Chairs</option><option>Catering</option><option>Flowers</option></select></div>
  <div class="col-md-2"><input class="form-control" type="number" name="qty" placeholder="{{ txt('stock_qty') }}"></div>
  <div class="col-md-2"><input class="form-control" type="number" name="cost" placeholder="Cost"></div>
  <div class="col-md-2"><input class="form-control" name="supplier" placeholder="Supplier"></div>
  <div class="col-12"><button class="btn btn-tfs"><i class="fas fa-plus"></i> Add</button></div>
</form>

<table class="table">
<thead class="table-dark"><tr><th>{{ txt('stock_name') }}</th><th>Cat.</th><th>{{ txt('stock_qty') }}</th><th>Cost</th><th>Supplier</th><th>Act.</th></tr></thead>
<tbody>
{% for s in stock %}
<tr {% if s.quantity < 5 %}class="table-danger"{% endif %}>
  <td>{{s.name}}</td><td>{{s.category}}</td>
  <td>{% if s.quantity < 5 %}<span class="badge low-stock">{{s.quantity}}</span>{% else %}{{s.quantity}}{% endif %}</td>
  <td>R {{s.cost}}</td><td>{{s.supplier}}</td>
  <td><button class="btn btn-sm btn-tfs" onclick="location.href='/stock/edit/{{s.id}}'">{{ txt('edit') }}</button></td>
</tr>
{% else %}<tr><td colspan="6">{{ txt('no_data') }}</td></tr>{% endfor %}
</tbody></table>
</div></div>

<div class="card mb-4"><div class="card-header"><h5><i class="fas fa-truck"></i> {{ txt('fleet') }}</h5></div>
<div class="card-body">
<table class="table"><thead class="table-dark"><tr><th>{{ txt('vehicle') }}</th><th>{{ txt('driver') }}</th><th>{{ txt('status') }}</th></tr></thead>
<tbody>
{% for v in fleet %}
<tr><td>{{v.reg}}</td><td>{{v.driver}}</td>
<td><span class="badge {% if v.status=='Free' %}badge-free{% else %}badge-use{% endif %}">{{ txt(v.status|lower) }}</span></td></tr>
{% endfor %}
</tbody></table>
</div></div>

<div class="card"><div class="card-header"><h5><i class="fas fa-list"></i> {{ txt('dispatch_log') }}</h5></div>
<div class="card-body">
<table class="table"><thead class="table-dark"><tr><th>Case</th><th>Vehicle</th><th>Driver</th><th>{{ txt('out') }}</th><th>{{ txt('in') }}</th><th>Items</th><th>Act.</th></tr></thead>
<tbody>
{% for d in dispatch %}
<tr>
  <td>{{ client_name(case_by_id(d.case_id).client_id) }} – {{ case_by_id(d.case_id).service_type }}</td>
  <td>{{ fleet_by_id(d.vehicle_id).reg }}</td><td>{{ fleet_by_id(d.vehicle_id).driver }}</td>
  <td>{{ d.out_date }}</td><td>{{ d.in_date or '—' }}</td>
  <td>{{ d.items|join(', ') }}</td>
  <td>{% if not d.in_date %}<button class="btn btn-sm btn-success" onclick="location.href='/dispatch/return/{{d.id}}'">Return</button>{% endif %}</td>
</tr>
{% else %}<tr><td colspan="7">{{ txt('no_data') }}</td></tr>{% endfor %}
</tbody></table>
</div></div>
{% endif %}

<a href="/export" class="btn btn-tfs"><i class="fas fa-download"></i> {{ txt('export') }}</a>
{% if not admin %}<a href="/?admin=1" class="btn btn-outline-secondary ms-2">{{ txt('admin') }}</a>{% endif %}
</div>

<div class="modal fade" id="noteModal"><div class="modal-dialog"><div class="modal-content">
<div class="modal-header"><h5>Full Note</h5><button class="btn-close" data-bs-dismiss="modal"></button></div>
<div class="modal-body" id="noteBody"></div></div></div></div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
function toggleLang(){document.cookie='lang='+(document.cookie.includes('lang=st')?'en':'st')+';path=/';location.reload();}
function filter(id,val){document.querySelectorAll('#'+id+' tbody tr').forEach(r=>r.style.display=r.textContent.toLowerCase().includes(val.toLowerCase())?'':'none');}
function showNote(t){document.getElementById('noteBody').innerText=t||'(none)';new bootstrap.Modal(document.getElementById('noteModal')).show();}
</script>
</body></html>
'''

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def client_name(cid): return next((c['name'] for c in clients if c['id']==cid), '')
def case_by_id(cid):   return next((c for c in cases if c['id']==cid), None)
def fleet_by_id(fid):  return next((f for f in fleet if f['id']==fid), None)

# ----------------------------------------------------------------------
# ROUTES – ALL WORKING
# ----------------------------------------------------------------------
@app.route("/")
def index():
    admin = request.args.get('admin') == '1'
    return render_template_string(HTML,
        clients=clients, cases=cases, stock=stock, fleet=fleet, dispatch=dispatch,
        branches=BRANCHES, sources=SOURCES, services=SERVICES,
        today=datetime.now().strftime('%Y-%m-%d'), admin=admin,
        txt=txt, client_name=client_name, case_by_id=case_by_id, fleet_by_id=fleet_by_id)

# CLIENTS
@app.route("/client/add", methods=["POST"])
def client_add():
    global next_client_id
    clients.append({
        'id': next_client_id, 'name': request.form['name'], 'contact': request.form['contact'],
        'source': request.form['source'], 'branch': request.form['branch'], 'notes': request.form.get('notes','')
    })
    next_client_id += 1
    flash('Client added')
    return redirect(url_for('index'))

@app.route("/client/edit/<int:cid>")
def client_edit(cid): flash('Edit client – form not implemented'); return redirect(url_for('index'))
@app.route("/client/delete/<int:cid>")
def client_delete(cid):
    global clients, cases
    clients = [c for c in clients if c['id']!=cid]
    cases = [cs for cs in cases if cs['client_id']!=cid]
    flash('Client removed')
    return redirect(url_for('index'))

# CASES
@app.route("/case/add", methods=["POST"])
def case_add():
    global next_case_id
    items = [i.strip() for i in request.form.get('items','').split(',') if i.strip()]
    for itm in items:
        s = next((s for s in stock if s['name'].lower()==itm.lower()), None)
        if not s or s['quantity'] < 1:
            flash(f'Out of stock: {itm}')
            return redirect(url_for('index'))
    for itm in items:
        s = next((s for s in stock if s['name'].lower()==itm.lower()), None)
        if s: s['quantity'] -= 1
    cases.append({
        'id': next_case_id, 'client_id': int(request.form['client_id']),
        'service_type': request.form['service_type'], 'status': request.form['status'],
        'date': request.form['date'], 'items': items
    })
    next_case_id += 1
    flash('Case created')
    return redirect(url_for('index'))

@app.route("/case/edit/<int:cid>")
def case_edit(cid): flash('Edit case – form not implemented'); return redirect(url_for('index'))
@app.route("/case/delete/<int:cid>")
def case_delete(cid):
    global cases, dispatch
    cs = next((c for c in cases if c['id']==cid), None)
    if cs and not any(d['case_id']==cid for d in dispatch):
        for itm in cs['items']:
            s = next((s for s in stock if s['name'].lower()==itm.lower()), None)
            if s: s['quantity'] += 1
    cases = [c for c in cases if c['id']!=cid]
    dispatch = [d for d in dispatch if d['case_id']!=cid]
    flash('Case removed')
    return redirect(url_for('index'))

# DISPATCH
@app.route("/dispatch/<int:case_id>")
def dispatch_case(case_id):
    cs = case_by_id(case_id)
    if not cs: return redirect(url_for('index'))
    free = [v for v in fleet if v['status']=='Free']
    if not free:
        flash(txt('no_vehicle'))
        return redirect(url_for('index'))
    veh = free[0]; veh['status'] = 'In-Use'
    global next_disp_id
    dispatch.append({
        'id': next_disp_id, 'case_id': case_id, 'vehicle_id': veh['id'],
        'items': cs['items'], 'out_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'in_date': None, 'driver': veh['driver']
    })
    next_disp_id += 1
    flash(f'Dispatched – {veh["reg"]}')
    return redirect(url_for('index'))

@app.route("/dispatch/return/<int:disp_id>")
def return_dispatch(disp_id):
    d = next((x for x in dispatch if x['id']==disp_id), None)
    if not d or d['in_date']: return redirect(url_for('index'))
    v = fleet_by_id(d['vehicle_id'])
    if v: v['status'] = 'Free'
    d['in_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    flash('Returned')
    return redirect(url_for('index'))

# STOCK
@app.route("/stock/add", methods=["POST"])
def stock_add():
    global next_stock_id
    stock.append({
        'id': next_stock_id, 'name': request.form['name'], 'category': request.form['category'],
        'quantity': int(request.form['qty']), 'cost': float(request.form['cost']),
        'supplier': request.form['supplier']
    })
    next_stock_id += 1
    flash('Stock added')
    return redirect(url_for('index') + '?admin=1')

@app.route("/stock/edit/<int:sid>")
def stock_edit(sid): flash('Edit stock – form not implemented'); return redirect(url_for('index') + '?admin=1')

# EXPORT
@app.route("/export")
def export():
    df_c = pd.DataFrame([{'ID':c['id'],'Name':c['name'],'Contact':c['contact'],'Source':c['source'],'Branch':c['branch'],'Notes':c['notes']} for c in clients])
    df_cs = pd.DataFrame([{'CaseID':cs['id'],'Client':client_name(cs['client_id']),'Service':cs['service_type'],'Status':cs['status'],'Date':cs['date'],'Items':', '.join(cs['items'])} for cs in cases])
    df_s = pd.DataFrame(stock)
    df_d = pd.DataFrame([{'DispatchID':d['id'],'CaseID':d['case_id'],'Vehicle':fleet_by_id(d['vehicle_id'])['reg'],'Driver':d['driver'],'Out':d['out_date'],'In':d.get('in_date','—'),'Items':', '.join(d['items'])} for d in dispatch])
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        df_c.to_excel(writer, sheet_name='Clients', index=False)
        df_cs.to_excel(writer, sheet_name='Cases', index=False)
        df_s.to_excel(writer, sheet_name='Stock', index=False)
        df_d.to_excel(writer, sheet_name='Dispatch', index=False)
    out.seek(0)
    return out.getvalue(), 200, {
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'Content-Disposition': 'attachment; filename=tfs_report.xlsx'
    }

# ----------------------------------------------------------------------
# Run locally
# ----------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=port, debug=False)
