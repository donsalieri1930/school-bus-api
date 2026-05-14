from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi import Request, BackgroundTasks, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import PlainTextResponse
from starlette.responses import RedirectResponse

from db import get_todays_sms, engine, get_emails
from models import NewSMSRequestBody
from sms import process_sms_wrapper
from utils import get_client_ip, get_whitelisted_ips, get_current_username, parse_request_body_utf8, group_list_by_key, parse_list

app = FastAPI()
templates = Jinja2Templates(directory="templates")

templates.env.filters['parse_list'] = parse_list


@app.post("/sms")
async def new_sms(request: Request, background_tasks: BackgroundTasks):
    if get_client_ip(request) not in get_whitelisted_ips():
        raise HTTPException(status_code=403)
    body = await parse_request_body_utf8(request)
    background_tasks.add_task(process_sms_wrapper, body)
    return PlainTextResponse("OK")


@app.get("/admin")
async def new_admin_beta(request: Request, _: Annotated[str, Depends(get_current_username)]):
    async with AsyncSession(engine) as session:
        sms_rows = await get_todays_sms(session)
        grouped_rows = group_list_by_key(sms_rows, lambda r: r.lineCode)

        email_rows = await get_emails(session)
        grouped_emails = group_list_by_key(email_rows, lambda e: e.lineCode)
        return templates.TemplateResponse("admin2.jinja", {
            "request": request,
            "grouped_rows": grouped_rows,
            "grouped_emails": grouped_emails,
        })


@app.head("/status")
async def status():
    return "OK"


@app.get('/')
def home():
    return RedirectResponse('/admin')
