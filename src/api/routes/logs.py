from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/logs")
async def logs_page(request: Request):
    context = {
        "logs": [],
    }
    return templates.TemplateResponse(request, "logs.html", context)
