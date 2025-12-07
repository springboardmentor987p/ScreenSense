# 🚀 Screen Time Advisor - Deployment Guide

## Option 1: Deploy on GitHub Pages (Static Frontend Only)

### Step 1: Create GitHub Pages Branch
```powershell
cd C:\Users\Lenovo\OneDrive\Desktop\dona
git checkout -b gh-pages
```

### Step 2: Enable GitHub Pages
1. Go to: https://github.com/Dona-Sojan/screenspace-analysis
2. Click **Settings** → **Pages**
3. Select **Branch:** `gh-pages`
4. Click **Save**

### Step 3: Your Site URL
Your GitHub Pages site will be at:
```
https://Dona-Sojan.github.io/screenspace-analysis
```

---

## Option 2: Deploy on Heroku (Full App with Backend)

### Step 1: Install Heroku CLI
Download from: https://devcenter.heroku.com/articles/heroku-cli

### Step 2: Create Heroku App
```powershell
heroku login
heroku create your-app-name-screentime
```

### Step 3: Add Procfile
Create `Procfile` in your project root:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 4: Deploy
```powershell
git push heroku main
```

### Step 5: Your Live Link
```
https://your-app-name-screentime.herokuapp.com
```

---

## Option 3: Deploy on Vercel (Recommended - Free & Fast)

### Step 1: Push to GitHub
```powershell
git push origin main
```

### Step 2: Connect to Vercel
1. Go to: https://vercel.com
2. Click **New Project**
3. Import from GitHub: `screenspace-analysis`
4. Click **Deploy**

### Step 3: Your Live Link
```
https://screenspace-analysis.vercel.app
```

---

## Option 4: Deploy on Render (Free & Easy)

### Step 1: Go to Render
1. Visit: https://render.com
2. Click **New Web Service**
3. Connect GitHub repository

### Step 2: Configure
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
- **Environment:** Add your `GEMINI_API_KEY`

### Step 3: Deploy
Click **Deploy** and wait 2-3 minutes

### Step 4: Your Live Link
```
https://screenspace-analysis.onrender.com
```

---

## Option 5: Deploy on PythonAnywhere (Easiest for Python)

### Step 1: Create Account
Visit: https://www.pythonanywhere.com (Free tier available)

### Step 2: Upload Files
1. Click **Files**
2. Upload your project

### Step 3: Configure Web App
1. Add new web app (Flask/ASGI)
2. Point to `main.py`
3. Set Python version to 3.12

### Step 4: Your Live Link
```
https://yourusername.pythonanywhere.com
```

---

## Option 6: Deploy on Railway (Modern & Simple)

### Step 1: Go to Railway
1. Visit: https://railway.app
2. Click **New Project**
3. Deploy from GitHub

### Step 2: Auto-Configuration
Railway automatically detects Python + FastAPI

### Step 3: Add Secrets
- Go to **Variables**
- Add: `GEMINI_API_KEY=your_key_here`

### Step 4: Your Live Link
```
https://your-app.railway.app
```

---

## Quick Comparison

| Platform | Cost | Setup Time | Best For |
|----------|------|-----------|----------|
| GitHub Pages | Free | 5 min | Frontend only |
| Vercel | Free | 5 min | Full-stack |
| Render | Free | 10 min | Python apps |
| Heroku | Paid | 10 min | Long-running apps |
| Railway | Free tier | 10 min | Modern apps |
| PythonAnywhere | Free tier | 10 min | Simple Python |

---

## Getting Your GitHub Repository Link

### View Your Repository
```
https://github.com/Dona-Sojan/screenspace-analysis
```

### Clone Command (for others)
```
git clone https://github.com/Dona-Sojan/screenspace-analysis.git
```

### Raw File Links
View any file raw:
```
https://raw.githubusercontent.com/Dona-Sojan/screenspace-analysis/main/style.html
```

---

## Environment Variables Required

Before deploying, add these to your deployment platform:

```env
GEMINI_API_KEY=your-google-gemini-api-key-here
```

Get it from: https://ai.google.dev/

---

## Quick Start (Recommended: Vercel)

```powershell
# 1. Ensure all changes are committed
cd C:\Users\Lenovo\OneDrive\Desktop\dona
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Go to https://vercel.com
# 3. Sign up with GitHub
# 4. Click "New Project"
# 5. Select "screenspace-analysis"
# 6. Add GEMINI_API_KEY in Environment Variables
# 7. Click "Deploy"

# Your app will be live at: https://screenspace-analysis.vercel.app
```

---

## Troubleshooting

### API Key Not Working
- Make sure `GEMINI_API_KEY` is set in environment variables
- Don't include `export` or quotes

### Port Issues
- Cloud platforms assign dynamic ports
- Code already handles: `$PORT` or default `3000`

### Build Failures
- Create `requirements.txt` if missing:
  ```powershell
  pip freeze > requirements.txt
  ```

---

## Share Your Project

After deployment, share these links:

1. **GitHub Repo:** https://github.com/Dona-Sojan/screenspace-analysis
2. **Live Demo:** https://your-deployment-url.com
3. **Documentation:** Check `COMPREHENSIVE_DOCUMENTATION.md`

---

## Next Steps

1. Choose your deployment platform (Vercel recommended)
2. Add `GEMINI_API_KEY` to environment
3. Deploy and test
4. Share the live link!

**Your app will be live in minutes! 🎉**
