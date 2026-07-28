from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI(title="Section Incident Report")

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1>✅ App WORKING!</h1><a href='/login'>Go to Login</a>"

@app.get("/login", response_class=HTMLResponse)
def login():
    return """<html><body style="text-align:center; padding:50px;">
    <h1>Section Incident Report</h1>
    <form method="POST" action="/auth">
        <input type="text" name="username" placeholder="Username" required><br><br>
        <input type="password" name="password" placeholder="Password" required><br><br>
        <button type="submit">Login</button>
    </form>
    <p>Test: admin / admin@123</p>
    </body></html>"""

@app.post("/auth", response_class=HTMLResponse)
def auth(username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin@123":
        return "<h1>✅ Login Success!</h1><a href='/entry'>Go to Entry</a>"
    return "<h1>❌ Login Failed!</h1><a href='/login'>Try Again</a>"

@app.get("/entry", response_class=HTMLResponse)
def entry():
    return """<html><body style="padding:50px;">
    <h1>✅ Entry Form - App Working!</h1>
    <p>Full incident form coming soon...</p>
    <form method="POST" action="/save">
        <input type="text" name="train_no" placeholder="Train Number" required><br><br>
        <input type="date" name="date" required><br><br>
        <button type="submit">Save Incident</button>
    </form>
    <a href="/report">View Report</a>
    </body></html>"""

@app.post("/save", response_class=HTMLResponse)
def save(train_no: str = Form(...), date: str = Form(...)):
    return f"<h1>✅ Saved!</h1><p>Train: {train_no}</p><p>Date: {date}</p><a href='/entry'>Back</a>"

@app.get("/report", response_class=HTMLResponse)
def report():
    return "<h1>📊 Report Page</h1><p>Reports coming soon...</p><a href='/entry'>Back</a>"
