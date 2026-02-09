# 🚀 RAG Chatbot Deployment Guide

## Quick Deployment Options

### Option 1: Docker Compose (Recommended - Easiest)

**Prerequisites:**
- Docker Desktop installed
- Docker Compose installed

**Steps:**
```bash
# 1. Navigate to project directory
cd ai-rag-chatbot-python_v7

# 2. Start all services
docker-compose up -d

# 3. Check status
docker-compose ps

# 4. View logs
docker-compose logs -f

# 5. Stop services
docker-compose down
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

### Option 2: Cloud Deployment (Production)

#### A. Deploy to Railway.app (Free Tier Available)

**Backend Deployment:**
1. Go to https://railway.app
2. Sign up/Login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables from `.env` file
6. Railway will auto-detect Python and deploy

**Frontend Deployment:**
1. Create another service in same project
2. Select frontend folder
3. Add environment variable: `REACT_APP_API_URL=<your-backend-url>`
4. Deploy

#### B. Deploy to Render.com (Free Tier Available)

**Backend:**
1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repository
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables

**Frontend:**
1. New → Static Site
2. Build Command: `npm install && npm run build`
3. Publish Directory: `build`
4. Add environment variable: `REACT_APP_API_URL`

#### C. Deploy to Vercel (Frontend) + Railway (Backend)

**Frontend on Vercel:**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd frontend
vercel --prod
```

**Backend on Railway:**
- Follow Railway steps above

---

### Option 3: VPS Deployment (DigitalOcean, AWS, etc.)

**Requirements:**
- Ubuntu 20.04+ server
- Domain name (optional)
- SSH access

**Setup Script:**
```bash
# 1. SSH into your server
ssh user@your-server-ip

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Clone your repository
git clone <your-repo-url>
cd ai-rag-chatbot-python_v7

# 5. Configure environment
cp backend/RAG_chatbot/.env.example backend/RAG_chatbot/.env
nano backend/RAG_chatbot/.env  # Edit with your values

# 6. Deploy with Docker Compose
docker-compose up -d

# 7. Setup Nginx reverse proxy (optional)
sudo apt install nginx
sudo nano /etc/nginx/sites-available/chatbot
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

### Option 4: Windows Server Deployment

**Using IIS:**
1. Install IIS with URL Rewrite and ARR modules
2. Install Python 3.11+
3. Install Node.js 18+
4. Setup backend as Windows Service
5. Build frontend and serve with IIS

**Using PM2 (Easier):**
```bash
# Install PM2
npm install -g pm2

# Start backend
cd backend/RAG_chatbot
pm2 start main.py --name chatbot-backend --interpreter python

# Build and serve frontend
cd ../../frontend
npm run build
pm2 serve build 3000 --name chatbot-frontend

# Save PM2 configuration
pm2 save
pm2 startup
```

---

## Environment Variables Checklist

**Backend (.env):**
```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=rag_chatbot
DB_USER=root
DB_PASSWORD=your_password

# Security
SECRET_KEY=your-secret-key-here

# AI Model
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=llama3.2:latest

# CORS
FRONTEND_URL=http://your-frontend-url
```

**Frontend (.env):**
```env
REACT_APP_API_URL=http://your-backend-url/api/v1
REACT_APP_APP_NAME=AI RAG Chatbot
```

---

## Post-Deployment Checklist

- [ ] Backend health check: `curl http://your-backend/health`
- [ ] Frontend loads correctly
- [ ] User registration works
- [ ] Login works
- [ ] File upload works
- [ ] Chat functionality works
- [ ] Database connection stable
- [ ] Ollama model responding
- [ ] SSL certificate installed (production)
- [ ] Backups configured
- [ ] Monitoring setup

---

## Troubleshooting

**Backend won't start:**
- Check database connection
- Verify Ollama is running: `ollama list`
- Check logs: `docker-compose logs backend`

**Frontend can't connect to backend:**
- Verify CORS settings in backend
- Check `REACT_APP_API_URL` in frontend
- Ensure backend is accessible

**Database errors:**
- App will fallback to SQLite automatically
- For production, use MySQL/PostgreSQL

**Model errors:**
- Use smaller model: `llama3.2:latest` (2GB)
- Check Ollama: `ollama run llama3.2:latest`

---

## Recommended: Quick Deploy to Railway

**Fastest deployment (5 minutes):**

1. Push code to GitHub
2. Go to https://railway.app
3. New Project → Deploy from GitHub
4. Add services:
   - Backend (auto-detected Python)
   - Frontend (auto-detected Node.js)
   - MySQL database (from Railway templates)
5. Add environment variables
6. Deploy!

Railway provides:
- Free tier with 500 hours/month
- Automatic HTTPS
- Custom domains
- Easy scaling
- Built-in monitoring

---

## Need Help?

- Check logs: `docker-compose logs -f`
- Backend API docs: `http://localhost:8000/docs`
- Test endpoints: Use Postman or curl
