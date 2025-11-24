# 🔧 Railway Deployment Fix

## ❌ Error You Saw

```
⚠ Script start.sh not found
✖ Railpack could not determine how to build the app.
```

## ✅ Solution Applied

I've created the necessary configuration files:

1. **`railway.toml`** - Railway configuration
2. **`nixpacks.toml`** - Build configuration
3. **`Procfile`** - Start command

---

## 🚀 Deploy to Railway NOW

### Step 1: Push Configuration Files

```bash
cd Healthcare-AI-Dashboard
git add .
git commit -m "fix: Add Railway configuration files"
git push origin main
```

### Step 2: Configure Railway Service

1. **Go to:** https://railway.app
2. **Login** with GitHub
3. **New Project** → "Deploy from GitHub repo"
4. **Select:** `healthcare-ai-dashboard`

### Step 3: Railway Will Auto-Detect

Railway will now see:
- ✅ `railway.toml` - Configuration
- ✅ `nixpacks.toml` - Build instructions
- ✅ `Procfile` - Start command
- ✅ `backend/requirements.txt` - Dependencies

### Step 4: Add Environment Variables

1. Click on your service
2. Go to **"Variables"** tab
3. Add:
   ```
   PORT=8000
   PYTHON_VERSION=3.11
   HUGGINGFACE_API_KEY=your_key_here (optional)
   ```

### Step 5: Add PostgreSQL Database

1. Click **"New"** in your project
2. Select **"Database"** → **"PostgreSQL"**
3. Railway auto-connects it ✅

### Step 6: Generate Domain

1. Go to **"Settings"** → **"Networking"**
2. Click **"Generate Domain"**
3. Copy your URL: `https://your-app.up.railway.app`

### Step 7: Deploy!

1. Railway automatically deploys
2. Wait 2-3 minutes
3. Check logs for "Application startup complete"
4. Done! ✅

---

## 🧪 Test Your Deployment

```bash
# Replace with YOUR Railway URL
BACKEND_URL="https://your-app.up.railway.app"

# Test health check
curl $BACKEND_URL/

# Should return:
# {"message":"Healthcare AI Dashboard API","status":"running"}

# Test API docs (open in browser)
open $BACKEND_URL/docs
```

---

## 📋 Configuration Files Explained

### `railway.toml`
Tells Railway:
- Use NIXPACKS builder
- Install dependencies from `backend/requirements.txt`
- Start with uvicorn command

### `nixpacks.toml`
Tells Nixpacks:
- Use Python 3.11
- Install from backend directory
- Run uvicorn on $PORT

### `Procfile`
Backup start command:
- Heroku-style process file
- Railway reads this if other configs fail

---

## 🔧 Alternative: Manual Configuration

If auto-detection still fails:

### In Railway Dashboard:

1. **Go to your service** → **"Settings"**

2. **Set Root Directory:**
   ```
   backend
   ```

3. **Set Build Command:**
   ```
   pip install -r requirements.txt
   ```

4. **Set Start Command:**
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

5. **Set Python Version:**
   - Variables tab → Add `PYTHON_VERSION=3.11`

6. **Redeploy**

---

## ✅ Success Indicators

### Build Logs Should Show:
```
✓ Detected Python app
✓ Installing dependencies...
✓ Successfully installed fastapi uvicorn sqlalchemy httpx...
✓ Build succeeded
✓ Deploying...
```

### Service Logs Should Show:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Health Check Should Work:
```bash
curl https://your-app.up.railway.app/
# {"message":"Healthcare AI Dashboard API","status":"running"}
```

---

## 🎯 Quick Deployment Checklist

- [ ] Push configuration files to GitHub
- [ ] Sign up at railway.app
- [ ] Create new project from GitHub
- [ ] Railway auto-detects configuration
- [ ] Add environment variables (PORT, PYTHON_VERSION)
- [ ] Add PostgreSQL database
- [ ] Generate domain
- [ ] Wait for deployment (2-3 min)
- [ ] Test health check
- [ ] Test API docs
- [ ] Update GitHub README with live URL

---

## 💡 Pro Tips

### 1. Check Build Logs
If deployment fails:
- Click on your service
- Go to "Deployments" tab
- Click latest deployment
- Check "Build Logs" for errors

### 2. Check Service Logs
If app crashes:
- Go to "Logs" tab
- Look for Python errors
- Check for missing environment variables

### 3. Redeploy
If something goes wrong:
- Settings → "Redeploy"
- Or push empty commit to GitHub

### 4. Monitor Usage
- Dashboard → "Usage" tab
- See current month's usage
- $5 free credit should cover demo

---

## 🆘 Troubleshooting

### Issue: "Could not determine how to build"
**Fix:** Configuration files are now added. Push to GitHub and redeploy.

### Issue: "Module not found"
**Fix:** Check that `backend/requirements.txt` has all dependencies.

### Issue: "Port binding error"
**Fix:** Make sure start command uses `$PORT` variable.

### Issue: "Database connection error"
**Fix:** Add PostgreSQL database in Railway dashboard.

---

## 📊 What Railway Will Do

1. **Detect** Python app from configuration files
2. **Install** Python 3.11
3. **Install** dependencies from `backend/requirements.txt`
4. **Start** uvicorn server on $PORT
5. **Connect** to PostgreSQL database
6. **Generate** public URL
7. **Deploy** your app ✅

---

## 🎯 Expected Timeline

- **Push to GitHub:** 30 seconds
- **Railway detects changes:** 10 seconds
- **Build process:** 2-3 minutes
- **Deployment:** 30 seconds
- **Total:** ~4 minutes ✅

---

## 📱 After Deployment

### Update GitHub README:
```markdown
## 🌐 Live Demo
**Backend:** https://smart-hospital.up.railway.app
**API Docs:** https://smart-hospital.up.railway.app/docs

Deployed on Railway with:
- Zero cold starts
- Auto-scaling
- Production PostgreSQL
```

### Test All Features:
```bash
# Create patient
curl -X POST "https://your-app.up.railway.app/api/v1/patients" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "age": 45, "medical_record_number": "MRN001"}'

# Log vitals
curl -X POST "https://your-app.up.railway.app/api/v1/patients/1/metrics" \
  -H "Content-Type: application/json" \
  -d '{"heart_rate": 75, "blood_pressure": "120/80", "temperature": 98.6, "oxygen_saturation": 98.0}'

# Get prediction
curl -X POST "https://your-app.up.railway.app/api/v1/predictions" \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1}'

# Get triage
curl "https://your-app.up.railway.app/api/v1/triage"
```

---

## ✅ You're All Set!

**Configuration files are ready. Now:**

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "fix: Add Railway configuration"
   git push origin main
   ```

2. **Deploy on Railway:**
   - Go to railway.app
   - New Project → Deploy from GitHub
   - Select your repo
   - Add PostgreSQL
   - Generate domain
   - Done! ✅

**Your app will be live in 4 minutes! 🚀**
