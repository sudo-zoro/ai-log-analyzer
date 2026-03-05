"""
Ollama LLM Client — makes HTTP calls to a local Ollama instance.
"""
import httpx
import json
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def call_ollama(prompt: str, system_prompt: str = "") -> str:
    """
    Send a prompt to Ollama and return the generated text.
    Uses the /api/generate endpoint (non-streaming).
    """
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    if system_prompt:
        payload["system"] = system_prompt

    try:
        with httpx.Client(timeout=settings.OLLAMA_TIMEOUT) as client:
            response = client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
    except httpx.ConnectError:
        logger.error("Cannot connect to Ollama at %s", settings.OLLAMA_BASE_URL)
        raise RuntimeError(
            f"Ollama is not running at {settings.OLLAMA_BASE_URL}. "
            "Start it with: ollama serve"
        )
    except httpx.TimeoutException:
        logger.error("Ollama request timed out after %ds", settings.OLLAMA_TIMEOUT)
        raise RuntimeError("Ollama inference timed out. Try a smaller model or increase OLLAMA_TIMEOUT.")
    except Exception as e:
        logger.error("Ollama call failed: %s", e)
        raise RuntimeError(f"Ollama error: {str(e)}")


def check_ollama_health() -> dict:
    """Check if Ollama is running and the configured model is available."""
    try:
        with httpx.Client(timeout=5) as client:
            resp = client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            models = [m["name"] for m in data.get("models", [])]
            return {
                "status": "online",
                "available_models": models,
                "configured_model": settings.OLLAMA_MODEL,
                "model_ready": any(settings.OLLAMA_MODEL in m for m in models),
            }
    except Exception as e:
        return {"status": "offline", "error": str(e)}
