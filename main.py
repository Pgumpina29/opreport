from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv
import csv
from io import StringIO

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./section_cases.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SectionCase(Base):
    __tablename__ = "section_cases"

    id = Column(Integer, primary_key=True, index=True)
    sno = Column(String, nullable=True)
    date = Column(String, nullable=True)
    incident_time = Column(String, nullable=True)
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
    dpc_tlc_name = Column(String, nullable=True)
    usf_reflected = Column(String, nullable=True)
    root_cause = Column(Text, nullable=True)
    officers_movement = Column(Text, nullable=True)
    delay_reasons = Column(Text, nullable=True)
    incident_details = Column(Text, nullable=True)
    prev_logbook_remarks = Column(Text, nullable=True)
    shed_investigation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Section Incident Report", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Section Incident Report</title>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            * { box-sizing: border-box; }
            body, input, button, select, textarea { font-family: 'Montserrat', sans-serif; font-size: 10pt; }
            body { margin: 16px; background: #f7efda; color: #3a2a1e; }
            h1 { font-size: 14pt; color: #5b3a29; margin: 0 0 2px; }
            .sub { color: #8a745f; font-size: 9pt; margin: 0 0 12px; }
            .controls { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }
            .controls label { font-weight: 700; color: #6b5440; }
            input[type=date] { padding: 6px 8px; border: 1px solid #cbb894; border-radius: 6px; background: #fffdf8; }
            input[type=text], select, textarea { padding: 6px 8px; border: 1px solid #cbb894; border-radius: 6px; background: #fffdf8; }
            button { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; color: #fff; font-weight: 600; }
            .btn-filter { background: #2e8b57; }
            .btn-filter:hover { background: #256b44; }
            .btn-export { background: #1d6f42; }
            .btn-export:hover { background: #155233; }
            .btn-print { background: #7a5236; }
            .btn-print:hover { background: #5b3a29; }
            .form-section { background: #fff; border: 1px solid #e0cfa8; border-radius: 8px; padding: 14px 16px; margin-bottom: 16px; }
            .form-group { margin-bottom: 12px; }
            .form-group label { display: block; font-weight: 700; font-size: 8.5pt; color: #7a6450; margin-bottom: 3px; }
            .form-group input, .form-group select, .form-group textarea { width: 100%; }
            .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
            .grid.wide { grid-template-columns: 1fr; }
            textarea { resize: vertical; min-height: 80px; }
            .table-wrap { overflow-x: auto; }
            table { border-collapse: collapse; width: 100%; background: #fff; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 9pt; }
            th { background: #f6e087; font-weight: 600; }
            tr:nth-child(even) { background: #faf5ea; }
        </style>
    </head>
    <body>
        <h1>📋 Section Incident Report</h1>
        <p class="sub">SCoR Visakhapatnam Division</p>

        <div class="controls">
            <form method="GET" action="/report" style="display: flex; gap: 10px; flex-wrap: wrap;">
                <label>From <input type="date" name="from_date" required></label>
                <label>To <input type="date" name="to_date" required></label>
                <button type="submit" class="btn-filter">View Report</button>
            </form>
        </div>

        <div class="form-section">
            <h2>New Section Incident Entry</h2>
            <form method="POST" action="/create">
                <div class="grid">
                    <div class="form-group">
                        <label>S.No</label>
                        <input type="text" name="sno">
                    </div>
                    <div class="form-group">
                        <label>Date</label>
                        <input type="date" name="date" required>
                    </div>
                    <div class="form-group">
                        <label>Incident Time</label>
                        <input type="time" name="incident_time">
                    </div>
                    <div class="form-group">
                        <label>Section</label>
                        <input type="text" name="section">
                    </div>
                    <div class="form-group">
                        <label>Major Section</label>
                        <select name="major_section">
                            <option value="">--</option>
                            <option value="RV">RV</option>
                            <option value="PSA">PSA</option>
                            <option value="COMPLEX">COMPLEX</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Type of Incident</label>
                        <select name="incident_type">
                            <option value="">--</option>
                            <option value="Stalling">Stalling</option>
                            <option value="Loco Failure">Loco Failure</option>
                            <option value="Axle Lock">Axle Lock</option>
                            <option value="Hot axle">Hot axle</option>
                            <option value="Derailment">Derailment</option>
                            <option value="CRO">CRO</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Train No</label>
                        <input type="text" name="train_no">
                    </div>
                    <div class="form-group">
                        <label>Loco Nos</label>
                        <input type="text" name="loconos">
                    </div>
                    <div class="form-group">
                        <label>Home Shed</label>
                        <input type="text" name="homeshed">
                    </div>
                    <div class="form-group">
                        <label>LP Name</label>
                        <input type="text" name="lp_name">
                    </div>
                    <div class="form-group">
                        <label>Root Cause</label>
                        <textarea name="root_cause"></textarea>
                    </div>
                    <div class="form-group wide">
                        <label>Incident Details</label>
                        <textarea name="incident_details" style="min-height: 120px;"></textarea>
                    </div>
                    <div class="form-group">
                        <label>DPC / TLC Name</label>
                        <input type="text" name="dpc_tlc_name">
                    </div>
                    <div class="form-group">
                        <label>USF Reflected In</label>
                        <select name="usf_reflected">
                            <option value="">--</option>
                            <option value="Local">Local</option>
                            <option value="HQ">HQ</option>
                            <option value="Deleted">Deleted</option>
                            <option value="Misc">Misc</option>
                            <option value="Badweather">Badweather</option>
                        </select>
                    </div>
                </div>
                <button type="submit" class="btn-filter" style="margin-top: 10px;">Save Entry</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/create")
async def create_incident(
    sno: str = Form(None),
    date: str = Form(...),
    incident_time: str = Form(None),
    section: str = Form(None),
    major_section: str = Form(None),
    incident_type: str = Form(None),
    train_no: str = Form(None),
    loconos: str = Form(None),
    homeshed: str = Form(None),
    lp_name: str = Form(None),
    root_cause: str = Form(None),
    incident_details: str = Form(None),
    dpc_tlc_name: str = Form(None),
    usf_reflected: str = Form(None),
    db: Session = None
):
    db = SessionLocal()
    try:
        incident = SectionCase(
            sno=sno, date=date, incident_time=incident_time, section=section,
            major_section=major_section, incident_type=incident_type, train_no=train_no,
            loconos=loconos, homeshed=homeshed, lp_name=lp_name, root_cause=root_cause,
            incident_details=incident_details, dpc_tlc_name=dpc_tlc_name, usf_reflected=usf_reflected
        )
        db.add(incident)
        db.commit()
        return HTMLResponse("""
        <html><body style="font-family: Arial; margin: 20px;">
            <h2 style="color: green;">✓ Entry saved successfully</h2>
            <a href="/">← Back to form</a>
        </body></html>
        """)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/report", response_class=HTMLResponse)
async def get_report(from_date: Optional[str] = None, to_date: Optional[str] = None):
    db = SessionLocal()
    try:
        query = db.query(SectionCase)
        if from_date and to_date:
            query = query.filter(SectionCase.date.between(from_date, to_date))
        records = query.order_by(SectionCase.date.desc()).all()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Section Incident Report</title>
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
            <style>
                body {{ font-family: 'Montserrat', sans-serif; margin: 20px; background: #f7efda; }}
                h1 {{ color: #5b3a29; }}
                .controls {{ margin-bottom: 20px; }}
                button {{ padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; color: #fff; font-weight: 600; }}
                .btn-print {{ background: #7a5236; }} .btn-print:hover {{ background: #5b3a29; }}
                .btn-excel {{ background: #1d6f42; }} .btn-excel:hover {{ background: #155233; }}
                table {{ border-collapse: collapse; width: 100%; background: #fff; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 9pt; }}
                th {{ background: #f6e087; font-weight: 600; }}
                tr:nth-child(even) {{ background: #faf5ea; }}
                @media print {{
                    .controls {{ display: none; }}
                    body {{ background: #fff; }}
                }}
            </style>
        </head>
        <body>
            <h1>📑 Section Incident Report</h1>
            <div class="controls">
                <button class="btn-print" onclick="window.print()">🖨 Print</button>
                <a href="/export?from_date={from_date or ''}&to_date={to_date or ''}">
                    <button class="btn-excel">📊 Export Excel</button>
                </a>
                <a href="/"><button class="btn-print">← Back</button></a>
            </div>
            <p><strong>{len(records)} records</strong></p>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Train No</th>
                        <th>Type</th>
                        <th>Loco</th>
                        <th>LP Name</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
        """

        if records:
            for r in records:
                html += f"""
                <tr>
                    <td>{r.date or '-'}</td>
                    <td>{r.train_no or '-'}</td>
                    <td>{r.incident_type or '-'}</td>
                    <td>{r.loconos or '-'}</td>
                    <td>{r.lp_name or '-'}</td>
                    <td>{r.incident_details[:50] if r.incident_details else '-'}</td>
                </tr>
                """
        else:
            html += "<tr><td colspan='6' style='text-align: center;'>No records found</td></tr>"

        html += """
                </tbody>
            </table>
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; display: flex; justify-content: space-between;">
                <div style="text-align: center;">
                    <div style="margin-top: 40px; font-weight: 600;">CTLC/VSKP</div>
                </div>
                <div style="text-align: center;">
                    <div style="margin-top: 40px; font-weight: 600;">Sr.DEE(OP)/VSKP</div>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    finally:
        db.close()

@app.get("/export")
async def export_excel(from_date: Optional[str] = None, to_date: Optional[str] = None):
    db = SessionLocal()
    try:
        query = db.query(SectionCase)
        if from_date and to_date:
            query = query.filter(SectionCase.date.between(from_date, to_date))
        records = query.all()

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Date', 'Train', 'Type', 'Loco', 'LP Name', 'Section', 'Incident Details'])

        for r in records:
            writer.writerow([
                r.date or '', r.train_no or '', r.incident_type or '',
                r.loconos or '', r.lp_name or '', r.section or '',
                r.incident_details or ''
            ])

        return {
            "content": output.getvalue(),
            "filename": f"section_report_{from_date}_{to_date}.csv"
        }
    finally:
        db.close()

@app.get("/api/incidents")
async def get_incidents(db: Session = None):
    db = SessionLocal()
    try:
        incidents = db.query(SectionCase).all()
        return [
            {
                "id": i.id,
                "date": i.date,
                "train_no": i.train_no,
                "incident_type": i.incident_type,
                "loco": i.loconos,
                "lp_name": i.lp_name
            }
            for i in incidents
        ]
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
