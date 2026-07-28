# PythonAnywhere Deployment Guide

## Complete Step-by-Step Setup (15 minutes)

---

## **STEP 1: Create PythonAnywhere Account (2 min)**

1. Go to: https://www.pythonanywhere.com
2. Click **"Create a Beginner account"** (FREE)
3. Enter email & password
4. Verify email
5. Login to dashboard

---

## **STEP 2: Upload Your Code (3 min)**

1. In PythonAnywhere dashboard, click **"Files"** (top menu)
2. Click **"Upload a file"**
3. Upload these files:
   - `main.py` (your app)
   - `requirements.txt` (dependencies)
4. All files go to `/home/YOUR_USERNAME/mysite/`

---

## **STEP 3: Create Web App (5 min)**

1. Click **"Web"** (top menu)
2. Click **"Add a new web app"**
3. Choose domain: `yourname.pythonanywhere.com`
4. Click **"Next"**
5. Select **"Python 3.11"**
6. Click **"Manual configuration"**
7. Click **"Next"**

---

## **STEP 4: Configure WSGI File (3 min)**

1. Click **"Web"** → Your web app
2. Find **"WSGI configuration file"** section
3. Click the link (like `/var/www/yourname_pythonanywhere_com_wsgi.py`)
4. **Replace ALL content** with this:

```python
import sys
path = '/home/YOUR_USERNAME/mysite'
if path not in sys.path:
    sys.path.append(path)

from main import app
application = app
```

5. **Replace `YOUR_USERNAME`** with your actual username
6. Click **"Save"**

---

## **STEP 5: Install Dependencies (2 min)**

1. Click **"Consoles"** (top menu)
2. Click **"Bash"**
3. Run this command:
```bash
pip install fastapi uvicorn sqlalchemy python-multipart
```

4. Wait for install to finish ✓

---

## **STEP 6: Reload Web App (1 min)**

1. Go back to **"Web"**
2. Scroll to top
3. Click the green **"Reload"** button
4. Wait 10 seconds

---

## **STEP 7: Test Your App!**

Your app is LIVE at:
```
https://YOURNAME.pythonanywhere.com
```

**Test it:**
1. Click your domain link
2. You should see: "Welcome" message
3. Click "Login"
4. Enter: `admin` / `admin@123`
5. Click "Login"
6. **You're in!** ✅

---

## **TROUBLESHOOTING**

### Error: "ModuleNotFoundError"
- Run bash console: `pip install fastapi uvicorn sqlalchemy python-multipart`
- Click "Reload" web app

### Error: "504 Bad Gateway"
- Click "Reload" web app
- Wait 30 seconds
- Refresh page

### Can't login
- Check username/password: `admin` / `admin@123`
- Make sure main.py uploaded correctly

### Data not saving
- Check database permissions in Files section
- Make sure you can write to `/home/YOUR_USERNAME/mysite/`

---

## **LIVE APP URL**

Once working:
```
https://YOURNAME.pythonanywhere.com
```

**Share this link with anyone!** They can fill incident reports! 🎉

---

## **Questions?**

1. Stuck on STEP 4? Make sure to replace `YOUR_USERNAME` with actual username
2. Stuck on STEP 5? Run the bash command exactly as shown
3. App still not working? Click "Reload" and wait 30 seconds

---

**You're done!** Your app is ONLINE and WORKING! 🚀
