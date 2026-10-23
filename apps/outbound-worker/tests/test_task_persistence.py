"""Check TaskPersistence against a real PostgreSQL database.

These are integration tests: they check that the Python methods and database
work together. No database calls are replaced with pretend responses.

Start PostgreSQL first. From apps/outbound-worker, run:
    .venv/Scripts/python.exe -m unittest discover -s tests -v

`discover` finds test files; `-s tests` chooses the folder; `-v` shows each result.
"""

import unittest

from app import db
from persistence_test_case import PersistenceTestCase


# The shared base class prepares a fresh database schema before each test and
# removes it afterward. Methods starting with test_ are run by unittest.
class TaskPersistenceTests(PersistenceTestCase):
    async def test_atomic_claiming(self):
        # Act: try to claim the same task twice. The first call should change
        # QUEUED to PROCESSING; the second should find no eligible row to update.
        # await waits for each operation to finish before starting the next one.
        first = await self.tasks.claim_task(self.task_id)
        second = await self.tasks.claim_task(self.task_id)

        # Assert: these checks fail the test if the actual values differ from
        # what we expect. A successful claim returns the updated row as a dict.
        self.assertIsNotNone(first)
        self.assertEqual(first["id"], self.task_id)
        self.assertEqual(first["status"], "PROCESSING")
        self.assertIsNone(second)
        # This checks repeated claims in sequence; it does not simulate two
        # workers trying to claim the task at exactly the same time.

    async def test_transaction_rollback(self):
        # Expect a specific exception. assertRaisesRegex catches it outside the
        # transaction and checks its message; no exception would fail the test.
        with self.assertRaisesRegex(RuntimeError, "Deliberate rollback"):
            async with db.get_db_connection() as conn:
                # A transaction groups database changes. Leaving this block
                # with an exception undoes those changes (a rollback).
                async with conn.transaction():
                    # Passing conn is essential: the claim must use THIS
                    # transaction, rather than open and commit another connection.
                    claimed = await self.tasks.claim_task(self.task_id, conn=conn)
                    self.assertIsNotNone(claimed)
                    self.assertEqual(claimed["status"], "PROCESSING")
                    # Simulate a failure after claiming, before committing.
                    raise RuntimeError("Deliberate rollback")

        # get_task opens a fresh connection because no conn argument is passed.
        # This checks the saved database state after the failed transaction.
        task = await self.tasks.get_task(self.task_id)
        self.assertEqual(task["status"], "QUEUED")
        # The timestamp written by claim_task must have been undone as well.
        self.assertIsNone(task["startedAt"])

    async def test_complete_queued_task_returns_none(self):
        # Only PROCESSING tasks may become SUCCEEDED. Setup left this task
        # QUEUED, so attempting to complete it should update no row.
        result = await self.tasks.complete_task(self.task_id, {"ok": True})

        # Check both the method's response and the saved row. A None response
        # alone would not prove that the database was left unchanged.
        self.assertIsNone(result)
        task = await self.tasks.get_task(self.task_id)
        self.assertEqual(task["status"], "QUEUED")
        self.assertIsNone(task["result"])
        self.assertIsNone(task["completedAt"])


# Run the tests when this module is executed directly. When unittest imports it
# during discovery, this block is skipped because the runner handles execution.
if __name__ == "__main__":
    unittest.main()
