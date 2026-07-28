from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./incidents.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True)
    date = Column(String)
    train_no = Column(String)
    incident_type = Column(String)

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1>Welcome</h1><a href='/login'>Login</a>"

@app.get("/login", response_class=HTMLResponse)
def login():
    return "<h1>Login</h1><form method='POST' action='/auth'><input type='text' name='username' placeholder='Username'><input type='password' name='password' placeholder='Password'><button>Login</button></form><p>admin/admin@123</p>"

@app.post("/auth")
def auth(username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin@123":
        r = RedirectResponse("/entry", status_code=302)
        r.set_cookie("auth", "1")
        return r
    return RedirectResponse("/login", status_code=302)

@app.get("/entry", response_class=HTMLResponse)
def entry(request: Request):
    if not request.cookies.get("auth"):
        return RedirectResponse("/login", status_code=302)
    return "<h1>Entry</h1><form method='POST' action='/save'><input type='date' name='date' required><input type='text' name='train_no' placeholder='Train No' required><select name='incident_type'><option>Stalling</option><option>Derailment</option></select><button>Save</button></form><a href='/report'>Report</a> <a href='/logout'>Logout</a>"

@app.post("/save")
def save(date: str = Form(...), train_no: str = Form(...), incident_type: str = Form(...)):
    db = SessionLocal()
    db.add(Incident(date=date, train_no=train_no, incident_type=incident_type))
    db.commit()
    db.close()
    return "<h1>Saved!</h1><a href='/entry'>Back</a>"

@app.get("/report", response_class=HTMLResponse)
def report(request: Request):
    if not request.cookies.get("auth"):
        return RedirectResponse("/login", status_code=302)
    db = SessionLocal()
    rows = db.query(Incident).all()
    db.close()
    html = "<h1>Reports</h1><table border=1><tr><th>Date</th><th>Train</th><th>Type</th></tr>"
    for row in rows:
        html += f"<tr><td>{row.date}</td><td>{row.train_no}</td><td>{row.incident_type}</td></tr>"
    html += "</table><a href='/entry'>Back</a>"
    return html

@app.get("/logout")
def logout():
    r = RedirectResponse("/", status_code=302)
    r.delete_cookie("auth")
    return r
