# Section Incident Report (Python FastAPI)

Converted from PHP to Python. Section incident management system for SCoR Visakhapatnam Division.

## Features

✅ Section incident entry form  
✅ Automated report generation  
✅ Print & Excel export  
✅ Date range filtering  
✅ Signature blocks (CTLC/VSKP, Sr.DEE(OP)/VSKP)  
✅ RESTful API  

## Tech Stack

- **Backend:** FastAPI
- **Database:** PostgreSQL (Render) or SQLite (local)
- **Frontend:** HTML + CSS (Montserrat theme)
- **Hosting:** Render.com (FREE)

## Local Setup

### 1. Clone & Install
```bash
git clone https://github.com/vskpusf/opreport.git
cd opreport
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env with your database URL
```

### 3. Run Locally
```bash
uvicorn main:app --reload
```
Visit: `http://localhost:8000`

## Deploy to Render (FREE)

### Step 1: GitHub Setup
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/vskpusf/opreport.git
git push -u origin main
```

### Step 2: Render Deployment
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect to `vskpusf/opreport`
5. Use settings from `render.yaml`
6. Deploy!

### Your Live URL
```
https://opreport.onrender.com
```

## Database Schema

Automatically created on first run. Tables:
- `section_cases` — All incident records

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Entry form |
| POST | `/create` | Save incident |
| GET | `/report` | View report (filtered) |
| GET | `/export` | Export to Excel |
| GET | `/api/incidents` | JSON API |

## Files

```
opreport/
├── main.py              # FastAPI app
├── requirements.txt     # Python packages
├── .env.example        # Config template
├── .gitignore          # Git ignore
├── Procfile            # Heroku/Render config
├── render.yaml         # Render deployment
└── README.md           # This file
```

## Database Backup

```bash
# Export from Render
pg_dump postgresql://user:pass@host/db > backup.sql

# Restore
psql postgresql://user:pass@host/db < backup.sql
```

## Support

- **Local Issues:** Check `.env` database URL
- **Deploy Issues:** Check Render logs
- **Database:** Use Render's built-in PostgreSQL (free)

---

**Created:** 2026-07-26  
**Python Conversion:** FastAPI + SQLAlchemy  
**Original:** section.php + sectionreport.php
