"""Shared database setup; unittest does not discover this file as a test file.

Both test suites reuse this setup so each test gets a private schema and Task.
"""

import asyncio
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from psycopg import sql

from app import db
from app.tasks import TaskPersistence


class PersistenceTestCase(unittest.IsolatedAsyncioTestCase):
    # Each test gets its own event loop. Psycopg requires a selector loop on
    # Windows; staticmethod prevents Python from passing self to this factory.
    loop_factory = staticmethod(asyncio.SelectorEventLoop)

    async def asyncSetUp(self):
        # unittest calls asyncSetUp BEFORE EACH test. Each test therefore starts
        # with its own database tables and one new QUEUED task, regardless of
        # which test ran before it. self holds values that test methods can use.
        self.tasks = TaskPersistence()
        # UUIDs give each task and schema a unique name to avoid collisions.
        self.task_id = str(uuid4())
        self.schema = f"test_tasks_{uuid4().hex}"

        # A PostgreSQL schema is a named container for tables inside a database.
        # Our temporary schema keeps test rows separate from application rows
        # and prevents workers using the normal schema from claiming test tasks.
        # async with opens a connection and closes it on exit. This connection
        # also commits its changes on success or rolls them back on an exception.
        async with db.get_db_connection() as conn:
            # Schema names are SQL identifiers, so use Identifier to quote them
            # safely. %s parameters below are for data values, not table names.
            await conn.execute(
                sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema))
            )

        # Temporarily point the real connection helper at our test schema.
        # patch changes this setting only; database queries still run for real.
        # enterContext arranges to restore the original setting after the test.
        self.enterContext(patch.object(db, "DB_SCHEMA", self.schema))
        # Register cleanup now so it runs even if later setup or a test fails.
        # Pass the method itself, without (), so unittest can call it afterward.
        self.addAsyncCleanup(self.remove_test_schema)
        async with db.get_db_connection() as conn:
            # Migrations are the project's SQL files for creating and updating
            # tables. Reusing them gives us the actual application table layout.
            # __file__ is this file's path; parents[2] takes us to the apps folder.
            migrations = (
                Path(__file__).resolve().parents[2]
                / "ingestion-api" / "prisma" / "migrations"
            )
            # The migration folders start with timestamps. Sorting applies them
            # from oldest to newest, as later changes depend on earlier ones.
            for migration in sorted(migrations.glob("*/migration.sql")):
                await conn.execute(migration.read_text(encoding="utf-8"))
            # Give each test a known starting state: one QUEUED task.
            # The separate tuple supplies values for the %s placeholders safely.
            # The phone numbers are sample data; these tests make no calls.
            await conn.execute(
                '''INSERT INTO "Task"
                   (id, "userPhone", "recipientPhone", instruction, status, "updatedAt")
                   VALUES (%s, %s, %s, %s, 'QUEUED', CURRENT_TIMESTAMP)''',
                (self.task_id, "+12025550101", "+12025550102", "Persistence test"),
            )

    async def remove_test_schema(self):
        # CASCADE removes the tables and types inside our temporary schema too.
        # Only the uniquely named schema created for this test is removed.
        async with db.get_db_connection() as conn:
            await conn.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema))
            )

