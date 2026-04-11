from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/signals")
async def signals_page(request: Request):
    context = {
        "signals": [],
    }
    return templates.TemplateResponse(request, "signals.html", context)
