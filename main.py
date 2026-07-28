from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, StreamingResponse
import csv
from io import StringIO
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from datetime import datetime
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
import shutil
import subprocess
from pathlib import Path
from bson import ObjectId

load_dotenv()

# MongoDB Connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://guest:guest@cluster0.mongodb.net/section_cases?retryWrites=true&w=majority")
try:
    client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client['section_cases']
    collection = db['incidents']
except Exception as e:
    print(f"⚠️ MongoDB connection warning: {e}")
    db = None
    collection = None

app = FastAPI(title="Section Incident Report", version="1.0.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def hv(v):
    return str(v or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def fdate(s):
    if not s: return '-'
    try:
        from datetime import datetime as dt
        d = dt.strptime(str(s), '%Y-%m-%d')
        return d.strftime('%d-%m-%y')
    except:
        return hv(str(s))

@app.on_event("startup")
async def startup_event():
    try:
        if collection:
            collection.create_index("date")
            collection.create_index("division")
            print("✓ MongoDB connected and indexes created")
    except Exception as e:
        print(f"⚠️ MongoDB startup warning: {e}")

credentials = {
    "admin": ("admin@123", "admin"),
    "visakhapatnam": ("visakhapatnam123", "vskp"),
    "guntakal": ("guntakal123", "gtl"),
    "vijayawada": ("vijayawada123", "bza"),
    "guntur": ("guntur123", "gnt")
}

def check_auth(request: Request):
    if not request.cookies.get("auth"):
        return RedirectResponse(url="/login", status_code=302)
    return None

@app.get("/")
async def welcome():
    return HTMLResponse("""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Section Incident Report</title><link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Montserrat,sans-serif;background:#2c1810;color:#f7efda;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}html,body{background:#2c1810}.welcome-box{background:rgba(62,39,35,.98);padding:60px 40px;border-radius:12px;box-shadow:0 8px 40px rgba(0,0,0,.5);max-width:500px;width:100%;border:1px solid #6d4c41;text-align:center}h1{color:#FF9933;font-size:32px;margin-bottom:15px;font-weight:700}p{color:#d4a574;font-size:14px;line-height:1.6;margin-bottom:20px}.ashoka{width:120px;height:120px;margin:0 auto 30px;position:relative}<svg width="200" height="200" viewBox="0 0 200 200" style="position:absolute;width:100%;height:100%"><circle cx="100" cy="100" r="95" fill="none" stroke="#FF9933" stroke-width="6"/><circle cx="100" cy="100" r="78" fill="none" stroke="#FFFFFF" stroke-width="5"/><circle cx="100" cy="100" r="62" fill="none" stroke="#138808" stroke-width="5"/><image x="45" y="45" width="110" height="110" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%23FF9933'/%3E%3C/svg%3E"/></svg>.btn{display:inline-block;margin:10px;padding:12px 30px;background:#138808;color:#fff;text-decoration:none;border-radius:6px;font-weight:600;transition:.3s}.btn:hover{background:#0d6206;transform:scale(1.05)}</style></head><body><div class="welcome-box"><div class="ashoka"></div><h1>Section Incident Report</h1><p>Unified Safety Framework - Incident Logging System for South Coast Railway</p><a href="/login" class="btn">Login</a></div></body></html>""")

@app.get("/login")
async def login_page():
    return HTMLResponse("""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Login</title><link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Montserrat,sans-serif;background:#2c1810;color:#f7efda;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}.login-container{position:relative;width:100%;max-width:400px}.login-box{background:rgba(62,39,35,.98);padding:50px 40px;border-radius:12px;box-shadow:0 8px 40px rgba(0,0,0,.5);max-width:400px;width:95%;border:1px solid #6d4c41}h1{color:#FF9933;font-size:24px;margin:0 0 10px;font-weight:700;text-align:center}.form-group{margin-bottom:20px}label{display:block;font-weight:600;color:#d4a574;margin-bottom:6px;font-size:13px}input{width:100%;padding:10px 12px;border:2px solid #6d4c41;border-radius:6px;font-size:14px;font-family:inherit;background:#2c1810;color:#fff}input:focus{outline:none;border-color:#FF9933;box-shadow:0 0 0 3px rgba(255,153,51,.1)}button{width:100%;padding:11px;background:#FF9933;color:#1a1a1a;border:none;border-radius:6px;font-weight:700;font-size:15px;cursor:pointer;transition:.3s}button:hover{background:#e68a1f}.error{color:#ffab91;font-size:13px;margin-bottom:15px;text-align:center;padding:10px;background:#3e2723;border-radius:6px;border:1px solid #6d4c41}.back{text-align:center;margin-top:15px}.back a{color:#FF9933;text-decoration:none;font-size:13px}.back a:hover{text-decoration:underline}<svg width="200" height="200" viewBox="0 0 200 200" style="position:absolute;top:-60px;left:50%;transform:translateX(-50%);z-index:-1"><circle cx="100" cy="100" r="95" fill="none" stroke="#FF9933" stroke-width="6"/><circle cx="100" cy="100" r="78" fill="none" stroke="#FFFFFF" stroke-width="5"/><circle cx="100" cy="100" r="62" fill="none" stroke="#138808" stroke-width="5"/></svg></style></head><body><div class="login-container"><div class="login-box"><h1>Login</h1><form method="POST" action="/auth"><div class="form-group"><label>Username</label><input type="text" name="username" required placeholder="Enter username" autocomplete="off"></div><div class="form-group"><label>Password</label><input type="password" name="password" required placeholder="Enter password" autocomplete="off"></div><button type="submit">Login</button><div class="back"><a href="/">← Back</a></div></form></div></div></body></html>""")

@app.post("/auth")
async def authenticate(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in credentials:
        expected_pass, division = credentials[username]
        if password == expected_pass:
            role = "admin" if username == "admin" else "user"
            response = RedirectResponse(url="/entry", status_code=302)
            response.set_cookie(key="auth", value=username, max_age=3600)
            response.set_cookie(key="role", value=role, max_age=3600)
            response.set_cookie(key="division", value=division if role == "user" else "Visakhapatnam", max_age=3600)
            return response
    return RedirectResponse(url="/login", status_code=302)

@app.get("/entry", response_class=HTMLResponse)
async def read_entry(request: Request):
    auth_check = check_auth(request)
    if auth_check:
        return auth_check

    return HTMLResponse("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Section Incident Entry</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Montserrat,sans-serif;background:#faf5ea;color:#3a2a1e;padding:20px}
.container{max-width:1200px;margin:0 auto;background:#fff;border-radius:8px;padding:24px;box-shadow:0 2px 12px rgba(91,58,41,.1)}
.page-head{margin-bottom:20px}
h1{font-size:28px;color:#5b3a29;margin-bottom:8px}
.tabs{display:flex;gap:6px;margin-bottom:20px}
.tabs a{padding:8px 16px;border-radius:20px;background:#efe3cd;color:#5b3a29;text-decoration:none;font-size:12px;font-weight:600;cursor:pointer}
.tabs a:hover{background:#e0cfa8}
.tabs a.active{background:#5b3a29;color:#f3e7d6}
.form-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;align-items:start}
.form-block{min-width:0;padding:0 12px 12px;background:#faf5ea;border:1px solid #eadfc7;border-radius:8px}
.form-block.full{grid-column:1/-1}
.form-block h3{margin:0 -12px 10px;padding:8px 12px;background:#5b3a29;color:#f3e7d6;border-radius:7px 7px 0 0;font-size:12.5px;font-weight:600}
label{display:block;margin-top:8px;font-size:11.5px;font-weight:600;color:#5b3a29}
input,select,textarea{width:100%;max-width:100%;margin-top:3px;padding:7px 8px;font-size:12.5px;color:#2c1810;background:#fffdf8;border:1px solid #cbb894;border-radius:5px}
input:focus,select:focus,textarea:focus{outline:none;border-color:#7a5236;box-shadow:0 0 0 2px rgba(122,82,54,.16)}
textarea{min-height:80px;resize:vertical}
.actions{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:16px}
button{background:#138808;color:#fff;border:none;border-radius:6px;padding:9px 22px;font-size:13px;font-weight:600;cursor:pointer;transition:.15s}
button:hover{background:#0d6206}
.note{padding:9px 12px;border-radius:6px;font-size:12px;font-weight:600;margin-bottom:12px}
.note.success{background:#e8f6ec;color:#0f6b34;border:1px solid #a8d5b8}
.note.error{background:#ffecec;color:#b00020;border:1px solid #e3a3a3}
@media(max-width:640px){body{padding:12px}.container{padding:14px}}
</style>
</head>
<body>
<div class="container">
<div class="page-head">
<h1>Section Incident Entry</h1>
<nav class="tabs">
<a class="active" href="/entry">New Entry</a>
<a href="/records">Edit Records</a>
<a href="/report">View Report</a>
<a href="/logout" style="margin-left:auto;background:#c0392b;color:#fff;">Logout</a>
</nav>
</div>

<form method="POST" action="/create">
<div class="form-grid">

<div class="form-block">
<h3>Section & Incident</h3>
<label>S.No</label><input name="sno" type="text">
<label>Date of Incidence</label><input type="date" name="date" required>
<label>Time of Incidence</label><input type="time" name="incident_time">
<input type="hidden" name="division" value="Visakhapatnam">
<label>Section</label><input name="section" type="text">
<label>Major Section</label><input name="major_section" type="text">
<label>Minor Section</label><input name="minor_section" type="text">
<label>Location (OHE Mast No)</label><input name="location" type="text">
<label>Gradient</label><input name="gradient" type="text">
<label>Curvature</label><input name="curvature" type="text">
<label>Weather Condition</label><select name="weather"><option value="">-- select --</option><option>Sunny</option><option>Fair</option><option>Drizzling</option><option>Raining</option><option>Dewy</option></select>
<label>Sanders</label><select name="sanders"><option value="">-- select --</option><option>Working</option><option>Not working</option><option>Sand exhausted</option><option>Sand pipe missing</option><option>Sander valve not working</option><option>Sander pipe not aligned</option><option>Pebble obstruction</option></select>
<label>Spare Sand Bags</label><select name="spare_sandbags"><option value="">-- select --</option><option>Yes</option><option>No</option></select>
<label>Type of Incident</label><select name="incident_type"><option value="">-- select --</option><option>Stalling</option><option>Loco Failure</option><option>Axle Lock</option><option>Hot axle</option><option>Derailment</option><option>CRO</option></select>
</div>

<div class="form-block">
<h3>Train Details</h3>
<label>Train No</label><input name="train_no" type="text" required>
<div style="margin:14px 0 0;padding-bottom:5px;border-bottom:1px solid #e0cfa8;color:#5b3a29;font-size:12px;font-weight:700">Load Particulars</div>
<label>VG Load</label><input name="vg_load" type="text">
<label>FOIS Load</label><input name="fois_load" type="text">
<label>JPO Load</label><input name="jpo_load" type="text">
<label>Commodity</label><input name="commodity" type="text">
<label>Load At</label><input name="load_at" type="text">
<label>Destination</label><input name="destination" type="text">
</div>

<div class="form-block">
<h3>Loco</h3>
<label>Loco Nos</label><input name="loconos" type="text">
<label>Home Shed</label><input name="homeshed" type="text">
<label>Type of Loco</label><input name="locotype" type="text">
<label>Make of VCU (BUR / SR / HLC)</label><input name="vcu_make" type="text">
<label>Date of Commission</label><input name="date_commission" type="text">
<label>Last Overhaul & Date</label><input name="last_overhaul" type="text">
<label>Last Schedule & Date</label><input name="last_schedule" type="text">
<label>Last Trip Schedule Place & Date</label><input name="last_trip_schedule" type="text">
</div>

<div class="form-block">
<h3>Crew Details</h3>
<label>LP Name</label><input name="lp_name" type="text">
<label>CMS ID</label><input name="cms_id" type="text">
<label>Category</label><input name="category" type="text">
<label>ALP Name</label><input name="alp_name" type="text">
<label>Assigned CLI</label><input name="assigned_cli" type="text">
<label>Guard</label><input name="guard" type="text">
<label>LP Cell No</label><input name="lp_cell_no" type="text">
<label>CLI Cell No</label><input name="cli_cell_no" type="text">
</div>

<div class="form-block">
<h3>Traffic Disruptions & Blocks</h3>
<label>Trains Lost Punctuality</label><input name="trains_lost_punctuality" type="text">
<label>Trains Short Terminated</label><input name="trains_short_terminated" type="text">
<label>Trains Rescheduled / Delayed</label><input name="trains_rescheduled" type="text">
<div style="margin:14px 0 0;padding-bottom:5px;border-bottom:1px solid #e0cfa8;color:#5b3a29;font-size:12px;font-weight:700">Blocks</div>
<label>Traffic Block</label><input name="traffic_block" type="text">
<label>Power Block</label><input name="power_block" type="text">
<div style="margin:14px 0 0;padding-bottom:5px;border-bottom:1px solid #e0cfa8;color:#5b3a29;font-size:12px;font-weight:700">Relief / Banker</div>
<label>Relief / Banker Given</label><select name="banker_given" id="banker_given"><option value="">-- select --</option><option>Yes</option><option>No</option><option>Same Loco</option></select>
<div id="banker_details" style="display:none">
<label>Loco No</label><input name="banker_locono" type="text">
<label>Train No</label><input name="banker_trainno" type="text">
<label>Detached At</label><input name="banker_detached_at" type="text">
<label>Time</label><input name="banker_time" type="time">
<label>Section Cleared Time</label><input name="banker_section_cleared" type="time">
<label>Station Name</label><input name="banker_stn_name" type="text">
</div>
</div>

<div class="form-block full">
<h3>Investigation & Restoration</h3>
<label>Responsibility for Failure</label><input name="responsibility" type="text">
<label>Time Taken for Restoration</label><input name="restoration_time" type="text">
<label>Root Cause of Failure</label><textarea name="root_cause" rows="3"></textarea>
<label>Officers & Staff Movement</label><textarea name="officers_movement" rows="3"></textarea>
<label>Reasons for Delay in Restoration / Measures to Minimise Restoration Time</label><textarea name="delay_reasons" rows="3"></textarea>
<label>Details of Incident</label><textarea name="incident_details" rows="5"></textarea>
<div style="display:flex;gap:12px;flex-wrap:wrap">
<div style="flex:1;min-width:0">
<label>Previous Log Book Remarks</label><textarea name="prev_logbook_remarks" rows="3"></textarea>
</div>
<div style="flex:1;min-width:0">
<label>Shed Investigation Finding</label><textarea name="shed_investigation" rows="3"></textarea>
</div>
</div>
<label>DPC / TLC Name</label><input name="dpc_tlc_name" type="text">
<label>USF Reflected In</label><select name="usf_reflected"><option value="">-- select --</option><option>Local</option><option>HQ</option><option>Deleted</option><option>Misc</option><option>Badweather</option></select>
</div>

</div>
<div class="actions">
<button type="submit">Submit</button>
</div>
</form>

</div>
<script>
var s = document.getElementById("banker_given"), b = document.getElementById("banker_details");
if (s && b) { s.addEventListener("change", function(){ b.style.display = (this.value === "Yes" || this.value === "Same Loco") ? "" : "none"; }); }
</script>
</body>
</html>
""")

@app.post("/create")
async def create_incident(
    sno: str = Form(None),
    date: str = Form(...),
    incident_time: str = Form(None),
    division: str = Form(None),
    section: str = Form(None),
    major_section: str = Form(None),
    minor_section: str = Form(None),
    location: str = Form(None),
    gradient: str = Form(None),
    curvature: str = Form(None),
    weather: str = Form(None),
    sanders: str = Form(None),
    spare_sandbags: str = Form(None),
    incident_type: str = Form(None),
    train_no: str = Form(None),
    vg_load: str = Form(None),
    fois_load: str = Form(None),
    jpo_load: str = Form(None),
    commodity: str = Form(None),
    load_at: str = Form(None),
    destination: str = Form(None),
    loconos: str = Form(None),
    homeshed: str = Form(None),
    locotype: str = Form(None),
    vcu_make: str = Form(None),
    date_commission: str = Form(None),
    last_overhaul: str = Form(None),
    last_schedule: str = Form(None),
    last_trip_schedule: str = Form(None),
    lp_name: str = Form(None),
    cms_id: str = Form(None),
    category: str = Form(None),
    alp_name: str = Form(None),
    assigned_cli: str = Form(None),
    guard: str = Form(None),
    lp_cell_no: str = Form(None),
    cli_cell_no: str = Form(None),
    trains_lost_punctuality: str = Form(None),
    trains_short_terminated: str = Form(None),
    trains_rescheduled: str = Form(None),
    traffic_block: str = Form(None),
    power_block: str = Form(None),
    banker_given: str = Form(None),
    banker_locono: str = Form(None),
    banker_trainno: str = Form(None),
    banker_detached_at: str = Form(None),
    banker_time: str = Form(None),
    banker_section_cleared: str = Form(None),
    banker_stn_name: str = Form(None),
    responsibility: str = Form(None),
    restoration_time: str = Form(None),
    root_cause: str = Form(None),
    officers_movement: str = Form(None),
    delay_reasons: str = Form(None),
    incident_details: str = Form(None),
    prev_logbook_remarks: str = Form(None),
    shed_investigation: str = Form(None),
    dpc_tlc_name: str = Form(None),
    usf_reflected: str = Form(None)
):
    try:
        incident_doc = {
            "sno": sno,
            "date": date,
            "incident_time": incident_time,
            "division": division,
            "section": section,
            "major_section": major_section,
            "minor_section": minor_section,
            "location": location,
            "gradient": gradient,
            "curvature": curvature,
            "weather": weather,
            "sanders": sanders,
            "spare_sandbags": spare_sandbags,
            "incident_type": incident_type,
            "train_no": train_no,
            "vg_load": vg_load,
            "fois_load": fois_load,
            "jpo_load": jpo_load,
            "commodity": commodity,
            "load_at": load_at,
            "destination": destination,
            "loconos": loconos,
            "homeshed": homeshed,
            "locotype": locotype,
            "vcu_make": vcu_make,
            "date_commission": date_commission,
            "last_overhaul": last_overhaul,
            "last_schedule": last_schedule,
            "last_trip_schedule": last_trip_schedule,
            "lp_name": lp_name,
            "cms_id": cms_id,
            "category": category,
            "alp_name": alp_name,
            "assigned_cli": assigned_cli,
            "guard": guard,
            "lp_cell_no": lp_cell_no,
            "cli_cell_no": cli_cell_no,
            "trains_lost_punctuality": trains_lost_punctuality,
            "trains_short_terminated": trains_short_terminated,
            "trains_rescheduled": trains_rescheduled,
            "traffic_block": traffic_block,
            "power_block": power_block,
            "banker_given": banker_given,
            "banker_locono": banker_locono,
            "banker_trainno": banker_trainno,
            "banker_detached_at": banker_detached_at,
            "banker_time": banker_time,
            "banker_section_cleared": banker_section_cleared,
            "banker_stn_name": banker_stn_name,
            "responsibility": responsibility,
            "restoration_time": restoration_time,
            "root_cause": root_cause,
            "officers_movement": officers_movement,
            "delay_reasons": delay_reasons,
            "incident_details": incident_details,
            "prev_logbook_remarks": prev_logbook_remarks,
            "shed_investigation": shed_investigation,
            "dpc_tlc_name": dpc_tlc_name,
            "usf_reflected": usf_reflected,
            "created_at": datetime.utcnow()
        }

        if collection:
            result = collection.insert_one(incident_doc)
            print(f"✓ SAVED: Incident ID={result.inserted_id}, Division={division}, Train={train_no}")

        return HTMLResponse("""
        <html><body style="font-family: Montserrat; margin: 20px;">
            <div style="background:#e8f6ec; color:#0f6b34; padding:12px; border-radius:6px; border:1px solid #a8d5b8;">
            <h2 style="margin:0 0 8px;">✓ Saved successfully!</h2>
            <a href="/entry">← Back to form</a>
            </div>
        </body></html>
        """)
    except Exception as e:
        print(f"ERROR SAVING INCIDENT: {str(e)}")
        return HTMLResponse(f"""
        <html><body style="font-family: Montserrat; margin: 20px;">
            <div style="background:#fde8e8; color:#c0392b; padding:12px; border-radius:6px; border:1px solid #f5b3b3;">
            <h2 style="margin:0 0 8px;">❌ Error saving incident!</h2>
            <p style="margin:8px 0; color:#8b0000;"><strong>Error:</strong> {str(e)}</p>
            <a href="/entry">← Back to form</a>
            </div>
        </body></html>
        """, status_code=400)

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("auth")
    return response

@app.get("/report", response_class=HTMLResponse)
async def get_report(request: Request, from_date: Optional[str] = None, to_date: Optional[str] = None):
    auth_check = check_auth(request)
    if auth_check:
        return auth_check

    try:
        query = {}
        query["division"] = {"$regex": "Visakhapatnam", "$options": "i"}

        if from_date and to_date:
            query["date"] = {"$gte": from_date, "$lte": to_date}

        records = list(collection.find(query).sort("date", -1)) if collection else []

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Section Incident Report</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{margin:0;padding:0;background:#faf5ea;color:#3a2a1e;font-family:Montserrat}}
.container{{max-width:1200px;margin:0 auto;padding:20px}}
h1{{font-size:28px;color:#5b3a29;margin-bottom:10px}}
.sub{{color:#8a745f;font-size:14px;margin-bottom:20px}}
.controls{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:20px}}
.tabs{{display:flex;gap:6px;margin-bottom:20px}}
.tabs a{{padding:7px 14px;border-radius:20px;background:#efe3cd;color:#5b3a29;text-decoration:none;font-size:12px;font-weight:600}}
.tabs a.active{{background:#5b3a29;color:#f3e7d6}}
.report-block{{background:#fff;border:1px solid #e0cfa8;border-radius:8px;padding:14px 16px;margin-bottom:16px;box-shadow:0 2px 8px rgba(91,58,41,.08);page-break-inside:avoid;page-break-after:auto}}
.rpt-org{{display:flex;justify-content:space-between;align-items:center;font-size:10.5pt;color:#5b3a29;letter-spacing:.3px;padding-bottom:5px;margin-bottom:6px;border-bottom:1px solid #c9a063}}
.block-head{{display:flex;justify-content:space-between;font-weight:700;color:#5b3a29;border-bottom:2px solid #c9a063;padding-bottom:6px;margin-bottom:8px}}
h2{{font-size:9pt;color:#5b3a29;border-bottom:1px solid #e0cfa8;margin:12px 0 6px;padding-bottom:2px}}
.grid{{display:flex;flex-wrap:wrap;gap:8px 14px}}
.field{{flex:1 1 150px;min-width:140px}}
.field.wide{{flex-basis:100%}}
.flabel{{font-weight:700;font-size:8.5pt;color:#7a6450}}
.fvalue{{font-size:10pt;min-height:1em}}
.empty{{color:#8a745f}}
@page{{margin:0}}
@media print{{
    html,body{{margin:0;padding:0;background:#fff;color:#000}}
    .controls{{display:none !important}}
    .tabs{{display:none !important}}
    h1,.sub{{display:none !important}}
    .report-block{{display:block !important;border:1px solid #444;border-radius:0;box-shadow:none;padding:6px 8px;margin:6mm;page-break-inside:avoid;visibility:visible}}
    .rpt-org{{display:block !important;color:#000;border-bottom:1px solid #000;padding-bottom:4px;margin-bottom:6px;visibility:visible}}
    .rpt-org b{{color:#000;font-weight:bold}}
    .block-head{{display:block !important;border-bottom:1.5px solid #000;margin-bottom:6px;padding-bottom:4px;visibility:visible}}
    h2{{display:block !important;color:#000;border-bottom:1px solid #000;font-size:9pt;margin:8px 0 4px 0;padding-bottom:2px;visibility:visible}}
    .grid{{display:flex !important;flex-wrap:wrap;gap:8px 12px;margin-bottom:6px;visibility:visible}}
    .field{{display:block !important;flex:1 1 140px;min-width:120px;visibility:visible}}
    .flabel{{display:block !important;color:#000;font-weight:bold;font-size:8pt;visibility:visible}}
    .fvalue{{display:block !important;color:#000;font-size:9pt;visibility:visible}}
}}
</style>
</head>
<body>
<div class="container">
<h1>Section Incident Report</h1>
<p class="sub">Section incidents — stalling, loco failure, derailment, CRO, etc.</p>

<div class="controls">
<form method="GET" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
<label>From <input type="date" name="from_date" value="{hv(from_date or '')}"></label>
<label>To <input type="date" name="to_date" value="{hv(to_date or '')}"></label>
<button type="submit" style="background:#7a5236;color:#fff;border:none;border-radius:6px;padding:8px 16px;cursor:pointer">Filter</button>
<button type="button" style="background:#7a5236;color:#fff;border:none;border-radius:6px;padding:8px 16px;cursor:pointer" onclick="window.print()">Print</button>
<a href="/export" style="margin-left:auto;display:inline-block;background:#138808;color:#fff;padding:7px 16px;border-radius:6px;text-decoration:none;font-weight:600;cursor:pointer">📊 Export to Excel</a>
</form>
</div>

<p style='color:#6b5440;font-weight:600;margin-bottom:15px;'>Division: <b>Visakhapatnam</b></p>

<div class="tabs">
<a href="/entry">New Entry</a>
<a href="/records">Edit Records</a>
<a class="active" href="/report">View Report</a>
<a href="/logout" style="margin-left:auto;background:#c0392b;color:#fff;">Logout</a>
</div>
"""
        if not records:
            html += f'<p class="empty">No records for the selected date range.</p>'
        else:
            for row in records:
                div_name = row.get('division') or 'Visakhapatnam'
                html += f"""<div class="report-block">
<div class="rpt-org"><span>Railway: <b>SCoR</b></span><span>Division: <b>{hv(div_name)}</b></span></div>
<div class="block-head"><span>Date: {fdate(row.get('date'))}</span><span>Train: {hv(row.get('train_no') or '')}</span><span>Incident: {hv(row.get('incident_type') or '')}</span></div>
<h2>1. Section &amp; Incident</h2>
<div class="grid">
<div class="field"><div class="flabel">S.No</div><div class="fvalue">{hv(row.get('sno') or '-')}</div></div>
<div class="field"><div class="flabel">Division</div><div class="fvalue">{hv(row.get('division') or '-')}</div></div>
<div class="field"><div class="flabel">Time</div><div class="fvalue">{hv(row.get('incident_time') or '-')}</div></div>
<div class="field"><div class="flabel">Section</div><div class="fvalue">{hv(row.get('section') or '-')}</div></div>
<div class="field"><div class="flabel">Major Section</div><div class="fvalue">{hv(row.get('major_section') or '-')}</div></div>
<div class="field"><div class="flabel">Minor Section</div><div class="fvalue">{hv(row.get('minor_section') or '-')}</div></div>
<div class="field"><div class="flabel">Location (OHE Mast)</div><div class="fvalue">{hv(row.get('location') or '-')}</div></div>
<div class="field"><div class="flabel">Gradient</div><div class="fvalue">{hv(row.get('gradient') or '-')}</div></div>
<div class="field"><div class="flabel">Curvature</div><div class="fvalue">{hv(row.get('curvature') or '-')}</div></div>
<div class="field"><div class="flabel">Weather</div><div class="fvalue">{hv(row.get('weather') or '-')}</div></div>
<div class="field"><div class="flabel">Sanders</div><div class="fvalue">{hv(row.get('sanders') or '-')}</div></div>
<div class="field"><div class="flabel">Spare Sand Bags</div><div class="fvalue">{hv(row.get('spare_sandbags') or '-')}</div></div>
<div class="field"><div class="flabel">Type of Incident</div><div class="fvalue">{hv(row.get('incident_type') or '-')}</div></div>
</div>
<h2>2. Train Details</h2>
<div class="grid">
<div class="field"><div class="flabel">Train No</div><div class="fvalue">{hv(row.get('train_no') or '-')}</div></div>
<div class="field"><div class="flabel">VG Load</div><div class="fvalue">{hv(row.get('vg_load') or '-')}</div></div>
<div class="field"><div class="flabel">FOIS Load</div><div class="fvalue">{hv(row.get('fois_load') or '-')}</div></div>
<div class="field"><div class="flabel">JPO Load</div><div class="fvalue">{hv(row.get('jpo_load') or '-')}</div></div>
<div class="field"><div class="flabel">Commodity</div><div class="fvalue">{hv(row.get('commodity') or '-')}</div></div>
<div class="field"><div class="flabel">Load At</div><div class="fvalue">{hv(row.get('load_at') or '-')}</div></div>
<div class="field"><div class="flabel">Destination</div><div class="fvalue">{hv(row.get('destination') or '-')}</div></div>
</div>
<h2>3. Loco</h2>
<div class="grid">
<div class="field"><div class="flabel">Loco Nos</div><div class="fvalue">{hv(row.get('loconos') or '-')}</div></div>
<div class="field"><div class="flabel">Home Shed</div><div class="fvalue">{hv(row.get('homeshed') or '-')}</div></div>
<div class="field"><div class="flabel">Type of Loco</div><div class="fvalue">{hv(row.get('locotype') or '-')}</div></div>
<div class="field"><div class="flabel">Make of VCU</div><div class="fvalue">{hv(row.get('vcu_make') or '-')}</div></div>
<div class="field"><div class="flabel">Date of Commission</div><div class="fvalue">{hv(row.get('date_commission') or '-')}</div></div>
<div class="field"><div class="flabel">Last Overhaul</div><div class="fvalue">{hv(row.get('last_overhaul') or '-')}</div></div>
<div class="field"><div class="flabel">Last Schedule</div><div class="fvalue">{hv(row.get('last_schedule') or '-')}</div></div>
<div class="field"><div class="flabel">Last Trip Schedule</div><div class="fvalue">{hv(row.get('last_trip_schedule') or '-')}</div></div>
</div>
<h2>4. Crew Details</h2>
<div class="grid">
<div class="field"><div class="flabel">LP Name</div><div class="fvalue">{hv(row.get('lp_name') or '-')}</div></div>
<div class="field"><div class="flabel">CMS ID</div><div class="fvalue">{hv(row.get('cms_id') or '-')}</div></div>
<div class="field"><div class="flabel">Category</div><div class="fvalue">{hv(row.get('category') or '-')}</div></div>
<div class="field"><div class="flabel">ALP Name</div><div class="fvalue">{hv(row.get('alp_name') or '-')}</div></div>
<div class="field"><div class="flabel">Assigned CLI</div><div class="fvalue">{hv(row.get('assigned_cli') or '-')}</div></div>
<div class="field"><div class="flabel">Guard</div><div class="fvalue">{hv(row.get('guard') or '-')}</div></div>
<div class="field"><div class="flabel">LP Cell No</div><div class="fvalue">{hv(row.get('lp_cell_no') or '-')}</div></div>
<div class="field"><div class="flabel">CLI Cell No</div><div class="fvalue">{hv(row.get('cli_cell_no') or '-')}</div></div>
</div>
<h2>5. Disruptions & Blocks</h2>
<div class="grid">
<div class="field"><div class="flabel">Trains Lost Punctuality</div><div class="fvalue">{hv(row.get('trains_lost_punctuality') or '-')}</div></div>
<div class="field"><div class="flabel">Trains Short Terminated</div><div class="fvalue">{hv(row.get('trains_short_terminated') or '-')}</div></div>
<div class="field"><div class="flabel">Trains Rescheduled</div><div class="fvalue">{hv(row.get('trains_rescheduled') or '-')}</div></div>
<div class="field"><div class="flabel">Traffic Block</div><div class="fvalue">{hv(row.get('traffic_block') or '-')}</div></div>
<div class="field"><div class="flabel">Power Block</div><div class="fvalue">{hv(row.get('power_block') or '-')}</div></div>
</div>
<h2>6. Relief / Banker</h2>
<div class="grid">
<div class="field"><div class="flabel">Relief/Banker Given</div><div class="fvalue">{hv(row.get('banker_given') or '-')}</div></div>
<div class="field"><div class="flabel">Loco No</div><div class="fvalue">{hv(row.get('banker_locono') or '-')}</div></div>
<div class="field"><div class="flabel">Train No</div><div class="fvalue">{hv(row.get('banker_trainno') or '-')}</div></div>
<div class="field"><div class="flabel">Detached At</div><div class="fvalue">{hv(row.get('banker_detached_at') or '-')}</div></div>
<div class="field"><div class="flabel">Time</div><div class="fvalue">{hv(row.get('banker_time') or '-')}</div></div>
<div class="field"><div class="flabel">Section Cleared Time</div><div class="fvalue">{hv(row.get('banker_section_cleared') or '-')}</div></div>
<div class="field"><div class="flabel">Station Name</div><div class="fvalue">{hv(row.get('banker_stn_name') or '-')}</div></div>
</div>
<h2>7. Restoration</h2>
<div class="grid">
<div class="field"><div class="flabel">Responsibility</div><div class="fvalue">{hv(row.get('responsibility') or '-')}</div></div>
<div class="field"><div class="flabel">Restoration Time</div><div class="fvalue">{hv(row.get('restoration_time') or '-')}</div></div>
<div class="field wide"><div class="flabel">Root Cause</div><div class="fvalue">{hv(row.get('root_cause') or '-')}</div></div>
<div class="field wide"><div class="flabel">Officers Movement</div><div class="fvalue">{hv(row.get('officers_movement') or '-')}</div></div>
<div class="field wide"><div class="flabel">Delay Reasons</div><div class="fvalue">{hv(row.get('delay_reasons') or '-')}</div></div>
<div class="field wide"><div class="flabel">Details of Incident</div><div class="fvalue">{hv(row.get('incident_details') or '-')}</div></div>
<div class="field wide"><div class="flabel">Previous Log Book Remarks</div><div class="fvalue">{hv(row.get('prev_logbook_remarks') or '-')}</div></div>
<div class="field wide"><div class="flabel">Shed Investigation Finding</div><div class="fvalue">{hv(row.get('shed_investigation') or '-')}</div></div>
</div>
<h2>8. Reporting</h2>
<div class="grid">
<div class="field"><div class="flabel">DPC / TLC Name</div><div class="fvalue">{hv(row.get('dpc_tlc_name') or '-')}</div></div>
<div class="field"><div class="flabel">USF Reflected In</div><div class="fvalue">{hv(row.get('usf_reflected') or '-')}</div></div>
</div>
</div>
"""
        html += """</body></html>"""
        return html
    except Exception as e:
        print(f"Report Error: {e}")
        return HTMLResponse(f"<p>Error loading report: {e}</p>", status_code=500)

@app.get("/export")
async def export_excel(request: Request):
    auth_check = check_auth(request)
    if auth_check:
        return auth_check

    try:
        records = list(collection.find({"division": {"$regex": "Visakhapatnam", "$options": "i"}}).sort("date", -1)) if collection else []

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Date", "Train", "Division", "Section", "Incident Type", "LP Name", "Status"])
        for row in records:
            writer.writerow([
                str(row.get('_id', '')),
                row.get('date', ''),
                row.get('train_no', ''),
                row.get('division', ''),
                row.get('section', ''),
                row.get('incident_type', ''),
                row.get('lp_name', ''),
                "Completed"
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment;filename=incidents_export.csv"}
        )
    except Exception as e:
        return HTMLResponse(f"<p>Export Error: {e}</p>", status_code=500)

@app.get("/debug-db")
async def debug_db():
    db_type = "MongoDB Atlas" if collection else "Not Connected"
    return HTMLResponse(f"""
    <html><body style="font-family: Montserrat; margin: 20px;">
    <h1>Database Configuration</h1>
    <p><strong>Database:</strong> {db_type}</p>
    <p><strong>STATUS:</strong> {'✅ Connected' if collection else '❌ Not Connected'}</p>
    <p><a href="/debug-data">View All Records →</a></p>
    </body></html>
    """)

@app.get("/debug-data")
async def debug_data():
    try:
        all_records = list(collection.find().limit(100)) if collection else []
        html = f"""
        <html><body style="font-family: Montserrat; margin: 20px;">
        <h1>Database Debug Info</h1>
        <p><strong>Total Records:</strong> {len(all_records)}</p>
        """
        if all_records:
            html += "<table border='1' style='border-collapse:collapse;padding:10px;'>"
            html += "<tr><th>ID</th><th>Date</th><th>Division</th><th>Train</th><th>Incident Type</th></tr>"
            for record in all_records:
                html += f"<tr><td>{str(record['_id'])}</td><td>{record.get('date', '')}</td><td>{record.get('division', '')}</td><td>{record.get('train_no', '')}</td><td>{record.get('incident_type', '')}</td></tr>"
            html += "</table>"
        else:
            html += "<p style='color:red;'><strong>⚠️ NO DATA IN DATABASE!</strong></p>"
        html += "</body></html>"
        return HTMLResponse(html)
    except Exception as e:
        return HTMLResponse(f"<p>Error: {e}</p>", status_code=500)

@app.get("/records", response_class=HTMLResponse)
async def get_records(request: Request):
    auth_check = check_auth(request)
    if auth_check:
        return auth_check

    try:
        recs = list(collection.find().sort("_id", -1).limit(50)) if collection else []
        html = """<!DOCTYPE html><html><head><title>Edit Records</title></head><body style="font-family:Montserrat;margin:20px">
        <h1>Saved Records (latest 50)</h1>
        <table border="1" style="border-collapse:collapse;width:100%;margin-top:20px">
        <tr><th>Date</th><th>Train</th><th>Incident</th><th>Actions</th></tr>
        """
        for r in recs:
            html += f"""<tr>
            <td>{r.get('date', '')}</td>
            <td>{r.get('train_no', '')}</td>
            <td>{r.get('incident_type', '')}</td>
            <td><a href="/delete/{str(r['_id'])}">Delete</a></td>
            </tr>"""
        html += """</table><br><a href="/entry">← Back</a></body></html>"""
        return html
    except Exception as e:
        return HTMLResponse(f"<p>Error: {e}</p>", status_code=500)

@app.get("/delete/{record_id}")
async def delete_record(record_id: str, request: Request):
    auth_check = check_auth(request)
    if auth_check:
        return auth_check

    try:
        if collection:
            collection.delete_one({"_id": ObjectId(record_id)})
        return RedirectResponse(url="/records", status_code=302)
    except Exception as e:
        return HTMLResponse(f"<p>Error: {e}</p>", status_code=500)
