@echo off
echo Starting Complexity Analyzer...

echo Starting Backend (FastAPI)...
start "Backend" cmd /k "call .venv\Scripts\activate && uvicorn src.server.main:app --reload --port 8000"

echo Starting Frontend (Vite)...
cd web_app
start "Frontend" cmd /k "npm run dev"
cd ..

echo Done! Access the app at http://localhost:5173
