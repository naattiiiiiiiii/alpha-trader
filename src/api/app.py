from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from src.api.routes.dashboard import router as dashboard_router
from src.api.routes.positions import router as positions_router
from src.api.routes.history import router as history_router
from src.api.routes.signals import router as signals_router
from src.api.routes.settings import router as settings_router
from src.api.routes.logs import router as logs_router


def create_app() -> FastAPI:
    app = FastAPI(title="Alpha Trader", version="0.1.0")

    # Static files and templates
    static_dir = Path(__file__).parent / "static"
    templates_dir = Path(__file__).parent / "templates"
    static_dir.mkdir(exist_ok=True)
    templates_dir.mkdir(exist_ok=True)

    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Health endpoint
    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "alpha-trader"}

    # Routes
    app.include_router(dashboard_router)
    app.include_router(positions_router)
    app.include_router(history_router)
    app.include_router(signals_router)
    app.include_router(settings_router)
    app.include_router(logs_router)

    return app
