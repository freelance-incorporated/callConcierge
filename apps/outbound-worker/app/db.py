import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv
from psycopg import AsyncConnection
from psycopg.rows import dict_row


load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DB_URL = os.getenv(
    "DB_URL",
    "postgresql://root:password@localhost:5432/outbound_concierge",
)
_url = urlsplit(DB_URL)
_query = dict(parse_qsl(_url.query))
DB_SCHEMA = _query.pop("schema", "public")
DB_URL = urlunsplit(_url._replace(query=urlencode(_query)))


@asynccontextmanager
async def get_db_connection() -> AsyncIterator[AsyncConnection]:
    async with await AsyncConnection.connect(DB_URL, row_factory=dict_row, options=f'-csearch_path="{DB_SCHEMA}"') as connection:
        yield connection
