# 🚀 Quick Start Guide

## Current Status
✅ Backend: Running on http://localhost:8000 with llama3.2 model
✅ Frontend: Running on http://localhost:3000
✅ Database: SQLite (auto-fallback from MySQL)

## Test the App Right Now

1. **Open your browser**: http://localhost:3000
2. **Register a new account** (or use test account if created)
3. **Try chatting** - the llama3.2 model should respond now!

## For Future Runs

### Option 1: Double-click to start
```
start_production.bat
```

### Option 2: Manual start
```bash
# Terminal 1 - Backend
cd backend/RAG_chatbot
python main.py

# Terminal 2 - Frontend  
cd frontend
npm start
```

## Deploy to Production

See `DEPLOYMENT_GUIDE.md` for detailed deployment options:
- Docker Compose (easiest)
- Railway.app (free hosting)
- Render.com (free hosting)
- VPS deployment

## Current Configuration

**Model**: llama3.2:latest (2GB - lightweight)
**Database**: SQLite (local file)
**Storage**: Local filesystem

## Troubleshooting

**Chat not responding?**
- Check Ollama is running: `ollama list`
- Test model: `ollama run llama3.2:latest`

**Can't login?**
- Register a new account first
- Or run: `python create_test_user.py` (creates admin/admin123)

**Port already in use?**
- Backend: Change PORT in .env
- Frontend: Change port in package.json

## Next Steps

1. ✅ Test chat functionality
2. ✅ Upload documents to Knowledge Base
3. ✅ Try document-based Q&A
4. 📦 Deploy to production (see DEPLOYMENT_GUIDE.md)
