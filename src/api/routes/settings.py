from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pathlib import Path

from src.config import get_settings

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/settings")
async def settings_page(request: Request):
    settings = get_settings()
    context = {
        "settings": {
            "max_risk_per_trade": settings.max_risk_per_trade * 100,
            "max_daily_loss": settings.max_daily_loss * 100,
            "max_portfolio_heat": settings.max_portfolio_heat * 100,
            "max_drawdown": settings.max_drawdown * 100,
            "max_sector_exposure": settings.max_sector_exposure * 100,
            "analysis_interval": settings.analysis_interval_minutes,
            "max_watchlist_size": settings.max_watchlist_size,
        },
        "agent_status": "ACTIVE",
    }
    return templates.TemplateResponse(request, "settings.html", context)
