# 🚀 Manual Render Deployment Guide

## Complete Step-by-Step Guide to Deploy Backend & Frontend Separately

---

## 📋 Prerequisites

✅ Code pushed to GitHub: https://github.com/vraj1091/RAG
✅ Render account (free): https://render.com
✅ 15 minutes of your time

---

## Part 1: Deploy Backend (Python FastAPI)

### Step 1: Create Web Service

1. **Go to Render Dashboard**: https://dashboard.render.com
2. Click **"New +"** button (top right)
3. Select **"Web Service"**

### Step 2: Connect Repository

1. Click **"Connect account"** if you haven't connected GitHub yet
2. Find and select your repository: **`vraj1091/RAG`**
3. Click **"Connect"**

### Step 3: Configure Backend Service

Fill in these settings:

**Basic Settings:**
```
Name: rag-chatbot-backend
Region: Oregon (US West) - Free
Branch: main
Root Directory: backend/RAG_chatbot
```

**Build & Deploy:**
```
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Instance Type:**
```
Instance Type: Free
```

### Step 4: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these one by one:

```
DB_HOST = localhost
DB_PORT = 3306
DB_NAME = rag_chatbot
DB_USER = root
DB_PASSWORD = your_secure_password_123
SECRET_KEY = your-super-secret-key-change-this-now-12345678
OLLAMA_BASE_URL = http://localhost:11434
OLLAMA_MODEL_NAME = llama3.2:latest
FRONTEND_URL = https://rag-chatbot-frontend.onrender.com
DEBUG = false
LOG_LEVEL = INFO
UPLOAD_PATH = ./uploads
VECTOR_STORE_PATH = ./vector_store
PYTHON_VERSION = 3.11.0
```

⚠️ **Important**: 
- Change `SECRET_KEY` to a random string (at least 32 characters)
- We'll update `FRONTEND_URL` later with the actual URL

### Step 5: Create Backend Service

1. Click **"Create Web Service"** button at the bottom
2. Wait for deployment (5-10 minutes)
3. Watch the logs - you should see:
   ```
   ✅ Application startup complete!
   Uvicorn running on http://0.0.0.0:8000
   ```

### Step 6: Copy Backend URL

1. Once deployed, you'll see your backend URL at the top
2. It will look like: `https://rag-chatbot-backend-XXXX.onrender.com`
3. **Copy this URL** - you'll need it for the frontend!

### Step 7: Test Backend

Visit these URLs to verify:
- Health check: `https://rag-chatbot-backend-XXXX.onrender.com/health`
- API docs: `https://rag-chatbot-backend-XXXX.onrender.com/docs`

You should see a response! ✅

---

## Part 2: Deploy Frontend (React)

### Step 1: Create Static Site

1. Go back to Render Dashboard
2. Click **"New +"** button
3. Select **"Static Site"**

### Step 2: Connect Same Repository

1. Select your repository: **`vraj1091/RAG`**
2. Click **"Connect"**

### Step 3: Configure Frontend Service

Fill in these settings:

**Basic Settings:**
```
Name: rag-chatbot-frontend
Branch: main
Root Directory: frontend
```

**Build Settings:**
```
Build Command: npm install && npm run build
Publish Directory: build
```

### Step 4: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these (replace XXXX with your actual backend URL):

```
REACT_APP_API_URL = https://rag-chatbot-backend-XXXX.onrender.com/api/v1
REACT_APP_APP_NAME = AI RAG Chatbot
REACT_APP_VERSION = 2.0.0
```

⚠️ **Critical**: Make sure to use your actual backend URL from Part 1, Step 6!

### Step 5: Add Rewrite Rules (Important!)

Scroll down to **"Redirects/Rewrites"** section:

Click **"Add Rule"**:
```
Source: /*
Destination: /index.html
Action: Rewrite
```

This ensures React Router works correctly!

### Step 6: Create Frontend Service

1. Click **"Create Static Site"** button
2. Wait for build (3-5 minutes)
3. Watch the logs for successful build

### Step 7: Copy Frontend URL

1. Once deployed, copy your frontend URL
2. It will look like: `https://rag-chatbot-frontend-YYYY.onrender.com`

---

## Part 3: Connect Backend & Frontend

### Step 1: Update Backend CORS

1. Go to your **Backend service** in Render
2. Click **"Environment"** in the left sidebar
3. Find `FRONTEND_URL` variable
4. Update it with your actual frontend URL:
   ```
   FRONTEND_URL = https://rag-chatbot-frontend-YYYY.onrender.com
   ```
5. Click **"Save Changes"**
6. Backend will automatically redeploy (1-2 minutes)

### Step 2: Verify Frontend Environment

1. Go to your **Frontend service** in Render
2. Click **"Environment"** in the left sidebar
3. Verify `REACT_APP_API_URL` has the correct backend URL
4. If you need to change it, update and click **"Save Changes"**

---

## 🎉 Your App is Live!

### Access Your App

- **Frontend**: https://rag-chatbot-frontend-YYYY.onrender.com
- **Backend API**: https://rag-chatbot-backend-XXXX.onrender.com
- **API Docs**: https://rag-chatbot-backend-XXXX.onrender.com/docs

### Test Your App

1. **Open Frontend URL** in your browser
2. **Register** a new account
3. **Login** with your credentials
4. **Try chatting** - type "hello"
5. **Upload a document** in Knowledge Base (optional)

---

## ⚠️ Important Notes

### Free Tier Limitations

1. **Services Sleep After 15 Minutes**
   - First request after sleep takes 30-60 seconds to wake up
   - This is normal for free tier
   - Upgrade to paid ($7/month) for always-on

