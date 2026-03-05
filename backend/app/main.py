from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.database import init_db
from app.api.router import api_router

# Setup logging before anything else
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("Starting %s v%s [%s]", settings.APP_NAME, settings.APP_VERSION, settings.APP_ENV)

    # Ensure storage directories exist
    settings.ensure_directories()

    # Initialize database tables (dev mode; prod uses Alembic)
    try:
        init_db()
        logger.info("Database tables initialized.")
    except Exception as e:
        logger.warning("DB init skipped (may need migrations): %s", e)

    # Pre-load the security knowledge base into ChromaDB
    try:
        from app.rag_engine.embedder import load_knowledge_base
        count = load_knowledge_base()
        logger.info("Security knowledge base ready (%d documents).", count)
    except Exception as e:
        logger.warning("Knowledge base pre-load skipped: %s", e)

    yield

    logger.info("SecRAG shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Security Log Intelligence Platform — Anomaly Detection + RAG + LLM",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def health():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_detailed():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "ollama_url": settings.OLLAMA_BASE_URL,
        "ollama_model": settings.OLLAMA_MODEL,
        "upload_dir": settings.UPLOAD_DIR,
        "models_dir": settings.MODELS_DIR,
    }