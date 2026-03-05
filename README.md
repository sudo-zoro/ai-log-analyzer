# SecRAG AI – AI-Powered Security Log Intelligence Platform

SecRAG AI is a full-stack security analytics platform design to detect anomalies in system logs and provide intelligent, AI-generated explanations mapped to security frameworks such as the OWASP Top 10.

It leverages:
1. **Isolation Forest** (Machine Learning) for anomaly detection in raw logs.
2. **ChromaDB** (RAG Engine) to store and retrieve security context and attack patterns.
3. **Ollama** (Local LLM) to generate structured explanations of the detected anomalies.

---

## 🏗️ Project Structure
Currently, the **backend API** is fully built.

```text
secrag-ai/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # FastAPI endpoint controllers
│   │   ├── core/            # Config, database, logging setup
│   │   ├── llm_engine/      # Ollama client and prompt builder
│   │   ├── ml_engine/       # Feature engineering, Trainer, Detector
│   │   ├── models/          # SQLAlchemy Database Models (Dataset, MLModel, DetectionRun)
│   │   ├── rag_engine/      # ChromaDB Embedder and Knowledge Base
│   │   ├── services/        # Orchestration layer (Dataset, ML, Detection, LLM services)
│   │   └── main.py          # Application entrypoint
│   ├── .env                 # Environment variables
│   ├── pyproject.toml       # Poetry dependencies
│   └── uploads/ & models/   # Local storage for CSVs and Joblib models
```

---

## 🚀 How to Run the Backend

### Prerequisites
1. **Python 3.11+**
2. **PostgreSQL**: Must be running. The default `.env` assumes a DB named `secrag_db` with user `secrag` and password `secrag` running on `localhost:5432`.
   - *Example to create it via psql:*
     ```sql
     CREATE USER secrag WITH PASSWORD 'secrag';
     CREATE DATABASE secrag_db OWNER secrag;
     ```
3. **Ollama** (optional, but required for the `/api/v1/explain` endpoint):
   - Install [Ollama](https://ollama.com/)
   - Run: `ollama run llama3`

### Installation & Startup
Navigate to the `backend` directory and set up the Poetry environment:

```bash
cd backend

# 1. Install dependencies (including python-multipart for file uploads)
poetry install

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Start the FastAPI development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🧪 How to Test the API

Once the server is running, the interactive Swagger UI documentation is available at:
👉 **http://127.0.0.1:8000/docs**

### End-to-End Testing Flow

1. **Upload a Log Dataset**
   - Go to `POST /api/v1/datasets/upload`
   - Upload any CSV file containing logs (e.g., an export of Nginx, Apache, or generic application logs).
   - *Save the `id` returned in the response.*

2. **Train an Anomaly Detection Model**
   - Go to `POST /api/v1/models/train`
   - Click "Try it out" and provide:
     ```json
     {
       "dataset_id": "<the-id-from-step-1>",
       "model_name": "Test Isolation Forest",
       "n_estimators": 100,
       "contamination": 0.05
     }
     ```
   - *Save the `id` returned in the response. This is your `model_id`.*

3. **Run Detection on New Logs**
   - Go to `POST /api/v1/detect/`
   - Provide the `model_id` from Step 2.
   - Upload a CSV containing the new logs you want to scan for anomalies.
   - The API will return the detected anomalies (the rows flagged as `-1` by the Isolation Forest).

4. **Generate AI Explanations (Requires Ollama)**
   - Go to `POST /api/v1/explain/`
   - Paste the list of anomalies retrieved from Step 3 into the `anomaly_rows` field.
   - The RAG engine will pull relevant OWASP documentation from ChromaDB, feed it to `llama3` via Ollama, and return a structured JSON response identifying the attack type, severity, and recommended fixes.