2. **Ollama/AI Model Won't Work**
   - Render free tier can't run Ollama (needs GPU)
   - Chat will work but AI responses will fail
   - **Solutions**:
     - Use external AI API (OpenAI, Gemini)
     - Deploy Ollama on Railway instead
     - Upgrade to Render paid plan

3. **Database is Ephemeral**
   - SQLite file resets on service restart
   - For production, add PostgreSQL database
   - See "Add Database" section below

### Expected Warnings in Logs

These are normal and can be ignored:
```
⚠️ MySQL connection failed - Using SQLite fallback
⚠️ Cannot connect to Tally
⚠️ Ollama connection failed
```

---

## 🔧 Optional: Add PostgreSQL Database

For persistent data storage:

### Step 1: Create Database

1. In Render Dashboard, click **"New +"**
2. Select **"PostgreSQL"**
3. Configure:
   ```
   Name: rag-chatbot-db
   Database: rag_chatbot
   User: rag_user
   Region: Oregon (same as backend)
   Plan: Free
   ```
4. Click **"Create Database"**

### Step 2: Get Connection Details

1. Once created, click on the database
2. Scroll down to **"Connections"**
3. Copy the **"Internal Database URL"**

### Step 3: Update Backend Environment

1. Go to your **Backend service**
2. Click **"Environment"**
3. Update these variables:
   ```
   DB_HOST = <from connection string>
   DB_PORT = 5432
   DB_NAME = rag_chatbot
   DB_USER = rag_user
   DB_PASSWORD = <from connection string>
   ```
4. Or simply add:
   ```
   DATABASE_URL = <paste internal database URL>
   ```
5. Click **"Save Changes"**
6. Backend will redeploy with PostgreSQL!

---

## 🐛 Troubleshooting

### Backend Won't Start

**Check Logs:**
1. Go to Backend service
2. Click **"Logs"** tab
3. Look for errors

**Common Issues:**
- Missing environment variables → Add them
- Build timeout → Increase in settings
- Python version mismatch → Set `PYTHON_VERSION=3.11.0`

**Fix:**
```bash
# Test locally first
cd backend/RAG_chatbot
pip install -r requirements.txt
python main.py
```

### Frontend Shows Blank Page

**Check:**
1. Build logs for errors
2. Browser console (F12) for errors
3. `REACT_APP_API_URL` is correct

**Common Issues:**
- Wrong API URL → Update environment variable
- Missing rewrite rule → Add `/* → /index.html`
- Build failed → Check Node version

### Can't Login/Register

**Check:**
1. Backend is running (not sleeping)
2. CORS configured correctly
3. Frontend can reach backend

**Test:**
```bash
# Test backend directly
curl https://rag-chatbot-backend-XXXX.onrender.com/health

# Should return: {"status":"healthy"}
```

### Chat Not Responding

**Expected on Free Tier:**
- Ollama doesn't work on Render free tier
- You'll see: "Error loading model"

**Solutions:**
1. **Use OpenAI API** (recommended):
   - Get key from https://platform.openai.com
   - Add to backend env: `OPENAI_API_KEY=sk-...`
   
2. **Use Google Gemini** (free):
   - Get key from https://makersuite.google.com/app/apikey
   - Add to backend env: `GEMINI_API_KEY=...`

3. **Deploy on Railway** (better free tier with GPU)

---

## 📊 Monitor Your Deployment

### View Logs

**Backend:**
1. Go to Backend service
2. Click **"Logs"** tab
3. See real-time logs

**Frontend:**
1. Go to Frontend service
2. Click **"Logs"** tab
3. See build and deploy logs

### Check Metrics

1. Click **"Metrics"** tab
2. See CPU, Memory, Bandwidth usage
3. Monitor response times

### Set Up Alerts

1. Go to service settings
2. Click **"Notifications"**
3. Add email for deploy failures

---

## 💰 Cost Summary

**Free Tier (Current Setup):**
- Backend: Free (with sleep)
- Frontend: Free
- Database: Free (if added)
- **Total: $0/month**

**Paid Tier (Always On):**
- Backend: $7/month
- Frontend: Free
- Database: $7/month (optional)
- **Total: $7-14/month**

---

## 🎯 Next Steps

- [ ] Test all features
- [ ] Add custom domain (optional)
- [ ] Set up monitoring
- [ ] Configure external AI API
- [ ] Add PostgreSQL for production
- [ ] Set up backups

---

## 🆘 Need Help?

1. **Check Logs First** - Most issues show up in logs
2. **Test Backend API** - Use `/docs` endpoint
3. **Verify Environment Variables** - Make sure all are set
4. **Check Render Status** - https://status.render.com

---

## ✅ Deployment Checklist

### Backend
- [ ] Service created and deployed
- [ ] All environment variables added
- [ ] Health check passes
- [ ] API docs accessible
- [ ] Logs show no critical errors

### Frontend
- [ ] Static site created and deployed
- [ ] Environment variables set correctly
- [ ] Rewrite rule added
- [ ] Site loads in browser
- [ ] Can navigate between pages

### Integration
- [ ] Backend CORS configured with frontend URL
- [ ] Frontend API URL points to backend
- [ ] Can register new user
- [ ] Can login successfully
- [ ] Chat interface works

---

**🎉 Congratulations! Your RAG Chatbot is now live on Render!**

**Your URLs:**
- Frontend: `https://rag-chatbot-frontend-YYYY.onrender.com`
- Backend: `https://rag-chatbot-backend-XXXX.onrender.com`

Share your app with the world! 🚀
