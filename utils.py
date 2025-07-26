import json
import re
import secrets
from datetime import date
from typing import Set, Annotated, List, Tuple

from fastapi import Request, Depends, status, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from unidecode import unidecode

from config import ADMIN_USERNAME, ADMIN_PASSWORD, CONFIRMATION_FORMAT
from models import FamilyRow


def get_client_ip(request: Request) -> str:
    """
    Return the original client IP, using 'X-Forwarded-For' if behind a proxy.
    """
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host


def get_whitelisted_ips(filename='whitelist.json') -> Set[str]:
    """
    Return trusted IP addresses stored in the specified JSON file.
    :param filename: Relative path to JSON file
    :return: Set of IP addresses
    """
    with open(filename) as f:
        return set(json.load(f))


def normalize(text: str) -> str:
    """
    Return ASCII-only, lowercase version of given text.
    """
    return unidecode(text).lower()


def name_in_text(name: str, text: str) -> bool:
    """
    Check if a normalized name appears as a whole word in the text.
    """
    pattern = rf'\b{normalize(name)}\b'
    return re.search(pattern, normalize(text)) is not None


def get_current_username(credentials: Annotated[HTTPBasicCredentials, Depends(HTTPBasic())]) -> str:
    """
    Validate user credentials using HTTP Basic Authentication.
    :param credentials: HTTPBasicCredentials object containing username and password
    :return: Username if credentials are correct
    :raises: HTTPException (401) if credentials are invalid, with WWW-Authenticate header
    """
    is_correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def create_confirmation_message(family_matched: List[FamilyRow], dates: List[Tuple[str, date]]) -> str:
    """
    Create a confirmation message for SMS sender.
    :param family_matched: List of FamilyRow objects containing matched children data
    :param dates: List of (matched_string, date) tuples in the original order
    """
    children_full_names = set([row.childFullName for row in family_matched])
    if len(dates) == 1:
        dates_str = dates[0][1].strftime('%d.%m.%Y')
    else:
        dates_str = dates[0][1].strftime('%d.%m.%Y') + ' - ' + dates[1][1].strftime('%d.%m.%Y')

    return CONFIRMATION_FORMAT.format(', '.join(children_full_names), dates_str)


