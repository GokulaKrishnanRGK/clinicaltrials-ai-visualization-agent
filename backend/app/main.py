from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.examples import router as examples_router
from app.routers.health import router as health_router
from app.routers.visualizations import router as visualizations_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(examples_router)
    app.include_router(visualizations_router)
    return app


app = create_app()
