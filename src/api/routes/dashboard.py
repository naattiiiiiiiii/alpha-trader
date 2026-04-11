from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/")
async def overview(request: Request):
    # TODO: Wire to real portfolio data in integration task
    context = {
        "status": "ACTIVE",
        "equity": 100_000.00,
        "daily_pnl": 0.00,
        "total_pnl": 0.00,
        "drawdown_pct": 0.0,
        "positions_count": 0,
        "portfolio_heat": 0.0,
    }
    return templates.TemplateResponse(request, "overview.html", context)
