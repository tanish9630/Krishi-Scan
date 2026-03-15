---
description: Start the Krishi Scan frontend and backend development servers
---

// turbo-all

## Start Krishi Scan Development Servers

### 1. Start the Backend (FastAPI)
Run from the project root:
```bash
source .venv/bin/activate && cd backend && uvicorn main:app --reload
```
Backend will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### 2. Start the Frontend (React + Vite)
In a new terminal, run from the project root:
```bash
cd frontend && npm run dev
```
Frontend will be available at: http://localhost:5173

### 3. Verify Both Are Running
Check backend health:
```bash
curl -s http://localhost:8000 | python3 -m json.tool
```

Check frontend is up:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173
```

### Notes
- The `.venv` virtual environment must exist. If not, run: `python3 -m venv .venv && source .venv/bin/activate && pip install -r backend/requirements.txt`
- Frontend dependencies: run `cd frontend && npm install` if `node_modules` is missing
- API Keys must be set in `.env` (copy from `.env.example`):
  - `GEMINI_API_KEY`
  - `OPENWEATHER_API_KEY`
