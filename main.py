from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, StreamingResponse
import csv
from io import StringIO
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv
import shutil
import subprocess
from pathlib import Path

load_dotenv()

# Use PostgreSQL if DATABASE_URL is set, otherwise use SQLite (local only)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./section_cases.db")
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # PostgreSQL connection (Render)
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SectionCase(Base):
    __tablename__ = "section_cases"
    id = Column(Integer, primary_key=True, index=True)
    sno = Column(String, nullable=True)
    date = Column(String, nullable=True)
    incident_time = Column(String, nullable=True)
    division = Column(String, nullable=True)
    section = Column(String, nullable=True)
    major_section = Column(String, nullable=True)
    minor_section = Column(String, nullable=True)
    location = Column(String, nullable=True)
    gradient = Column(String, nullable=True)
    curvature = Column(String, nullable=True)
    weather = Column(String, nullable=True)
    sanders = Column(String, nullable=True)
    spare_sandbags = Column(String, nullable=True)
    incident_type = Column(String, nullable=True)
    train_no = Column(String, nullable=True)
    vg_load = Column(String, nullable=True)
    fois_load = Column(String, nullable=True)
    jpo_load = Column(String, nullable=True)
    commodity = Column(String, nullable=True)
    load_at = Column(String, nullable=True)
    destination = Column(String, nullable=True)
    loconos = Column(String, nullable=True)
    homeshed = Column(String, nullable=True)
    locotype = Column(String, nullable=True)
    vcu_make = Column(String, nullable=True)
    date_commission = Column(String, nullable=True)
    last_overhaul = Column(String, nullable=True)
    last_schedule = Column(String, nullable=True)
    last_trip_schedule = Column(String, nullable=True)
    lp_name = Column(String, nullable=True)
    cms_id = Column(String, nullable=True)
    category = Column(String, nullable=True)
    alp_name = Column(String, nullable=True)
    assigned_cli = Column(String, nullable=True)
    guard = Column(String, nullable=True)
    lp_cell_no = Column(String, nullable=True)
    cli_cell_no = Column(String, nullable=True)
    trains_lost_punctuality = Column(String, nullable=True)
    trains_short_terminated = Column(String, nullable=True)
    trains_rescheduled = Column(String, nullable=True)
    traffic_block = Column(String, nullable=True)
    power_block = Column(String, nullable=True)
    banker_given = Column(String, nullable=True)
    banker_locono = Column(String, nullable=True)
    banker_trainno = Column(String, nullable=True)
    banker_detached_at = Column(String, nullable=True)
    banker_time = Column(String, nullable=True)
    banker_section_cleared = Column(String, nullable=True)
    banker_stn_name = Column(String, nullable=True)
    responsibility = Column(String, nullable=True)
    restoration_time = Column(String, nullable=True)
    root_cause = Column(Text, nullable=True)
    officers_movement = Column(Text, nullable=True)
    delay_reasons = Column(Text, nullable=True)
    incident_details = Column(Text, nullable=True)
    prev_logbook_remarks = Column(Text, nullable=True)
    shed_investigation = Column(Text, nullable=True)
    dpc_tlc_name = Column(String, nullable=True)
    usf_reflected = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Section Incident Report", version="1.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def hv(v):
    # HTML escape utility
    return str(v or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def fdate(s):
    if not s: return '-'
    try:
        from datetime import datetime as dt
        d = dt.strptime(str(s), '%Y-%m-%d')
        return d.strftime('%d-%m-%y')
    except:
        return hv(str(s))

@app.get("/")
async def welcome():
    return RedirectResponse(url="/login", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Login - USF-LOGS</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;}
body{margin:0; padding:0; font-family:'Montserrat',sans-serif; background:linear-gradient(135deg, #3e2723 0%, #5d4037 100%); min-height:100vh; display:flex; align-items:center; justify-content:center;}
.login-box{background:rgba(62,39,35,.98); padding:50px 40px; border-radius:12px; box-shadow:0 8px 40px rgba(0,0,0,.5); max-width:400px; width:95%; border:1px solid #6d4c41;}
h1{color:#e7b35a; font-size:24px; margin:0 0 10px; font-weight:700; text-align:center;}
.creds{color:#a8a8a8; font-size:11px; margin:0 0 20px; padding:10px; background:#1a1a1a; border-radius:6px; border-left:3px solid #e7b35a;}
.creds strong{color:#d4a574;}
.form-group{margin-bottom:20px;}
label{display:block; font-weight:600; color:#d4a574; margin-bottom:6px; font-size:13px;}
input{width:100%; padding:10px 12px; border:2px solid #6d4c41; border-radius:6px; font-size:14px; font-family:inherit; background:#2c1810; color:#fff;}
input:focus{outline:none; border-color:#e7b35a; box-shadow:0 0 0 3px rgba(231,179,90,.1);}
button{width:100%; padding:11px; background:#e7b35a; color:#1a1a1a; border:none; border-radius:6px; font-weight:700; font-size:15px; cursor:pointer; transition:.3s;}
button:hover{background:#d4a574;}
.error{color:#ffab91; font-size:13px; margin-bottom:15px; text-align:center; padding:10px; background:#3e2723; border-radius:6px; border:1px solid #6d4c41;}
.back{text-align:center; margin-top:15px;}
.back a{color:#e7b35a; text-decoration:none; font-size:13px;}
.back a:hover{text-decoration:underline;}
</style>
</head>
<body>
<div class="login-box">
<div style="width:200px; height:200px; margin:0 auto 20px; position:relative; display:flex; align-items:center; justify-content:center;">
<svg width="200" height="200" viewBox="0 0 200 200" style="position:absolute;">
<circle cx="100" cy="100" r="95" fill="none" stroke="#e7b35a" stroke-width="6"/>
<circle cx="100" cy="100" r="78" fill="none" stroke="#d4a574" stroke-width="5"/>
<circle cx="100" cy="100" r="62" fill="none" stroke="#a8a8a8" stroke-width="5"/>
</svg>
<img src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg" alt="Ashoka Emblem" style="width:90px; height:90px; position:relative; z-index:1; filter:brightness(0) invert(1) brightness(1.2);" onerror="this.style.display='none'">
</div>
<h1>USF-LOGS Login</h1>
<form method="POST" action="/auth">
<div class="form-group">
<label>Username</label>
<input type="text" name="username" required placeholder="Enter username" autocomplete="off">
</div>
<div class="form-group">
<label>Password</label>
<input type="password" name="password" required placeholder="Enter password" autocomplete="off">
</div>
<button type="submit">Login</button>
</form>
<div class="back">
<a href="/">← Back</a>
</div>
</div>
</body>
</html>"""

@app.post("/auth")
async def authenticate(username: str = Form(...), password: str = Form(...)):
    # Credentials mapping: username -> (password, division)
    credentials = {
        "visakhapatnam": ("visakhapatnam123", "Visakhapatnam"),
        "vskp": ("vskp123", "Visakhapatnam")
    }

    if username == "admin" and password == "admin@123":
        response = RedirectResponse(url="/entry", status_code=302)
        response.set_cookie(key="auth", value="logged_in", max_age=3600)
        response.set_cookie(key="role", value="admin", max_age=3600)
        return response
    elif username in credentials:
        expected_pass, division = credentials[username]
        if password == expected_pass:
            response = RedirectResponse(url="/entry", status_code=302)
            response.set_cookie(key="auth", value="logged_in", max_age=3600)
            response.set_cookie(key="role", value="user", max_age=3600)
            response.set_cookie(key="division", value=division, max_age=3600)
            return response
    return HTMLResponse("""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Login - USF-LOGS</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;}
body{margin:0; padding:0; font-family:'Montserrat',sans-serif; background:linear-gradient(135deg, #3e2723 0%, #5d4037 100%); min-height:100vh; display:flex; align-items:center; justify-content:center;}
.login-box{background:rgba(62,39,35,.98); padding:50px 40px; border-radius:12px; box-shadow:0 8px 40px rgba(0,0,0,.5); max-width:400px; width:95%; border:1px solid #6d4c41;}
h1{color:#e7b35a; font-size:24px; margin:0 0 10px; font-weight:700; text-align:center;}
.form-group{margin-bottom:20px;}
label{display:block; font-weight:600; color:#d4a574; margin-bottom:6px; font-size:13px;}
input{width:100%; padding:10px 12px; border:2px solid #6d4c41; border-radius:6px; font-size:14px; font-family:inherit; background:#2c1810; color:#fff;}
input:focus{outline:none; border-color:#e7b35a; box-shadow:0 0 0 3px rgba(231,179,90,.1);}
button{width:100%; padding:11px; background:#e7b35a; color:#1a1a1a; border:none; border-radius:6px; font-weight:700; font-size:15px; cursor:pointer; transition:.3s;}
button:hover{background:#d4a574;}
.error{color:#ff6b6b; font-size:13px; margin-bottom:15px; text-align:center; padding:10px; background:#3a1a1a; border-radius:6px; border:1px solid #8a3a3a;}
.back{text-align:center; margin-top:15px;}
.back a{color:#e7b35a; text-decoration:none; font-size:13px;}
.back a:hover{text-decoration:underline;}
</style>
</head>
<body>
<div class="login-box">
<div style="width:200px; height:200px; margin:0 auto 20px; position:relative; display:flex; align-items:center; justify-content:center;">
<svg width="200" height="200" viewBox="0 0 200 200" style="position:absolute;">
<circle cx="100" cy="100" r="95" fill="none" stroke="#e7b35a" stroke-width="6"/>
<circle cx="100" cy="100" r="78" fill="none" stroke="#d4a574" stroke-width="5"/>
<circle cx="100" cy="100" r="62" fill="none" stroke="#a8a8a8" stroke-width="5"/>
</svg>
<img src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg" alt="Ashoka Emblem" style="width:90px; height:90px; position:relative; z-index:1; filter:brightness(0) invert(1) brightness(1.2);" onerror="this.style.display='none'">
</div>
<h1>USF-LOGS Login</h1>
<form method="POST" action="/auth">
<div class="error">❌ Invalid username or password. Try again.</div>
<div class="form-group">
<label>Username</label>
<input type="text" name="username" required placeholder="Enter username" autocomplete="off">
</div>
<div class="form-group">
<label>Password</label>
<input type="password" name="password" required placeholder="Enter password" autocomplete="off">
</div>
<button type="submit">Login</button>
</form>
<div class="back">
<a href="/">← Back</a>
</div>
</div>
</body>
</html>""")

def check_auth(request: Request):
    if not request.cookies.get("auth"):
        return RedirectResponse(url="/login", status_code=302)
    return None

@app.get("/entry", response_class=HTMLResponse)
async def read_entry(request: Request):
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Section Incident Entry</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root{
    --brown:#5b3a29; --brown2:#7a5236; --brown-dark:#4a2e1f;
    --cream:#f7efda; --gold:#e7b35a;
    --border:#e0cfa8; --field-border:#cbb894; --field-bg:#fffdf8;
    --txt:#3a2a1e; --label:#6b5440; --muted:#8a745f;
    --green:#2e8b57; --green-dark:#256b44; --red:#c0392b;
}
*,*::before,*::after{box-sizing:border-box;}
body{
    margin:0; padding:20px;
    background:var(--cream); color:var(--txt);
    font:400 12px/1.45 'Montserrat',sans-serif;
}
input,select,textarea,button{font-family:inherit;}
.container{
    max-width:1500px; margin:0 auto; padding:18px;
    background:#fff; border:1px solid var(--border); border-radius:10px;
    box-shadow:0 4px 14px rgba(91,58,41,.10);
}
.page-head{
    display:flex; align-items:center; justify-content:space-between;
    gap:14px; flex-wrap:wrap; margin-bottom:16px;
}
.page-head h1{margin:0; font-size:19px; font-weight:700; color:var(--brown); letter-spacing:.2px;}
.tabs{display:flex; gap:6px; flex-wrap:wrap;}
.tabs a{
    padding:7px 14px; border-radius:20px; background:#efe3cd; color:var(--brown);
    text-decoration:none; font-size:12px; font-weight:600; white-space:nowrap; transition:.15s;
}
.tabs a:hover{background:#e3d3b3;}
.tabs a.active{background:var(--brown); color:#f3e7d6;}
.form-grid{
    display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr));
    gap:12px; align-items:start;
}
.form-block{
    min-width:0;
    padding:0 12px 12px;
    background:#faf5ea; border:1px solid #eadfc7; border-radius:8px;
    box-shadow:0 1px 4px rgba(91,58,41,.06);
}
.form-block.full{grid-column:1/-1;}
.form-block h3{
    margin:0 -12px 10px; padding:8px 12px;
    background:var(--brown); color:#f3e7d6; border-radius:7px 7px 0 0;
    font-size:12.5px; font-weight:600; letter-spacing:.3px;
}
.sub-head{
    margin:14px 0 0; padding-bottom:5px; border-bottom:1px solid var(--border);
    color:var(--brown); font-size:12px; font-weight:700; letter-spacing:.3px;
}
label{display:block; margin-top:8px; font-size:11.5px; font-weight:600; color:var(--label);}
input,select,textarea{
    width:100%; max-width:100%; margin-top:3px; padding:7px 8px;
    font-size:12.5px; color:var(--txt);
    background:var(--field-bg); border:1px solid var(--field-border); border-radius:5px;
}
input:focus,select:focus,textarea:focus{
    outline:none; border-color:var(--brown2); box-shadow:0 0 0 2px rgba(122,82,54,.16);
}
textarea{min-height:80px; resize:vertical;}
.field-row{display:flex; gap:12px; flex-wrap:wrap;}
.field-row>div{flex:1 1 220px; min-width:0;}
.actions{display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-top:16px;}
button{
    background:var(--green); color:#fff; border:none; border-radius:6px;
    padding:9px 22px; font-size:13px; font-weight:600; cursor:pointer; transition:.15s;
}
button:hover{background:var(--green-dark);}
.note{padding:9px 12px; border-radius:6px; font-size:12px; font-weight:600; margin-bottom:12px;}
.note.success{background:#e8f6ec; color:#0f6b34; border:1px solid #a8d5b8;}
.note.error{background:#ffecec; color:#b00020; border:1px solid #e3a3a3;}
.note ul{margin:4px 0 0; padding-left:18px; font-weight:500;}
@media(max-width:640px){
    body{padding:12px;}
    .container{padding:14px;}
}
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
        <a href="/logout" style="margin-left:auto; background:#c0392b; color:#fff;">Logout</a>
    </nav>
</div>

<form method="POST" action="/create">
<div class="form-grid">

<div class="form-block">
<h3>Section &amp; Incident</h3>
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
<div class="sub-head">Load Particulars</div>
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
<label>Last Overhaul &amp; Date</label><input name="last_overhaul" type="text">
<label>Last Schedule &amp; Date</label><input name="last_schedule" type="text">
<label>Last Trip Schedule Place &amp; Date</label><input name="last_trip_schedule" type="text">
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
<h3>Traffic Disruptions &amp; Blocks</h3>
<label>Trains Lost Punctuality</label><input name="trains_lost_punctuality" type="text">
<label>Trains Short Terminated</label><input name="trains_short_terminated" type="text">
<label>Trains Rescheduled / Delayed</label><input name="trains_rescheduled" type="text">
<div class="sub-head">Blocks</div>
<label>Traffic Block</label><input name="traffic_block" type="text">
<label>Power Block</label><input name="power_block" type="text">
<div class="sub-head">Relief / Banker</div>
<label>Relief / Banker Given</label>
<select id="banker_given" name="banker_given"><option value="">-- select --</option><option>Yes</option><option>No</option><option>Same Loco</option></select>
<div id="banker_details" style="display:none">
<label>Loco No</label><input name="banker_locono" type="text">
<label>Train No</label><input name="banker_trainno" type="text">
<label>Detached At</label><input name="banker_detached_at" type="text">
<label>Time</label><input type="time" name="banker_time">
<label>Section Cleared Time</label><input type="time" name="banker_section_cleared">
<label>Station Name</label><input name="banker_stn_name" type="text">
</div>
</div>

<div class="form-block full">
<h3>Investigation &amp; Restoration</h3>
<div class="field-row">
<div><label>Responsibility for Failure</label><input name="responsibility" type="text"></div>
<div><label>Time Taken for Restoration</label><input name="restoration_time" type="text"></div>
</div>
<label>Root Cause of Failure</label><textarea name="root_cause" rows="3"></textarea>
<label>Officers &amp; Staff Movement</label><textarea name="officers_movement" rows="3"></textarea>
<label>Reasons for Delay in Restoration / Measures to Minimise Restoration Time</label><textarea name="delay_reasons" rows="3"></textarea>
<label>Details of Incident</label><textarea name="incident_details" rows="5"></textarea>
<div class="field-row">
<div><label>Previous Log Book Remarks</label><textarea name="prev_logbook_remarks" rows="3"></textarea></div>
<div><label>Shed Investigation Finding</label><textarea name="shed_investigation" rows="3"></textarea></div>
</div>
<div class="field-row">
<div><label>DPC / TLC Name</label><input name="dpc_tlc_name" type="text"></div>
<div><label>USF Reflected In</label><select name="usf_reflected"><option value="">-- select --</option><option>Local</option><option>HQ</option><option>Deleted</option><option>Misc</option><option>Badweather</option></select></div>
</div>
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
"""

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
    train_no: str = Form(...),
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
    db = SessionLocal()
    try:
        incident = SectionCase(
            sno=sno, date=date, incident_time=incident_time, division=division, section=section,
            major_section=major_section, minor_section=minor_section, location=location,
            gradient=gradient, curvature=curvature, weather=weather, sanders=sanders,
            spare_sandbags=spare_sandbags, incident_type=incident_type, train_no=train_no,
            vg_load=vg_load, fois_load=fois_load, jpo_load=jpo_load, commodity=commodity,
            load_at=load_at, destination=destination, loconos=loconos, homeshed=homeshed,
            locotype=locotype, vcu_make=vcu_make, date_commission=date_commission,
            last_overhaul=last_overhaul, last_schedule=last_schedule, last_trip_schedule=last_trip_schedule,
            lp_name=lp_name, cms_id=cms_id, category=category, alp_name=alp_name,
            assigned_cli=assigned_cli, guard=guard, lp_cell_no=lp_cell_no, cli_cell_no=cli_cell_no,
            trains_lost_punctuality=trains_lost_punctuality, trains_short_terminated=trains_short_terminated,
            trains_rescheduled=trains_rescheduled, traffic_block=traffic_block, power_block=power_block,
            banker_given=banker_given, banker_locono=banker_locono, banker_trainno=banker_trainno,
            banker_detached_at=banker_detached_at, banker_time=banker_time,
            banker_section_cleared=banker_section_cleared, banker_stn_name=banker_stn_name,
            responsibility=responsibility, restoration_time=restoration_time,
            root_cause=root_cause, officers_movement=officers_movement, delay_reasons=delay_reasons,
            incident_details=incident_details, prev_logbook_remarks=prev_logbook_remarks,
            shed_investigation=shed_investigation, dpc_tlc_name=dpc_tlc_name, usf_reflected=usf_reflected
        )
        db.add(incident)
        db.commit()
        return HTMLResponse("""
        <html><body style="font-family: Montserrat; margin: 20px;">
            <div style="background:#e8f6ec; color:#0f6b34; padding:12px; border-radius:6px; border:1px solid #a8d5b8;">
            <h2 style="margin:0 0 8px;">✓ Saved successfully!</h2>
            <a href="/entry">← Back to form</a>
            </div>
        </body></html>
        """)
    except Exception as e:
        db.rollback()
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
    finally:
        db.close()

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("auth")
    return response

@app.get("/records", response_class=HTMLResponse)
async def get_records(request: Request):
    auth_check = check_auth(request)
    if auth_check:
        return auth_check
    db = SessionLocal()
    try:
        recs = db.query(SectionCase).order_by(SectionCase.id.desc()).limit(50).all()
        html = """<!doctype html>

<html><head><meta charset="utf-8"><title>Section Incident Records</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root{ --brown:#5b3a29; --cream:#f7efda; --border:#e0cfa8; --txt:#3a2a1e; --label:#6b5440; --green:#2e8b57; --green-dark:#256b44; --red:#c0392b; }
*{box-sizing:border-box;}
body{ margin:0; padding:20px; background:var(--cream); color:var(--txt); font:400 12px/1.45 'Montserrat',sans-serif; }
.container{ max-width:1500px; margin:0 auto; padding:18px; background:#fff; border:1px solid var(--border); border-radius:10px; box-shadow:0 4px 14px rgba(91,58,41,.10); }
.page-head h1{ margin:0 0 16px; font-size:19px; font-weight:700; color:var(--brown); }
.tabs{ display:flex; gap:6px; margin-bottom:20px; }
.tabs a{ padding:7px 14px; border-radius:20px; background:#efe3cd; color:var(--brown); text-decoration:none; font-size:12px; font-weight:600; }
.tabs a.active{ background:var(--brown); color:#f3e7d6; }
table{ width:100%; border-collapse:collapse; }
th,td{ padding:8px 10px; font-size:12px; text-align:left; border-bottom:1px solid #ece0cf; }
th{ background:var(--brown); color:#f3e7d6; font-weight:600; }
tbody tr:hover{ background:#fdf8ee; }
.rec-edit,.rec-del{ display:inline-block; color:#fff; text-decoration:none; font-size:11.5px; font-weight:600; padding:4px 12px; border-radius:5px; }
.rec-edit{ background:var(--green); }
.rec-edit:hover{ background:var(--green-dark); }
.rec-del{ background:var(--red); margin-left:4px; }
.rec-del:hover{ background:#a33024; }
.empty{ color:#8a745f; }
</style>
</head><body>
<div class="container">
<h1>Section Incident Records</h1>
<div class="tabs">
<a href="/entry">New Entry</a>
<a class="active" href="/records">Edit Records</a>
<a href="/report">View Report</a>
<a href="/logout" style="margin-left:auto; background:#c0392b; color:#fff;">Logout</a>
</div>
<h3>Saved Records (latest 50) — click Edit to modify</h3>
<table>
<thead><tr><th>ID</th><th>Sno</th><th>Date</th><th>Division</th><th>Train No</th><th>Incident</th><th>Action</th></tr></thead>
<tbody>
"""
        if recs:
            for r in recs:
                html += f"""<tr>
<td>{r.id}</td>
<td>{hv(r.sno or '')}</td>
<td>{hv(r.date or '')}</td>
<td>{hv(r.division or '')}</td>
<td>{hv(r.train_no or '')}</td>
<td>{hv(r.incident_type or '')}</td>
<td>
<a class="rec-edit" href="/edit/{r.id}">Edit</a>
<a class="rec-del" href="/delete/{r.id}" onclick="return confirm('Delete record #{r.id}?')">Delete</a>
</td>
</tr>"""
        else:
            html += '<tr><td colspan="7" class="empty">No records yet.</td></tr>'
        html += """</tbody></table>
</div></body></html>"""
        return html
    finally:
        db.close()

@app.get("/report", response_class=HTMLResponse)
async def get_report(request: Request, from_date: Optional[str] = None, to_date: Optional[str] = None, division: Optional[str] = None):
    auth_check = check_auth(request)
    if auth_check:
        return auth_check

    db = SessionLocal()
    try:
        is_admin = request.cookies.get("role") == "admin"
        user_division = request.cookies.get("division", "")

        records = []
        query = db.query(SectionCase)

        # Filter by date range if provided
        if from_date and to_date:
            query = query.filter(SectionCase.date.between(from_date, to_date))

        # Filter by Visakhapatnam division only
        query = query.filter(SectionCase.division == "Visakhapatnam")

        records = query.order_by(SectionCase.date.desc()).all()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Section Incident Report</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{{ box-sizing:border-box; }}
body,input,button{{ font-family:'Montserrat',sans-serif; font-size:10pt; }}
body{{ margin:16px; background:#f7efda; color:#3a2a1e; }}
h1{{ font-size:14pt; color:#5b3a29; margin:0 0 2px; }}
.sub{{ color:#8a745f; font-size:9pt; margin:0 0 12px; }}
.controls{{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:14px; }}
.controls label{{ font-weight:700; color:#6b5440; }}
input[type=date]{{ padding:6px 8px; border:1px solid #cbb894; border-radius:6px; background:#fffdf8; }}
button{{ padding:7px 16px; border:none; border-radius:6px; cursor:pointer; color:#fff; font-weight:600; }}
.btn-filter{{ background:#2e8b57; }} .btn-filter:hover{{ background:#256b44; }}
.btn-print{{ background:#7a5236; }} .btn-print:hover{{ background:#5b3a29; }}
.tabs{{ display:flex; gap:6px; margin-bottom:20px; }}
.tabs a{{ padding:7px 14px; border-radius:20px; background:#efe3cd; color:#5b3a29; text-decoration:none; font-size:12px; font-weight:600; }}
.tabs a.active{{ background:#5b3a29; color:#f3e7d6; }}
.empty{{ color:#8a745f; }}
.report-block{{ background:#fff; border:1px solid #e0cfa8; border-radius:8px; padding:14px 16px; margin-bottom:16px; box-shadow:0 2px 8px rgba(91,58,41,.08); page-break-inside:avoid; page-break-after:auto; }}
.report-block:not(:last-child){{ page-break-after:always; }}
.rpt-org{{ display:flex; justify-content:space-between; align-items:center; font-size:10.5pt; color:#5b3a29; letter-spacing:.3px; padding-bottom:5px; margin-bottom:6px; border-bottom:1px solid #c9a063; }}
.rpt-org b{{ color:#3a2a1e; }}
.block-head{{ display:flex; justify-content:space-between; font-weight:700; color:#5b3a29; border-bottom:2px solid #c9a063; padding-bottom:6px; margin-bottom:8px; }}
h2{{ font-size:9pt; color:#5b3a29; border-bottom:1px solid #e0cfa8; margin:12px 0 6px; padding-bottom:2px; }}
.grid{{ display:flex; flex-wrap:wrap; gap:8px 14px; }}
.field{{ flex:1 1 150px; min-width:140px; }}
.field.wide{{ flex-basis:100%; }}
.flabel{{ font-weight:700; font-size:8.5pt; color:#7a6450; }}
.fvalue{{ font-size:10pt; min-height:1em; }}
.sig-block{{ margin-top:20px; padding-top:12px; border-top:1px solid #e0cfa8; }}
.sig-line{{ display:flex; justify-content:space-between; }}
.sig-col{{ flex:1; text-align:center; }}
.sig-name{{ font-size:10pt; font-weight:600; color:#5b3a29; margin-top:40px; }}
@page{{ margin:0; }}
@media print{{
    html,body{{ margin:0; padding:0; background:#fff; color:#000; }}
    * {{ visibility:visible; }}
    .controls{{ display:none !important; }}
    .tabs{{ display:none !important; }}
    .division-tabs{{ display:none !important; }}
    .report-block{{ display:block !important; border:1px solid #444; border-radius:0; box-shadow:none; padding:6px 8px; margin:6mm; page-break-inside:avoid; visibility:visible; }}
    h1,.sub{{ display:none !important; }}
    .rpt-org{{ display:block !important; color:#000; border-bottom:1px solid #000; padding-bottom:4px; margin-bottom:6px; visibility:visible; }}
    .rpt-org b{{ color:#000; font-weight:bold; }}
    .block-head{{ display:block !important; border-bottom:1.5px solid #000; margin-bottom:6px; padding-bottom:4px; visibility:visible; }}
    h2{{ display:block !important; color:#000; border-bottom:1px solid #000; font-size:9pt; margin:8px 0 4px 0; padding-bottom:2px; visibility:visible; }}
    .grid{{ display:flex !important; flex-wrap:wrap; gap:8px 12px; margin-bottom:6px; visibility:visible; }}
    .field{{ display:block !important; flex:1 1 140px; min-width:120px; visibility:visible; }}
    .flabel{{ display:block !important; color:#000; font-weight:bold; font-size:8pt; visibility:visible; }}
    .fvalue{{ display:block !important; color:#000; font-size:9pt; visibility:visible; }}
    .sig-block{{ border-top:1px solid #000; margin-top:16px; padding-top:8px; }}
    .sig-name{{ color:#000; margin-top:36px; }}
    .print-footer{{ display:block !important; color:#000; border-top:1.5px solid #000; margin-top:20px; padding-top:10px; text-align:center; font-weight:bold; }}
    .print-header{{ display:none; }}
    .empty{{ display:none; }}
}}
</style>
</head>
<body>
<h1>Section Incident Report</h1>
<p class="sub">Section incidents — stalling, loco failure, derailment, CRO, etc.</p>

<div class="controls">
<form method="GET" style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
<label>From <input type="date" name="from_date" value="{hv(from_date or '')}"></label>
<label>To <input type="date" name="to_date" value="{hv(to_date or '')}"></label>
<button type="submit" class="btn-filter">Filter</button>
<button type="button" class="btn-print" onclick="window.print()">Print</button>
<a href="/export" style="margin-left:auto; display:inline-block; background:#138808; color:#fff; padding:7px 16px; border-radius:6px; text-decoration:none; font-weight:600; cursor:pointer;">📊 Export to Excel</a>
</form>
</div>

<p style='color:#6b5440; font-weight:600; margin-bottom:15px;'>Division: <b>Visakhapatnam</b></p>

<div class="tabs">
<a href="/entry">New Entry</a>
<a href="/records">Edit Records</a>
<a class="active" href="/report">View Report</a>
<a href="/logout" style="margin-left:auto; background:#c0392b; color:#fff;">Logout</a>
</div>
"""
        if not from_date or not to_date:
            html += '<p class="empty" style="color:#c0392b; font-weight:600; padding:20px; background:#ffe8e8; border-radius:6px;">⚠️ Please select a date range and click Filter to view reports.</p>'
        elif not records:
            html += f'<p class="empty">No records for the selected date range.</p>'
        else:
            for row in records:
                div_name = row.division or 'Visakhapatnam'
                html += f"""<div class="report-block">
<div class="rpt-org"><span>Railway: <b>SCoR</b></span><span>Division: <b>{hv(div_name)}</b></span></div>
<div class="block-head"><span>Date: {fdate(row.date)}</span><span>Train: {hv(row.train_no or '')}</span><span>Incident: {hv(row.incident_type or '')}</span></div>
<h2>1. Section &amp; Incident</h2>
<div class="grid">
<div class="field"><div class="flabel">S.No</div><div class="fvalue">{hv(row.sno or '-')}</div></div>
<div class="field"><div class="flabel">Division</div><div class="fvalue">{hv(row.division or '-')}</div></div>
<div class="field"><div class="flabel">Time</div><div class="fvalue">{hv(row.incident_time or '-')}</div></div>
<div class="field"><div class="flabel">Section</div><div class="fvalue">{hv(row.section or '-')}</div></div>
<div class="field"><div class="flabel">Major Section</div><div class="fvalue">{hv(row.major_section or '-')}</div></div>
<div class="field"><div class="flabel">Minor Section</div><div class="fvalue">{hv(row.minor_section or '-')}</div></div>
<div class="field"><div class="flabel">Location (OHE Mast)</div><div class="fvalue">{hv(row.location or '-')}</div></div>
<div class="field"><div class="flabel">Gradient</div><div class="fvalue">{hv(row.gradient or '-')}</div></div>
<div class="field"><div class="flabel">Curvature</div><div class="fvalue">{hv(row.curvature or '-')}</div></div>
<div class="field"><div class="flabel">Weather</div><div class="fvalue">{hv(row.weather or '-')}</div></div>
<div class="field"><div class="flabel">Sanders</div><div class="fvalue">{hv(row.sanders or '-')}</div></div>
<div class="field"><div class="flabel">Spare Sand Bags</div><div class="fvalue">{hv(row.spare_sandbags or '-')}</div></div>
<div class="field"><div class="flabel">Type of Incident</div><div class="fvalue">{hv(row.incident_type or '-')}</div></div>
</div>
<h2>2. Train Details</h2>
<div class="grid">
<div class="field"><div class="flabel">Train No</div><div class="fvalue">{hv(row.train_no or '-')}</div></div>
<div class="field"><div class="flabel">VG Load</div><div class="fvalue">{hv(row.vg_load or '-')}</div></div>
<div class="field"><div class="flabel">FOIS Load</div><div class="fvalue">{hv(row.fois_load or '-')}</div></div>
<div class="field"><div class="flabel">JPO Load</div><div class="fvalue">{hv(row.jpo_load or '-')}</div></div>
<div class="field"><div class="flabel">Commodity</div><div class="fvalue">{hv(row.commodity or '-')}</div></div>
<div class="field"><div class="flabel">Load At</div><div class="fvalue">{hv(row.load_at or '-')}</div></div>
<div class="field"><div class="flabel">Destination</div><div class="fvalue">{hv(row.destination or '-')}</div></div>
</div>
<h2>3. Loco</h2>
<div class="grid">
<div class="field"><div class="flabel">Loco Nos</div><div class="fvalue">{hv(row.loconos or '-')}</div></div>
<div class="field"><div class="flabel">Home Shed</div><div class="fvalue">{hv(row.homeshed or '-')}</div></div>
<div class="field"><div class="flabel">Type of Loco</div><div class="fvalue">{hv(row.locotype or '-')}</div></div>
<div class="field"><div class="flabel">Make of VCU</div><div class="fvalue">{hv(row.vcu_make or '-')}</div></div>
<div class="field"><div class="flabel">Date of Commission</div><div class="fvalue">{hv(row.date_commission or '-')}</div></div>
<div class="field"><div class="flabel">Last Overhaul</div><div class="fvalue">{hv(row.last_overhaul or '-')}</div></div>
<div class="field"><div class="flabel">Last Schedule</div><div class="fvalue">{hv(row.last_schedule or '-')}</div></div>
<div class="field"><div class="flabel">Last Trip Schedule</div><div class="fvalue">{hv(row.last_trip_schedule or '-')}</div></div>
</div>
<h2>4. Crew Details</h2>
<div class="grid">
<div class="field"><div class="flabel">LP Name</div><div class="fvalue">{hv(row.lp_name or '-')}</div></div>
<div class="field"><div class="flabel">CMS ID</div><div class="fvalue">{hv(row.cms_id or '-')}</div></div>
<div class="field"><div class="flabel">Category</div><div class="fvalue">{hv(row.category or '-')}</div></div>
<div class="field"><div class="flabel">ALP Name</div><div class="fvalue">{hv(row.alp_name or '-')}</div></div>
<div class="field"><div class="flabel">Assigned CLI</div><div class="fvalue">{hv(row.assigned_cli or '-')}</div></div>
<div class="field"><div class="flabel">Guard</div><div class="fvalue">{hv(row.guard or '-')}</div></div>
<div class="field"><div class="flabel">LP Cell No</div><div class="fvalue">{hv(row.lp_cell_no or '-')}</div></div>
<div class="field"><div class="flabel">CLI Cell No</div><div class="fvalue">{hv(row.cli_cell_no or '-')}</div></div>
</div>
<h2>5. Disruptions & Blocks</h2>
<div class="grid">
<div class="field"><div class="flabel">Trains Lost Punctuality</div><div class="fvalue">{hv(row.trains_lost_punctuality or '-')}</div></div>
<div class="field"><div class="flabel">Trains Short Terminated</div><div class="fvalue">{hv(row.trains_short_terminated or '-')}</div></div>
<div class="field"><div class="flabel">Trains Rescheduled</div><div class="fvalue">{hv(row.trains_rescheduled or '-')}</div></div>
<div class="field"><div class="flabel">Traffic Block</div><div class="fvalue">{hv(row.traffic_block or '-')}</div></div>
<div class="field"><div class="flabel">Power Block</div><div class="fvalue">{hv(row.power_block or '-')}</div></div>
</div>
<h2>6. Relief / Banker</h2>
<div class="grid">
<div class="field"><div class="flabel">Relief/Banker Given</div><div class="fvalue">{hv(row.banker_given or '-')}</div></div>
<div class="field"><div class="flabel">Loco No</div><div class="fvalue">{hv(row.banker_locono or '-')}</div></div>
<div class="field"><div class="flabel">Train No</div><div class="fvalue">{hv(row.banker_trainno or '-')}</div></div>
<div class="field"><div class="flabel">Detached At</div><div class="fvalue">{hv(row.banker_detached_at or '-')}</div></div>
<div class="field"><div class="flabel">Time</div><div class="fvalue">{hv(row.banker_time or '-')}</div></div>
<div class="field"><div class="flabel">Section Cleared Time</div><div class="fvalue">{hv(row.banker_section_cleared or '-')}</div></div>
<div class="field"><div class="flabel">Station Name</div><div class="fvalue">{hv(row.banker_stn_name or '-')}</div></div>
</div>
<h2>7. Restoration</h2>
<div class="grid">
<div class="field"><div class="flabel">Responsibility</div><div class="fvalue">{hv(row.responsibility or '-')}</div></div>
<div class="field"><div class="flabel">Restoration Time</div><div class="fvalue">{hv(row.restoration_time or '-')}</div></div>
</div>
<h2>8. Reporting</h2>
<div class="grid">
<div class="field"><div class="flabel">DPC / TLC Name</div><div class="fvalue">{hv(row.dpc_tlc_name or '-')}</div></div>
<div class="field"><div class="flabel">USF Reflected In</div><div class="fvalue">{hv(row.usf_reflected or '-')}</div></div>
</div>
<h2>Case Details</h2>
<div class="grid">
<div class="field wide"><div class="flabel">Root Cause</div><div class="fvalue">{(row.root_cause or '-') if row.root_cause else '-'}</div></div>
<div class="field wide"><div class="flabel">Officers & Staff Movement</div><div class="fvalue">{(row.officers_movement or '-') if row.officers_movement else '-'}</div></div>
<div class="field wide"><div class="flabel">Reasons for Delay</div><div class="fvalue">{(row.delay_reasons or '-') if row.delay_reasons else '-'}</div></div>
<div class="field wide"><div class="flabel">Details of Incident</div><div class="fvalue">{(row.incident_details or '-') if row.incident_details else '-'}</div></div>
<div class="field wide"><div class="flabel">Previous Log Book Remarks</div><div class="fvalue">{(row.prev_logbook_remarks or '-') if row.prev_logbook_remarks else '-'}</div></div>
<div class="field wide"><div class="flabel">Shed Investigation Finding</div><div class="fvalue">{(row.shed_investigation or '-') if row.shed_investigation else '-'}</div></div>
</div>
<div class="sig-block">
<div class="sig-line">
<div class="sig-col"><div class="sig-name">CTLC/{hv(div_name)}</div></div>
<div class="sig-col"><div class="sig-name">SRDEEP/{hv(div_name)}</div></div>
</div>
</div>
</div>"""
        # Show division codes in footer
        if not is_admin and user_division:
            html += f"""<div class="print-footer">
<p style="margin:8px 0;">CTLC-{user_division}</p>
<p style="margin:8px 0;">SRDEEP-{user_division}</p>
</div>"""
        elif is_admin and division:
            html += f"""<div class="print-footer">
<p style="margin:8px 0;">CTLC-{division}</p>
<p style="margin:8px 0;">SRDEEP-{division}</p>
</div>"""
        html += """</body></html>"""
        return html
    finally:
        db.close()

@app.get("/delete/{record_id}")
async def delete_record(record_id: int):
    db = SessionLocal()
    try:
        db.query(SectionCase).filter(SectionCase.id == record_id).delete()
        db.commit()
        return HTMLResponse("""<html><body style="font-family: Montserrat; margin: 20px;">
        <div style="background:#e8f6ec; color:#0f6b34; padding:12px; border-radius:6px; border:1px solid #a8d5b8;">
        <h2 style="margin:0 0 8px;">✓ Record deleted!</h2>
        <a href="/records">← Back to records</a>
        </div></body></html>""")
    finally:
        db.close()

@app.get("/export")
async def export_excel(request: Request, division: Optional[str] = None):
    auth_check = check_auth(request)
    if auth_check:
        return auth_check

    db = SessionLocal()
    try:
        is_admin = request.cookies.get("role") == "admin"

        if is_admin:
            records = db.query(SectionCase).order_by(SectionCase.date.desc()).all()
        else:
            user_division = request.cookies.get("division", "")
            records = db.query(SectionCase).filter(SectionCase.division == user_division).order_by(SectionCase.date.desc()).all()

        if division and is_admin:
            records = [r for r in records if r.division == division]

        output = StringIO()
        writer = csv.writer(output)

        headers = ['ID', 'S.No', 'Date', 'Time', 'Division', 'Section', 'Train No', 'Incident Type', 'LP Name', 'Incident Details']
        writer.writerow(headers)

        for record in records:
            writer.writerow([
                record.id, record.sno, record.date, record.incident_time, record.division,
                record.section, record.train_no, record.incident_type, record.lp_name, record.incident_details
            ])

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=usf_reports.csv"}
        )
    finally:
        db.close()

@app.get("/edit/{record_id}")
async def edit_record_page(record_id: int):
    db = SessionLocal()
    try:
        row = db.query(SectionCase).filter(SectionCase.id == record_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="Record not found")
        return HTMLResponse(f"Edit form for record {record_id} - TODO")
    finally:
        db.close()

@app.get("/backup")
async def backup_database(request: Request):
    auth_check = check_auth(request)
    if auth_check:
        return auth_check

    is_admin = request.cookies.get("role") == "admin"
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can backup")

    try:
        db_path = "section_cases.db"
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"section_cases_backup_{timestamp}.db"

        shutil.copy2(db_path, backup_file)

        return {"status": "success", "message": f"Database backed up to {backup_file}", "file": str(backup_file)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")

@app.get("/backup/download/{filename}")
async def download_backup(filename: str, request: Request):
    auth_check = check_auth(request)
    if auth_check:
        return auth_check

    is_admin = request.cookies.get("role") == "admin"
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can download backups")

    try:
        file_path = Path("backups") / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Backup file not found")

        return FileResponse(file_path, filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
