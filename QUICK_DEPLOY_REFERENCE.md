# ⚡ Quick Deploy Reference Card

## Backend Configuration

```
Type: Web Service
Name: rag-chatbot-backend
Region: Oregon
Branch: main
Root Directory: backend/RAG_chatbot
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
Instance: Free
```

**Environment Variables:**
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=rag_chatbot
DB_USER=root
DB_PASSWORD=your_password
SECRET_KEY=your-secret-key-min-32-chars
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=llama3.2:latest
FRONTEND_URL=https://your-frontend.onrender.com
DEBUG=false
LOG_LEVEL=INFO
UPLOAD_PATH=./uploads
VECTOR_STORE_PATH=./vector_store
PYTHON_VERSION=3.11.0
```

---

## Frontend Configuration

```
Type: Static Site
Name: rag-chatbot-frontend
Branch: main
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: build
```

**Environment Variables:**
```env
REACT_APP_API_URL=https://your-backend.onrender.com/api/v1
REACT_APP_APP_NAME=AI RAG Chatbot
REACT_APP_VERSION=2.0.0
```

**Rewrite Rule:**
```
Source: /*
Destination: /index.html
Action: Rewrite
```

---

## Deployment Order

1. ✅ Deploy Backend first
2. ✅ Copy backend URL
3. ✅ Deploy Frontend with backend URL
4. ✅ Copy frontend URL
5. ✅ Update backend FRONTEND_URL
6. ✅ Test!

---

## Test URLs

- Health: `https://your-backend.onrender.com/health`
- API Docs: `https://your-backend.onrender.com/docs`
- Frontend: `https://your-frontend.onrender.com`

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Service sleeping | Normal on free tier (30s wake up) |
| Ollama not working | Use external AI API or Railway |
| CORS error | Update FRONTEND_URL in backend |
| Can't login | Check backend logs, verify DB |
| Blank page | Check rewrite rule, API URL |

---

**Full Guide**: See `MANUAL_RENDER_DEPLOY.md`
