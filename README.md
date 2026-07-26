# Section Incident Report (Python FastAPI)

Unified Safety Framework - Incident Logging System for South Coast Railway. Converted from PHP to Python.

## ✨ Features

✅ Dark theme UI with modern design  
✅ Section incident entry form  
✅ Division-based access control (Visakhapatnam, Guntakal, Vijayawada, Guntur)  
✅ Admin dashboard with full report access  
✅ Division tabs in report view  
✅ Date range filtering  
✅ **Excel export** with all incident details  
✅ **Auto backup** functionality  
✅ Print-ready reports with signatures  
✅ User & Admin role-based access  

## 🔐 Login Credentials

### Admin Account
- **Username:** `admin`
- **Password:** `admin@123`
- **Access:** All divisions, all reports, backup features

### User Accounts (by Division)
| Division | Username | Password |
|----------|----------|----------|
| Visakhapatnam | `visakhapatnam` | `visakhapatnam123` |
| Guntakal | `guntakal` | `guntakal123` |
| Vijayawada | `vijayawada` | `vijayawada123` |
| Guntur | `guntur` | `guntur123` |

**Note:** Users see only their division's data. Admins see all divisions.

## 🎨 UI/UX Improvements

- **Dark theme** with gold accents (previously tri-color)
- **Adjusted SVG circles** - no overlap with Ashoka Emblem
- **Responsive design** - works on desktop, tablet, mobile
- **Professional styling** using Montserrat font

## 🛠 Tech Stack

- **Backend:** FastAPI
- **Database:** SQLite (local) or PostgreSQL (Render)
- **Frontend:** HTML5 + CSS3 (Dark theme)
- **Hosting:** Render.com (FREE tier)

## 📦 Local Setup

### 1. Clone & Install
```bash
git clone https://github.com/Pgumpina29/opreport.git
cd opreport
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Locally
```bash
uvicorn main:app --reload
```
Visit: `http://localhost:8000`

## 🚀 Deploy to Render (FREE)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Update with dark theme and backup features"
git push origin main
```

### Step 2: Render Deployment
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub repo `opreport`
4. Deploy (auto-deploys on git push)

**Live URL:** `https://opreport.onrender.com`

## 💾 Database & Backup

### Local Database
- **File:** `section_cases.db` (SQLite)
- **Auto-created** on first run

### Admin Backup Features
1. Click **Backup** button (admin only)
2. Creates timestamped backup in `/backups/`
3. Download backups for off-site storage

**Cloud Sync Options:**
- Backup file → Google Drive (manual drag-drop)
- Backup file → OneDrive (sync folder)
- Or set up scheduled backup to cloud via .env

## 📊 Reports & Export

### View Report
1. Log in as User or Admin
2. Select division tab (if admin)
3. Choose date range
4. Click **Filter** to view
5. Click **Print** for PDF
6. Click **Export to Excel** for spreadsheet

### Excel Export Includes
- ID, S.No, Date, Time, Division
- Section, Train No, Incident Type
- LP Name, Incident Details

## 🔑 API Endpoints

| Method | Endpoint | Access | Purpose |
|--------|----------|--------|---------|
| GET | `/` | Public | Welcome page |
| GET | `/login` | Public | Login form |
| POST | `/auth` | Public | Authenticate |
| GET | `/entry` | Authenticated | New incident form |
| POST | `/create` | Authenticated | Save incident |
| GET | `/records` | Authenticated | Edit existing records |
| GET | `/report` | Authenticated | View filtered reports |
| GET | `/export` | Authenticated | Excel export |
| GET | `/backup` | Admin only | Create database backup |
| GET | `/backup/download/{file}` | Admin only | Download backup |

## 📁 Project Structure

```
opreport/
├── main.py              # FastAPI app (all features)
├── requirements.txt     # Dependencies
├── .env.example         # Config template
├── .gitignore          # Git ignore rules
├── Procfile            # Deployment config
├── render.yaml         # Render.com config
├── section_cases.db    # SQLite database
├── backups/            # Auto-backup folder
└── README.md           # This file
```

## 🔧 Environment Variables

Create `.env` file:
```bash
# Database URL (auto-uses SQLite if not set)
DATABASE_URL=sqlite:///./section_cases.db

# Or for PostgreSQL (Render):
DATABASE_URL=postgresql://user:pass@host/dbname
```

## 📝 Database Schema

Auto-created on first run:

**Table: `section_cases`**
- Incident details (date, time, location, etc.)
- Train information (loco, crew, load)
- Investigation findings
- Restoration details
- USF reflection status

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Login fails | Check credentials in README (above) |
| Can't see other divisions (user) | Users see only their division. Admin sees all. |
| Excel export empty | Use date range filter on Report page |
| Render deployment fails | Check `requirements.txt` includes `openpyxl` |
| Database reset needed | Delete `section_cases.db` and restart |

## 📞 Support

- **GitHub:** [Pgumpina29/opreport](https://github.com/Pgumpina29/opreport)
- **Issues:** Create GitHub issue for bugs
- **Database:** SQLite (local) / PostgreSQL (Render)

---

**Last Updated:** 2026-07-26  
**Version:** 2.0 (Dark theme, Excel export, backup)  
**Original PHP Version:** section.php + sectionreport.php
