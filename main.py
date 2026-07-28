from fastapi import FastAPI
from fastapi.responses import HTMLResponse

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

@app.post("/auth")
def auth(username: str, password: str):
    if username == "admin" and password == "admin@123":
        return "<h1>Login Success!</h1><a href='/entry'>Go to Entry</a>"
    return "<h1>Login Failed!</h1>"

@app.get("/entry", response_class=HTMLResponse)
def entry():
    return "<h1>✅ Entry Form - App Working!</h1>"
