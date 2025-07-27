import os
from dotenv import load_dotenv


load_dotenv()


MAX_RANGE = 30
FUTURE_LIMIT = 30
WHITELIST_REQUESTS = True
BEFORE_13_00 = True
CONFIRMATION_FORMAT = "Zgłoszenie dla {} na {} zostało przyjęte."
ERROR_MESSAGE = "Zgłoszenie nie zostało przyjęte z powodu awarii systemu. Prosimy o kontakt z administracją."

# Secrets
DATABASE = os.getenv("DATABASE")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SMSAPI = os.getenv("SMSAPI")

# Add any new critical env variables
assert all([DATABASE, ADMIN_USERNAME, ADMIN_PASSWORD, SMSAPI, ...])
