@echo off
echo ========================================
echo   Starting RAG Chatbot (Production)
echo ========================================
echo.

REM Start backend
echo [1/2] Starting Backend Server...
cd backend\RAG_chatbot
start "RAG Chatbot Backend" cmd /k "python main.py"
timeout /t 5 /nobreak >nul

REM Start frontend
echo [2/2] Starting Frontend Server...
cd ..\..\frontend
start "RAG Chatbot Frontend" cmd /k "npm start"

echo.
echo ========================================
echo   RAG Chatbot Started Successfully!
echo ========================================
echo.
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit this window...
pause >nul
