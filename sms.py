import logging

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from config import SMSAPI
from dates import *
from db import get_family_data, engine, insert_sms_record
from errors import *
from models import NewSMSRequestBody
from utils import name_in_text, create_confirmation_message

sms_logger = logging.getLogger('sms')


async def send_sms_async(to: str, message: str) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.post(
            "https://api.smsapi.pl/sms.do",
            headers={"Authorization": f"Bearer {SMSAPI}"},
            params={
                "to": to,
                "message": message,
                "encoding": "utf-8",
            }
        )


async def process_sms(body: NewSMSRequestBody, session: AsyncSession) -> None:
    """
    Validate, process and respond to new SMS request.
    :raises: errors.SMSValidationError
    """
    # Find all dates, including string aliases.
    dates = find_all_dates(body.sms_text)
    # Create a list of days or raise errors.SMSValidationError
    match dates:
        case []:
            raise NoDateFoundError()
        case [single]:
            # Validate single date
            validate_date(single)
            validate_time(single)
            days = [single[1]]
        case [start, end]:
            # Validate a range, start by validating start and end separately.
            validate_date(start)
            validate_time(start)
            validate_range(start, end)
            days = create_date_range(start, end)
        case _:
            raise TooManyDatesError(', '.join([d[0] for d in dates]))

    # Find all children and their bus lines for the given parent phone number.
    family = await get_family_data(body.sms_from[-9:], session)
    if not family: raise NoChildrenRegisteredError()

    # Find children whose names are in the message. Matching is
    # case-insensitive and ignores diacritics.
    family_matched = list(filter(lambda r: name_in_text(r.childFirstName, body.sms_text), family))

    if not family_matched:
        raise NoChildrenNameError(
            ', '.join(set([row.childFirstName for row in family])))

    # For every child, line, day add a new record.
    for row in family_matched:
        for day in days:
            await insert_sms_record(session,
                                    body.sms_date,
                                    body.sms_from,
                                    day,
                                    body.sms_text,
                                    row.childId,
                                    row.lineId)
    await send_sms_async(body.sms_from, create_confirmation_message(family_matched, dates))


async def process_sms_wrapper(body: NewSMSRequestBody) -> None:
    """
    Call process_sms with an asynchronous database session. Handle
    internal errors and log results.
    """
    async with AsyncSession(engine) as session:
        try:
            await process_sms(body, session)
            sms_logger.info(f'{body.sms_from}:{repr(body.sms_text)}:OK')
            print('ok')
        except SMSValidationError as e:
            print(e.message)
            sms_logger.info(f'{body.sms_from}:{repr(body.sms_text)}:{e.__class__.__name__}({e.param})')
            await send_sms_async(body.sms_from, e.message)