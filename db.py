from datetime import datetime, date
from pathlib import Path
from typing import List

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import text

from config import DATABASE
from models import FamilyRow, SMSRow

engine = create_async_engine(DATABASE, echo=False)


async def get_family_data(tel: str, session: AsyncSession) -> List[FamilyRow]:
    """
    Fetch all children records linked to a given parent phone number.
    :param tel: Parent phone number
    :param session: SQLAlchemy asynchronous session object
    :return: List of FamilyRow objects containing children data and bus
        line used by the child. The same child may appear in many rows.
    """
    sql = Path('sql/family.sql').read_text().strip()
    result = await session.execute(text(sql), {'tel': tel})
    return [FamilyRow(*row) for row in result.fetchall()]


async def insert_sms_record(
        session: AsyncSession,
        date_received_api: str,
        tel: str,
        target_date: date,
        text_: str,
        child_id: int,
        line_id: int
) -> None:
    """
    Insert a new SMS record into the database.
    :param session: SQLAlchemy asynchronous session object
    :param date_received_api: UNIX timestamp when the API received the SMS
    :param tel: Sender's phone number
    :param target_date: What date is this SMS about
    :param text_: ASCII-only, lowercase version of the SMS
    :param child_id: Child ID
    :param line_id: Bus line ID
    """
    sql = Path("sql/sms.sql").read_text().strip()
    await session.execute(
        text(sql),
        {
            "dateReceived": datetime.now(),
            "dateReceivedAPI": datetime.fromtimestamp(int(date_received_api)),
            "tel": tel,
            "targetDate": target_date,
            "text": text_,
            "childID": child_id,
            "lineID": line_id,
        }
    )
    await session.commit()


async def get_todays_sms(session: AsyncSession) -> List[SMSRow]:
    """
    Fetch all SMS records for today.
    :param session: SQLAlchemy asynchronous session object
    :return: List of SMSSow objects containing today's SMS data.
    """
    sql = Path('sql/today.sql').read_text().strip()
    result = await session.execute(text(sql))
    return [SMSRow(*row) for row in result.fetchall()]
