# SecRAG AI

SecRAG AI is a full-stack security log analysis platform.
It helps detect anomalies in logs and generate AI-based security explanations.

## Current Status
This project is actively under development.

## Features (Current)
- Upload CSV log datasets
- Train anomaly detection models
- Run detection on new logs
- Generate AI insights for detected anomalies

## Tech Stack
- Backend: FastAPI, PostgreSQL
- Frontend: React, TypeScript, TailwindCSS
- AI Layer: RAG + local LLM (Ollama)

## Quick Setup

### 1) Backend
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend docs: `http://127.0.0.1:8000/docs`

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend app: `http://localhost:5173`

### 3) Optional (AI Insights)
```bash
ollama serve
ollama pull llama3
```

## Basic Usage Flow
1. Upload dataset in `Datasets`
2. Train model in `Models`
3. Run detection in `Detection`
4. Generate explanation in `AI Insights`

## Notes
- Ensure PostgreSQL is running before starting backend.
- Keep `.env` files local and do not commit secrets.
