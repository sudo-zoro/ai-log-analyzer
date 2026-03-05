from fastapi import APIRouter
from app.api.routes import datasets, models, detect, explain

api_router = APIRouter()

api_router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
api_router.include_router(models.router, prefix="/models", tags=["Models"])
api_router.include_router(detect.router, prefix="/detect", tags=["Detection"])
api_router.include_router(explain.router, prefix="/explain", tags=["Explain"])
