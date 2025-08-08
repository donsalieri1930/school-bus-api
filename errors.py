from config import FUTURE_LIMIT, MAX_RANGE
from datetime import datetime


class SMSValidationError(Exception):
    """
    Base class for all SMS validation errors
    """
    message_template = 'base class'

    def __init__(self, param=""):
        self.param = param
        self.message = self.message_template.format(param)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class NoDateFoundError(SMSValidationError):
    message_template = ('Wiadomość nie zawiera daty. Dozwolony jest każdy format z 4-cyfrowym '
                        'rokiem (np. DD.\u200BMM.\u200BRRRR) oraz słowa "dzisiaj" i "jutro".')


class InvalidDateError(SMSValidationError):
    message_template = "Znaleziona data {} jest nieprawidłowa (nie ma takiego dnia)."


class TooManyDatesError(SMSValidationError):
    message_template = "Znaleziono więcej niż dwie daty: {}."


class DateInPastError(SMSValidationError):
    message_template = "Data {} jest w przeszłosci. Dzisiaj jest " + datetime.now().strftime('%d.%m.%Y') + "."


class DateTooFarInFutureError(SMSValidationError):
    message_template = "Data {} jest odległa o ponad " + str(FUTURE_LIMIT) + " dni."


class DateRangeOrderError(SMSValidationError):
    message_template = "Zakres dat {} jest nieprawidłowy, daty są w odwrotnej kolejności."


class DateRangeTooLongError(SMSValidationError):
    message_template = "Zakres dat {} jest dłuższy niż " + str(MAX_RANGE) + " dni."


class SentTooLateError(SMSValidationError):
    message_template = "Zgłoszenie dotyczy dzisiejszego dnia, ale zostało wysłane po godzinie 13:00."


class NoChildrenRegisteredError(SMSValidationError):
    message_template = "Ten numer telefonu nie jest powiązany z żadnym dzieckiem zapisanym do Węgielkobusa."


class NoChildrenNameError(SMSValidationError):
    message_template = "Wiadomość nie zawiera imienia dziecka zapisanego do Węgielkobusa: {}. "
