from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/positions")
async def positions_page(request: Request):
    context = {
        "positions": [],
    }
    return templates.TemplateResponse(request, "positions.html", context)
