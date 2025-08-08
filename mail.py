import asyncio
import smtplib
from email.message import EmailMessage
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from db import engine, get_emails, get_todays_sms
from utils import group_list_by_key
from config import EMAIL, EMAIL_PASSWORD, SMTP_HOST, SMTP_PORT, ADMIN_USERNAME, ADMIN_PASSWORD

templates = Environment(loader=FileSystemLoader('templates'))

async def main() -> None:
    """
    Send email report of today's SMS messages for each bus line.
    :return: None
    """
    async with AsyncSession(engine) as session:
        email_rows = await get_emails(session)
        sms_rows = await get_todays_sms(session)
    await engine.dispose()

    grouped_sms_rows = group_list_by_key(sms_rows, lambda row: row.lineCode)
    print(email_rows)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(EMAIL, EMAIL_PASSWORD)

        for line_code, emails in email_rows:
            if not emails: continue

            sms_list = grouped_sms_rows.get(line_code)
            html_body = templates.get_template('email.jinja').render(
                messages=sms_list,
                login=ADMIN_USERNAME,
                password=ADMIN_PASSWORD)

            msg = EmailMessage()
            msg["From"] = EMAIL
            msg["To"] = emails.replace(';', ',')
            msg["Subject"] = f'Linia {line_code} - {datetime.now().strftime("%H:%M")}'
            msg.add_alternative(html_body, subtype="html")

            smtp.send_message(msg)

            print(f'Sent to {msg['To']} email with subject {msg["Subject"]}')


if __name__ == "__main__":
    asyncio.run(main())