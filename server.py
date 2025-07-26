from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi import Request, BackgroundTasks, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import PlainTextResponse

from db import get_todays_sms, engine
from models import NewSMSRequestBody
from sms import process_sms_wrapper
from utils import get_client_ip, get_whitelisted_ips, get_current_username, parse_request_body_utf8

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.post("/sms")
async def new_sms(request: Request, background_tasks: BackgroundTasks):
    if get_client_ip(request) not in get_whitelisted_ips():
        raise HTTPException(status_code=403)
    body = await parse_request_body_utf8(request)
    background_tasks.add_task(process_sms_wrapper, body)
    return PlainTextResponse("OK")


@app.get("/admin")
async def admin(request: Request, _: Annotated[str, Depends(get_current_username)]):
    async with AsyncSession(engine) as session:
        return templates.TemplateResponse("admin.jinja", {
            'request': request,
            "rows": await get_todays_sms(session)})