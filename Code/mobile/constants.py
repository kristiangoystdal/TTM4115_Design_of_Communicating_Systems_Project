import os
from pathlib import Path

import pytz
from dotenv import load_dotenv


load_dotenv(verbose=True)

DISCOUNT_RATE = 0.5

BOOKINGS_HTML = "bookings.html"
HISTORY_HTML = "history.html"
INDEX_HTML = "index.html"
LOGIN_HTML = "login.html"
RECEIPT_HTML = "receipt.html"
REGISTER_HTML = "register.html"

TIMEZONE = pytz.timezone("Europe/Oslo")

_module_name = Path(__file__).parent.name
DATABASE_FILE = Path(_module_name) / "database.db"
SCHEMA_FILE = Path(_module_name) / "schema.sql"

SECRET_KEY: str = os.getenv("SECRET_KEY")  # type: ignore
