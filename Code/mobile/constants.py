import os
from pathlib import Path

import pytz
from dotenv import load_dotenv


load_dotenv(verbose=True)

HOST = "127.0.0.1"
PORT = 8_000
REDIRECT_PORT = 8_001

DISCOUNT_RATE = 0.3

INDEX_HTML = "index.html"

TIMEZONE = pytz.timezone("Europe/Oslo")

_module_name = Path(__file__).parent.name
DATABASE_FILE = Path(_module_name) / "database.db"
SCHEMA_FILE = Path(_module_name) / "schema.sql"

SECRET_KEY: str = os.getenv("SECRET_KEY")  # type: ignore
