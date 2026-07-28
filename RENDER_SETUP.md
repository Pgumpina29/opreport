# Render Deployment Guide

## **5 SIMPLE STEPS (10 minutes)**

---

### **STEP 1: Go to Render**
1. Visit: https://render.com
2. Click **"Sign Up"** (or login if you have account)
3. Use GitHub to sign up (easiest)

---

### **STEP 2: Create New Web Service**
1. Click **"New +"** → **"Web Service"**
2. Click **"Deploy from GitHub"** 
3. Connect your GitHub account
4. Find repo: **Pgumpina29/opreport**
5. Click **"Connect"**

---

### **STEP 3: Configure**
Fill in:
- **Name:** `opreport`
- **Environment:** Python 3
- **Build Command:** (should auto-fill from render.yaml)
- **Start Command:** (should auto-fill from render.yaml)
- **Plan:** FREE (blue button)

Click **"Create Web Service"**

---

### **STEP 4: Wait for Deploy**
- Watch status: "Building..." → "Deploying..." → "Live" ✅
- Takes 2-3 minutes
- You'll get a live URL like: `https://opreport-xxx.onrender.com`

---

### **STEP 5: Test Your App**

Visit your Render URL and test:
1. **Login page** loads ✅
2. Login: `admin` / `admin@123` ✅
3. **Entry form** appears ✅
4. Fill form and click **Save** ✅
5. Click **Report** and see data ✅

---

## **IF IT DOESN'T WORK:**

### **Error: "Application failed to respond"**
- Go to Render dashboard
- Check "Logs" (bottom of page)
- Look for red error messages
- Common fix: Wait 3 minutes and refresh

### **Error: "ModuleNotFoundError"**
- Check requirements.txt has all packages
- Render should auto-install from requirements.txt
- Wait and refresh

### **Data not saving**
- Check using SQLite database (local file)
- Should auto-create: `section_cases.db`
- Data persists on Render free tier

---

## **YOUR LIVE URL:**
```
https://opreport-xxx.onrender.com
```

**SHARE THIS WITH ANYONE** - they can fill incident reports! 🎉

---

**Follow the 5 steps above and you're LIVE!**
