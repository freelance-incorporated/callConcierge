import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from psycopg import AsyncConnection


load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DB_URL = os.getenv(
    "DB_URL",
    "postgresql://root:password@localhost:5432/outbound_concierge",
)


@asynccontextmanager
async def get_db_connection() -> AsyncIterator[AsyncConnection]:
    async with await AsyncConnection.connect(DB_URL) as connection:
        yield connection
