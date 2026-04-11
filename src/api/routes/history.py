from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/history")
async def history_page(request: Request):
    context = {
        "trades": [],
        "stats": {"win_rate": 0, "avg_win": 0, "avg_loss": 0, "profit_factor": 0, "total_trades": 0},
    }
    return templates.TemplateResponse(request, "history.html", context)
