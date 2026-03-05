# SecRAG AI

AI-powered security log intelligence platform for:
- anomaly detection on log datasets (Isolation Forest)
- contextual security analysis (RAG with ChromaDB)
- LLM-based incident explanation (Ollama + Llama)

SecRAG AI provides a full-stack workflow from raw CSV logs to actionable security insights.

## Why This Project
Security teams often have two gaps:
1. Detecting unusual behavior at scale.
2. Explaining what those anomalies actually mean.

SecRAG AI combines ML detection and RAG + LLM reasoning to bridge both.

## Core Capabilities
- Dataset upload and validation (CSV)
- Model training and model registry management
- Detection run on new/unseen log files
- AI-generated explanation with OWASP/security context
- Dashboard UI for end-to-end workflow

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy + PostgreSQL
- scikit-learn (Isolation Forest)
- ChromaDB (vector retrieval)
- Ollama (local LLM inference)

### Frontend
- React + TypeScript + Vite
- TailwindCSS
- React Router
- Axios
- TanStack React Query

## Architecture Flow

```text
Upload Dataset -> Train Model -> Run Detection -> Generate AI Insights

1) CSV logs are uploaded and stored with metadata
2) Isolation Forest model is trained and saved as artifacts
3) New logs are scored for anomalies
4) Anomaly rows are sent to RAG + LLM pipeline for explanation
```

## Repository Structure

```text
ai-log-analyzer/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # FastAPI endpoints
│   │   ├── core/              # Config, database, logging
│   │   ├── llm_engine/        # Ollama client + prompt builder
│   │   ├── ml_engine/         # Feature engineering, trainer, detector
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── rag_engine/        # Knowledge base + retrieval
│   │   └── services/          # Application orchestration layer
│   ├── pyproject.toml
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── api/               # Axios clients per module
│   │   ├── components/layout/ # Sidebar, Navbar, DashboardLayout
│   │   ├── hooks/             # React Query hooks
│   │   ├── pages/             # Dashboard/Datasets/Models/Detection/Insights
│   │   ├── routes/            # AppRouter
│   │   ├── types/             # Shared TypeScript types
│   │   └── utils/             # Format helpers
│   └── package.json
└── README.md
```

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL running on `localhost:5432`
- Ollama (for `/api/v1/explain`)

## 1) Backend Setup

```bash
cd backend
poetry install
```

### Create Database/User (one-time)

```sql
CREATE USER secrag WITH PASSWORD 'secrag';
CREATE DATABASE secrag_db OWNER secrag;
```

### Environment (`backend/.env`)

Default values:

```env
APP_ENV=development
APP_DEBUG=True
DATABASE_URL=postgresql://secrag:secrag@localhost:5432/secrag_db
UPLOAD_DIR=./uploads
MODELS_DIR=./stored_models
CHROMA_PERSIST_DIR=./chroma_db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
OLLAMA_TIMEOUT=120
LOG_LEVEL=INFO
```

### Run Backend

```bash
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend URLs:
- API Docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## 2) Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:
- `http://localhost:5173`

### Frontend API Base URL
By default frontend uses:
- `http://127.0.0.1:8000/api/v1`

You can override with `VITE_API_BASE_URL` if needed.

## 3) Ollama Setup (Insights Feature)

```bash
ollama serve
ollama pull llama3
```

Check Ollama:
```bash
curl http://localhost:11434/api/tags
```

## End-to-End Usage (UI)

1. Open `/datasets`
- Upload a CSV dataset

2. Open `/models`
- Train an Isolation Forest model on uploaded dataset
- Ensure model status becomes `ready`

3. Open `/detection`
- Select a ready model
- Upload inference CSV
- Run detection
- Review anomaly count, ratio, and anomaly rows

4. Open `/insights`
- Generate AI explanation from latest detection result
- Review attack type, severity, explanation, recommended fix, OWASP mapping

## API Surface (Current)

### Datasets
- `POST /api/v1/datasets/upload`
- `GET /api/v1/datasets/`
- `GET /api/v1/datasets/{dataset_id}`
- `DELETE /api/v1/datasets/{dataset_id}`

### Models
- `POST /api/v1/models/train`
- `GET /api/v1/models/`
- `GET /api/v1/models/{model_id}`
- `DELETE /api/v1/models/{model_id}`

### Detection
- `POST /api/v1/detect/`
- `GET /api/v1/detect/`
- `GET /api/v1/detect/{run_id}`

### Explain
- `POST /api/v1/explain/`
- `GET /api/v1/explain/health`
- `POST /api/v1/explain/reload-kb`

## Sample CSV for Quick Testing

```csv
status_code,response_time_ms,method,endpoint,user_role,failed_login_count
200,120,GET,/api/profile,user,0
200,95,GET,/api/dashboard,user,0
401,140,POST,/api/login,unknown,3
403,180,GET,/api/admin,user,0
500,900,POST,/api/export,admin,0
200,110,GET,/api/profile,user,0
429,320,POST,/api/login,unknown,8
200,130,GET,/api/orders,user,0
503,1200,GET,/api/reports,admin,0
200,100,GET,/api/home,user,0
```

## Troubleshooting

### `connection to server at "localhost", port 5432 failed`
PostgreSQL is not running or DB/user is missing.
- Start PostgreSQL service
- Ensure `DATABASE_URL` matches your local DB
- Create user/database if not created

### `Ollama is not running at http://localhost:11434`
Run:
```bash
ollama serve
ollama pull llama3
```

### Frontend error: `timeout of 20000ms exceeded` on insights
LLM responses can take longer than default frontend timeout.
- Increase request timeout for insights call in `frontend/src/api/insightsApi.ts`
- Optionally increase `OLLAMA_TIMEOUT` in `backend/.env`

## Development Notes
- This project is under active development.
- Detection + Insights UI flow is implemented.
- Next improvements: better detection history persistence in UI, richer charts, auth, and deployment hardening.

## Security Note
Do not commit real secrets. Keep `.env` local and rotate credentials if exposed.

