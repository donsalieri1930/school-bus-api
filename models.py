from typing import NamedTuple, Optional

from pydantic import BaseModel


class NewSMSRequestBody(BaseModel):
    """
    Body of the new SMS request.
    """
    sms_to: str
    sms_from: str
    sms_text: str
    sms_date: str
    username: str
    MsgId: Optional[str] = None


class FamilyRow(NamedTuple):
    """
    Information about the child and the bus line. The same child may
    appear with multiple bus lines.
    """
    lastName: str
    motherEmail: str
    fatherEmail: str
    motherTel: str
    fatherTel: str
    childFullName: str
    childFirstName: str
    lineCode: str
    childId: int
    lineId: int


class SMSRow(NamedTuple):
    """
    Information about the SMS message.
    """
    smsID: int
    dateReceived: str
    dateReceivedAPI: str
    tel: str
    targetDate: str
    text: str
    childID: int
    lineID: int
    childFullName: str
    lineCode: str
    childClassName: str


class EmailsRow(NamedTuple):
    lineCode: str
    emails: str
