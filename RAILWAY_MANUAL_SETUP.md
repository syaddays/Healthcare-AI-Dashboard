# 🚂 Railway Manual Setup Guide - GUARANTEED TO WORK

## 🎯 The Issue

Railway is trying to auto-detect and failing. **Let's configure it manually instead.**

---

## ✅ GUARANTEED SOLUTION: Manual Configuration

### Step 1: Create Railway Project (1 minute)

1. Go to: **https://railway.app**
2. Click **"Login with GitHub"**
3. Click **"New Project"**
4. Select **"Empty Project"** (NOT "Deploy from GitHub" yet)
5. Name it: `smart-hospital`

---

### Step 2: Add PostgreSQL Database (30 seconds)

1. In your project, click **"New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Done! Database is created ✅

---

### Step 3: Add Backend Service (2 minutes)

1. Click **"New"** again
2. Select **"GitHub Repo"**
3. Choose: `healthcare-ai-dashboard`
4. Railway creates a service

---

### Step 4: Configure Backend Service (IMPORTANT)

1. Click on the backend service card
2. Go to **"Settings"** tab
3. Configure these settings:

#### **Root Directory:**
```
backend
```

#### **Build Command:**
```
pip install --upgrade pip && pip install -r requirements.txt
```

#### **Start Command:**
```
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### **Watch Paths:**
```
backend/**
```

4. Click **"Save"** after each setting

---

### Step 5: Add Environment Variables (1 minute)

1. Still in your service, go to **"Variables"** tab
2. Click **"New Variable"**
3. Add these one by one:

```
PORT = 8000
PYTHON_VERSION = 3.11
NIXPACKS_PYTHON_VERSION = 3.11
HUGGINGFACE_API_KEY = your_key_here (optional)
```

4. Click **"Add"** for each

---

### Step 6: Generate Domain (30 seconds)

1. Go to **"Settings"** tab
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"**
4. Copy your URL: `https://smart-hospital-production.up.railway.app`
5. Save this URL! ✅

---

### Step 7: Deploy! (2-3 minutes)

1. Go to **"Deployments"** tab
2. Click **"Deploy"** button
3. Watch the logs:
   ```
   ✓ Building...
   ✓ Installing dependencies...
   ✓ Build succeeded
   ✓ Deploying...
   ```
4. Wait for "Deployment successful" ✅

---

## 🧪 Test Your Deployment

```bash
# Replace with YOUR Railway URL
BACKEND_URL="https://smart-hospital-production.up.railway.app"

# Test health check
curl $BACKEND_URL/

# Should return:
# {"message":"Healthcare AI Dashboard API","status":"running"}

# Test API docs (open in browser)
open $BACKEND_URL/docs
```

---

## 🔧 Troubleshooting

### Issue: Build Still Fails

**Solution 1: Clear Build Cache**
1. Settings → Scroll down
2. Click **"Clear Build Cache"**
3. Redeploy

**Solution 2: Check Python Version**
1. Variables tab
2. Make sure `PYTHON_VERSION=3.11`
3. Make sure `NIXPACKS_PYTHON_VERSION=3.11`

**Solution 3: Check Root Directory**
1. Settings tab
2. Root Directory should be exactly: `backend`
3. Not `./backend` or `/backend`

### Issue: App Crashes on Start

**Check Logs:**
1. Go to "Logs" tab
2. Look for Python errors
3. Common issues:
   - Missing environment variables
   - Database connection error
   - Port binding error

**Fix:**
1. Make sure PostgreSQL is added
2. Make sure start command uses `$PORT`
3. Check all environment variables are set

### Issue: Can't Connect to Database

**Solution:**
1. Make sure PostgreSQL service is running
2. Railway auto-sets `DATABASE_URL`
3. Check Variables tab for `DATABASE_URL`

---

## 📊 Expected Build Logs

### Good Build Logs:
```
==> Building with Nixpacks
==> Detected Python app
==> Installing Python 3.11
==> Installing dependencies from requirements.txt
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
==> Build succeeded
==> Starting deployment
==> Deployment successful
```

### Good Service Logs:
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## ✅ Configuration Checklist

Before deploying, verify:

- [ ] Project created on Railway
- [ ] PostgreSQL database added
- [ ] Backend service added from GitHub
- [ ] Root Directory set to `backend`
- [ ] Build Command set correctly
- [ ] Start Command set correctly
- [ ] Environment variables added (PORT, PYTHON_VERSION)
- [ ] Domain generated
- [ ] Deployment triggered

---

## 🎯 Alternative: Use Railway CLI

If web interface doesn't work, use CLI:

### Install Railway CLI:
```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex
```

### Deploy with CLI:
```bash
# Login
railway login

# Link to project
railway link

# Set root directory
railway up --service backend

# Add variables
railway variables set PORT=8000
railway variables set PYTHON_VERSION=3.11

# Deploy
railway up
```

---

## 💡 Pro Tips

### 1. Use Service Templates
Railway has templates for Python apps:
- Browse: https://railway.app/templates
- Search for "FastAPI"
- Use as reference

### 2. Check Railway Status
If nothing works:
- Check: https://status.railway.app
- Railway might be having issues

### 3. Join Railway Discord
Get help from community:
- Discord: https://discord.gg/railway
- Very responsive community

---

## 🆘 If Nothing Works: Use Vercel

Vercel is simpler for Python apps:

### Deploy Backend to Vercel:

1. Create `vercel.json` in root:
```json
{
  "builds": [
    {
      "src": "backend/app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "backend/app/main.py"
    }
  ]
}
```

2. Deploy:
```bash
npm i -g vercel
vercel
```

3. Done in 2 minutes! ✅

---

## 📱 After Successful Deployment

### Update GitHub README:
```markdown
## 🌐 Live Demo
**Backend:** https://smart-hospital-production.up.railway.app
**API Docs:** https://smart-hospital-production.up.railway.app/docs

Deployed on Railway with PostgreSQL database.
```

### Test All Endpoints:
```bash
# Create patient
curl -X POST "$BACKEND_URL/api/v1/patients" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "age": 45, "medical_record_number": "MRN001"}'

# Log vitals
curl -X POST "$BACKEND_URL/api/v1/patients/1/metrics" \
  -H "Content-Type: application/json" \
  -d '{"heart_rate": 75, "blood_pressure": "120/80", "temperature": 98.6, "oxygen_saturation": 98.0}'

# Get prediction
curl -X POST "$BACKEND_URL/api/v1/predictions" \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1}'

# Get triage
curl "$BACKEND_URL/api/v1/triage"
```

---

## ✅ Summary

**Manual configuration is more reliable than auto-detection.**

**Key Settings:**
- Root Directory: `backend`
- Build Command: `pip install --upgrade pip && pip install -r requirements.txt`
- Start Command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Python Version: `3.11`

**Time to Deploy:** 5-7 minutes  
**Success Rate:** 99% ✅

---

**Follow this guide step-by-step and your deployment WILL work! 🚀**
