# 🚂 Railway Deployment Guide - 5 Minutes

## 🎯 Why Railway?

Render has Python 3.13 Rust compilation issues. **Railway works perfectly and deploys in 5 minutes.**

---

## 🚀 Step-by-Step Deployment

### **Step 1: Sign Up (1 minute)**

1. Go to: **https://railway.app**
2. Click **"Login with GitHub"**
3. Authorize Railway to access your repos
4. Add credit card (required but **won't charge** on free tier)
   - You get **$5 free credit/month**
   - Your app uses ~$3-4/month
   - **Net cost: $0**

---

### **Step 2: Create Project (1 minute)**

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select: **`healthcare-ai-dashboard`**
4. Railway auto-detects it's a Python app ✅

---

### **Step 3: Configure Backend (2 minutes)**

1. Railway creates a service automatically
2. Click on the service card
3. Go to **"Settings"** tab
4. Configure:
   ```
   Root Directory: backend
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. Click **"Save"**

---

### **Step 4: Add Database (30 seconds)**

1. Click **"New"** button in your project
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Railway automatically:
   - Creates database
   - Connects it to your service
   - Sets DATABASE_URL environment variable
5. Done! ✅

---

### **Step 5: Environment Variables (30 seconds)**

1. Go to your backend service
2. Click **"Variables"** tab
3. Add these variables:
   ```
   PORT = 8000
   PYTHON_VERSION = 3.11
   HUGGINGFACE_API_KEY = your_key_here (optional)
   ```
4. Click **"Save"**

---

### **Step 6: Generate Domain (30 seconds)**

1. Go to **"Settings"** tab
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"**
4. Copy your URL: `https://your-app.up.railway.app`
5. Save this URL! ✅

---

### **Step 7: Deploy! (2-3 minutes)**

1. Railway automatically starts deploying
2. Watch the **"Deployments"** tab
3. Wait for:
   ```
   ✓ Building...
   ✓ Build succeeded
   ✓ Deploying...
   ✓ Deployment successful
   ```
4. Check **"Logs"** tab for:
   ```
   INFO: Application startup complete
   ```

---

## ✅ Verify Deployment

### Test Your Backend:

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

## 🎨 Deploy Frontend (Optional)

### Option 1: Vercel (Recommended)

1. Go to: **https://vercel.com**
2. Sign up with GitHub
3. **"New Project"** → Import your repo
4. Configure:
   ```
   Root Directory: frontend
   Framework: Create React App
   Build Command: npm run build
   Output Directory: build
   ```
5. Add Environment Variable:
   ```
   REACT_APP_API_URL = https://your-app.up.railway.app
   ```
6. Deploy!
7. Done in 2 minutes! ✅

### Option 2: Railway (Same Platform)

1. In same Railway project, click **"New"**
2. Select **"GitHub Repo"** → Same repo
3. Configure:
   ```
   Root Directory: frontend
   Build Command: npm install && npm run build
   Start Command: npx serve -s build -l $PORT
   ```
4. Add Environment Variable:
   ```
   REACT_APP_API_URL = https://your-backend.up.railway.app
   ```
5. Generate domain
6. Done! ✅

---

## 💰 Cost Breakdown

### Railway Free Tier:
- **$5 credit/month** (automatically applied)
- **Backend:** ~$3/month
- **Database:** ~$1/month
- **Total:** ~$4/month
- **Your cost:** **$0** (covered by free credit)

### After Free Credit:
- Pay only for what you use
- ~$5-10/month for small apps
- Can pause services when not in use

---

## 🔧 Troubleshooting

### Issue: Build Failed
**Check:**
- Root directory is set to `backend`
- requirements.txt exists
- Start command is correct

**Fix:**
- Go to Settings → Redeploy

### Issue: Database Connection Error
**Check:**
- PostgreSQL service is running
- DATABASE_URL is set automatically

**Fix:**
- Restart both services

### Issue: Port Binding Error
**Check:**
- Start command uses `$PORT` variable
- Not hardcoded to 8000

**Fix:**
- Update start command to use `$PORT`

---

## 📊 Railway vs Render

| Feature | Railway | Render |
|---------|---------|--------|
| **Setup Time** | 5 min | 10 min |
| **Python 3.13 Issues** | ✅ None | ❌ Has issues |
| **Cold Starts** | ✅ None | ❌ 30 sec |
| **Build Time** | 2-3 min | 5-7 min |
| **Free Tier** | $5 credit | Unlimited |
| **Credit Card** | Required | Not required |
| **Reliability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**Winner: Railway** (for hackathon demos)

---

## 🎯 Quick Commands

```bash
# 1. Push to GitHub
git add .
git commit -m "feat: Deploy to Railway"
git push origin main

# 2. Deploy on Railway
# - Go to railway.app
# - New Project → Deploy from GitHub
# - Select repo
# - Add PostgreSQL
# - Generate domain

# 3. Test deployment
curl https://your-app.up.railway.app/

# 4. Update README
# Add your live URLs
```

---

## 📱 Update Your Project

### GitHub README:
```markdown
## 🌐 Live Demo

**Backend:** https://smart-hospital.up.railway.app  
**API Docs:** https://smart-hospital.up.railway.app/docs  
**Frontend:** https://smart-hospital.vercel.app

Deployed on Railway + Vercel for optimal performance.
```

### LinkedIn Post:
```
🚀 Just deployed my Smart Hospital AI Dashboard!

Live demo: https://smart-hospital.up.railway.app

Built with FastAPI, React, and Mistral-7B LLM.
Deployed on Railway for zero cold starts and 99.9% uptime.

#HealthTech #AI #CloudDeployment
```

---

## ✅ Deployment Checklist

- [ ] Sign up at railway.app
- [ ] Add credit card (won't charge)
- [ ] Create project from GitHub
- [ ] Set root directory to `backend`
- [ ] Add PostgreSQL database
- [ ] Set environment variables (PORT, PYTHON_VERSION)
- [ ] Generate domain
- [ ] Wait for deployment (2-3 min)
- [ ] Test health check endpoint
- [ ] Test API docs
- [ ] Deploy frontend (Vercel or Railway)
- [ ] Update GitHub README with live URLs
- [ ] Test all features work
- [ ] Share with team

---

## 🎬 Video Tutorial

Railway has excellent docs:
- **Getting Started:** https://docs.railway.app/getting-started
- **Deploy from GitHub:** https://docs.railway.app/deploy/deployments
- **Environment Variables:** https://docs.railway.app/develop/variables

---

## 💡 Pro Tips

### 1. Monitor Your App
- Railway Dashboard → Your Service → "Metrics"
- See CPU, Memory, Network usage
- Monitor costs in real-time

### 2. View Logs
- Railway Dashboard → Your Service → "Logs"
- Real-time application logs
- Filter by severity

### 3. Redeploy Easily
- Push to GitHub → Auto-redeploys
- Or click "Redeploy" in Railway dashboard

### 4. Pause When Not Using
- Settings → "Pause Service"
- Saves credits when not demoing
- Resume instantly when needed

---

## 🆘 Need Help?

### Railway Resources:
- **Docs:** https://docs.railway.app
- **Discord:** https://discord.gg/railway
- **Twitter:** @Railway
- **Status:** https://status.railway.app

### Common Questions:

**Q: Will I be charged?**  
A: No, $5 free credit covers your demo. You'll get email if credit runs low.

**Q: Can I remove credit card later?**  
A: Yes, but service will pause when free credit runs out.

**Q: How do I check my usage?**  
A: Dashboard → "Usage" tab shows current month's usage.

**Q: Can I deploy multiple apps?**  
A: Yes! $5 credit is shared across all projects.

---

## 🎯 Summary

**Time to Deploy:** 5 minutes  
**Cost:** $0 (free credit)  
**Difficulty:** ⭐ Easy  
**Reliability:** ⭐⭐⭐⭐⭐  
**Performance:** ⭐⭐⭐⭐⭐  

**Perfect for hackathon demos! 🚀**

---

## 🚀 Deploy Now!

1. Go to: **https://railway.app**
2. Login with GitHub
3. Deploy from repo
4. Add PostgreSQL
5. Generate domain
6. **Done in 5 minutes!** ✅

---

**Your Smart Hospital AI Dashboard will be live, fast, and reliable! 💪**
