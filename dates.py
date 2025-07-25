import re
from datetime import datetime, timedelta, time, date
from typing import List, Tuple

from pytz import timezone

from config import *
from errors import *


def construct_date(text: str, dmy: bool) -> date:
    """
    Parse date in an allowed format into a date object.
    :param text: Date string
    :param dmy: DMY if True, else YMD
    :return: Date object
    :raises: errors.InvalidDateError
    """
    normalized = re.sub(r"[/-]", ".", text)
    fmt = "%d.%m.%Y" if dmy else "%Y.%m.%d"
    try:
        return datetime.strptime(normalized, fmt).date()
    except ValueError:
        raise InvalidDateError(text)


def find_all_dates(text: str) -> List[Tuple[str, date]]:
    """
    Finds all dates in any format that
        * is YMD or DMY
        * has 4-digit year
        * uses separators: "." or "/" or "-"
        * is a literal keyword meaning today or tomorrow
    :returns: List of (matched_string, date) tuples in the original order
    :raises: errors.InvalidDateError
    """

    # Regex groups
    dmy_regex = r"(?P<dmy>\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b)"
    ymd_regex = r"(?P<ymd>\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b)"
    today_regex = r"(?P<today>\b(?:dziś|dzis|dzisiaj)\b)"
    tomorrow_regex = r"(?P<tomorrow>\bjutro\b)"

    named_regex = f"{dmy_regex}|{ymd_regex}|{today_regex}|{tomorrow_regex}"

    results = []

    for match in re.finditer(named_regex, text, re.IGNORECASE):
        matched_str = match.group(0)
        dmy, ymd, today, tomorrow = match.groups() # one of these is not None

        if dmy:
            results.append((matched_str, construct_date(dmy, dmy=True)))
        elif ymd:
            results.append((matched_str, construct_date(ymd, dmy=False)))
        elif today:
            results.append((matched_str, date.today()))
        elif tomorrow:
            results.append((matched_str, date.today() + timedelta(days=1)))

    return results


def validate_date(new_date: Tuple[str, date]) -> None:
    """
    Validate single date, make sure that
        * date >= today
        * date <= today + config.FUTURE_LIMIT
    :param new_date: (matched_string, datetime.date) tuple
    :raises: errors.SMSValidationError
    """
    today = datetime.now(timezone("Europe/Warsaw")).date()
    if new_date[1] < today: raise DateInPastError(new_date[0])
    if new_date[1] > today + timedelta(days=FUTURE_LIMIT):
        raise DateTooFarInFutureError(new_date[0])


def validate_range(start: Tuple[str, date], end: Tuple[str, date]) -> None:
    """
    Validate a pair of dates, make sure that
        * start <= end
        * end - start <= config.FUTURE_LIMIT
    make sure to call validate_date on start and end before.
    :param start: (matched_string, datetime.date) tuple
    :param end: (matched_string, datetime.date) tuple
    :raises: errors.SMSValidationError
    """
    if end[1] < start[1]: raise DateRangeOrderError(start[0] + ' : ' + end[0])
    if (end[1] - start[1]).days > MAX_RANGE:
        raise DateRangeTooLongError(start[0] + ' : ' + end[0])


def validate_time(new_date: Tuple[str, date]) -> None:
    """
    Make sure that a message for today was received before 13:00 Warsaw time.
    Can be switched on/off by config.BEFORE_13_00.
    :param new_date: (matched_string, datetime.date) tuple
    :raises: errors.SentTooLateError
    """
    now = datetime.now(timezone("Europe/Warsaw"))
    if new_date[1] == now.date() and now.time() > time(hour=13) and BEFORE_13_00:
        raise SentTooLateError()


def create_date_range(start: Tuple[str, date], end: Tuple[str, date]) -> List[date]:
    """
    Create a list with all days from start to end inclusively.
    :param start: (matched_string, datetime.date) tuple
    :param end: (matched_string, datetime.date) tuple
    :return: List of datetime.date objects
    """
    delta = (end[1] - start[1]).days
    return [start[1] + timedelta(days=i) for i in range(delta + 1)]


def replace_literals(text: str) -> str:
    """
    Replace
        * "dzis", "dzisiaj" with today's date
        * "jutro" with tomorrow's date
    in DD.MM.YYYY format.
    """
    now = datetime.now(timezone("Europe/Warsaw"))
    today = now.date().isoformat()
    tomorrow = (now + timedelta(days=1)).date().strftime("%d.%m.%Y")
    for k, v in {'dzisiaj': today,
                 'dzis': today,
                 'jutro': tomorrow}.items():
        text = text.replace(k, v)
    return text
