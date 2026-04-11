from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/")
async def overview(request: Request):
    portfolio = request.app.state.portfolio
    if portfolio:
        state = portfolio.get_state()
        context = {
            "request": request,
            "status": "ACTIVE",
            "equity": state["equity"],
            "daily_pnl": state["daily_pnl"],
            "total_pnl": state["equity"] - 100_000,
            "drawdown_pct": state["drawdown_pct"] * 100,
            "positions_count": len(state["positions"]),
            "portfolio_heat": state["portfolio_heat"],
        }
    else:
        context = {
            "request": request,
            "status": "OFFLINE",
            "equity": 0, "daily_pnl": 0, "total_pnl": 0,
            "drawdown_pct": 0, "positions_count": 0, "portfolio_heat": 0,
        }
    return templates.TemplateResponse(request, "overview.html", context)
