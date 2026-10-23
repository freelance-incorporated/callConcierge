"""Test that claiming a Task and inserting its CallAttempt succeed or fail together.

Run from apps/outbound-worker:
    .venv/Scripts/python.exe -m unittest discover -s tests -v

These tests use real SQL in temporary schemas, with no calls to Twilio.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from psycopg.errors import CheckViolation
from psycopg.pq import TransactionStatus

from app import db, processor
from app.callAttempts import CallAttemptPersistence
from app.errors import TaskExecutionFailedError, TaskStateTransitionError
from persistence_test_case import PersistenceTestCase


class CallAttemptPersistenceTests(PersistenceTestCase):
    # The shared base class creates one QUEUED task before EACH test and removes
    # its private schema afterward, including when a test raises an exception.

    async def read_saved_state(self):
        # Always open a fresh connection: we want to see committed database data,
        # not changes that are only visible inside another connection's transaction.
        async with db.get_db_connection() as conn:
            task = await self.tasks.get_task(self.task_id, conn=conn)
            cursor = await conn.execute(
                'SELECT * FROM "CallAttempt" WHERE "taskId" = %s', (self.task_id,)
            )
            return task, await cursor.fetchall()

    async def assert_nothing_was_saved(self):
        task, attempts = await self.read_saved_state()
        self.assertEqual(task["status"], "QUEUED")
        self.assertIsNone(task["startedAt"])
        self.assertEqual(attempts, [])

    async def test_processor_fake_success_completes_task_and_attempt(self):
        result = await processor.process_task(
            SimpleNamespace(taskId=self.task_id, instruction="Fake success")
        )

        task, attempts = await self.read_saved_state()
        self.assertEqual(task["status"], "SUCCEEDED")
        self.assertEqual(result["outcome"], "SIMULATED_SUCCESS")
        self.assertEqual(task["result"], result)
        self.assertIsNotNone(task["completedAt"])
        self.assertIsNone(task["failureReason"])
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0]["status"], "COMPLETED")
        self.assertIsNotNone(attempts[0]["answeredAt"])
        self.assertIsNotNone(attempts[0]["endedAt"])

    async def test_processor_simulated_failure_fails_task_and_attempt(self):
        with self.assertRaisesRegex(TaskExecutionFailedError, "Simulated processing failure"):
            await processor.process_task(
                SimpleNamespace(taskId=self.task_id, instruction="SIMULATE_FAILURE")
            )

        task, attempts = await self.read_saved_state()
        self.assertEqual(task["status"], "FAILED")
        self.assertIsNone(task["result"])
        self.assertIsNotNone(task["completedAt"])
        self.assertEqual(task["failureReason"], "Simulated processing failure")
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0]["status"], "FAILED")
        self.assertEqual(attempts[0]["failureReason"], task["failureReason"])
        self.assertIsNotNone(attempts[0]["answeredAt"])
        self.assertIsNotNone(attempts[0]["endedAt"])

    async def test_processor_duplicate_after_success_preserves_original_attempt(self):
        message = SimpleNamespace(taskId=self.task_id, instruction="Fake success")
        result = await processor.process_task(message)
        original_task, original_attempts = await self.read_saved_state()

        with patch.object(processor, "fake_process", new_callable=AsyncMock) as work:
            duplicate_result = await processor.process_task(message)
            work.assert_not_awaited()

        self.assertEqual(duplicate_result, {
            "taskId": self.task_id, "status": "SUCCEEDED", "result": result,
        })
        task, attempts = await self.read_saved_state()
        self.assertEqual(task, original_task)
        self.assertEqual(task["status"], "SUCCEEDED")
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts, original_attempts)
        self.assertEqual(attempts[0]["status"], "COMPLETED")

    async def test_processor_rolls_back_attempt_completion_when_task_cannot_complete(self):
        async def change_task_status(message):
            task, attempts = await self.read_saved_state()
            self.assertEqual(task["status"], "PROCESSING")
            self.assertEqual(len(attempts), 1)
            self.assertEqual(attempts[0]["status"], "CONNECTED")
            # Commit an incompatible Task status before the completion transaction.
            async with db.get_db_connection() as conn:
                await conn.execute(
                    '''UPDATE "Task" SET status = 'QUEUED' WHERE id = %s''',
                    (self.task_id,),
                )
            return {"outcome": "SIMULATED_SUCCESS"}

        with patch.object(processor, "fake_process", side_effect=change_task_status):
            with self.assertRaisesRegex(TaskStateTransitionError, "could not transition to SUCCEEDED"):
                await processor.process_task(SimpleNamespace(taskId=self.task_id))

        task, attempts = await self.read_saved_state()
        self.assertEqual(task["status"], "QUEUED")
        self.assertIsNone(task["result"])
        self.assertIsNone(task["completedAt"])
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0]["status"], "CONNECTED")
        self.assertIsNotNone(attempts[0]["answeredAt"])
        self.assertIsNone(attempts[0]["endedAt"])

    async def test_connect_only_accepts_created_attempts(self):
        persistence = CallAttemptPersistence()
        attempt = await persistence.create_call_attempt(self.task_id)
        connected = await persistence.connect_call_attempt(attempt["id"])
        self.assertEqual(connected["status"], "CONNECTED")
        self.assertIsNotNone(connected["answeredAt"])

        for status in ("DIALING", "RINGING", "CONNECTED", "COMPLETED", "FAILED",
                       "BUSY", "REJECTED", "NO_ANSWER"):
            with self.subTest(status=status):
                async with db.get_db_connection() as conn:
                    cursor = await conn.execute(
                        '''UPDATE "CallAttempt" SET status = %s WHERE id = %s RETURNING *''',
                        (status, attempt["id"]),
                    )
                    before = await cursor.fetchone()
                self.assertIsNone(await persistence.connect_call_attempt(attempt["id"]))
                _, saved = await self.read_saved_state()
                self.assertEqual(saved, [before])

    async def test_fail_refuses_terminal_attempts(self):
        persistence = CallAttemptPersistence()
        attempt = await persistence.create_call_attempt(self.task_id)
        for status in ("COMPLETED", "FAILED", "BUSY", "REJECTED", "NO_ANSWER"):
            with self.subTest(status=status):
                async with db.get_db_connection() as conn:
                    cursor = await conn.execute(
                        '''UPDATE "CallAttempt" SET status = %s WHERE id = %s RETURNING *''',
                        (status, attempt["id"]),
                    )
                    before = await cursor.fetchone()
                self.assertIsNone(await persistence.fail_call_attempt(attempt["id"], "Too late"))
                _, saved = await self.read_saved_state()
                self.assertEqual(saved, [before])

    async def test_claim_and_attempt_commit_together(self):
        attempts = CallAttemptPersistence()
        async with db.get_db_connection() as conn:
            # This is the same transaction structure used in processor.py.
            async with conn.transaction():
                claimed = await self.tasks.claim_task(self.task_id, conn=conn)
                self.assertEqual(claimed["status"], "PROCESSING")

                # Supplying conn must prevent the persistence helper from opening
                # its own connection. This patch fails the test if it tries to.
                # The insertion itself still runs against the real database.
                with patch(
                    "app.callAttempts.get_db_connection",
                    side_effect=AssertionError("Must use the caller's connection"),
                ):
                    attempt = await attempts.create_call_attempt(self.task_id, conn=conn)

                self.assertIsNotNone(attempt)
                self.assertTrue(attempt["id"])
                self.assertEqual(attempt["taskId"], self.task_id)
                self.assertEqual(attempt["attemptNumber"], 1)
                self.assertEqual(attempt["status"], "CREATED")
                self.assertEqual(attempt["provider"], "Twilio")
                self.assertIsNone(attempt["providerCallId"])
                self.assertIsNotNone(attempt["updatedAt"])

                # The caller still owns an open connection and an active
                # transaction. Another connection must see neither change yet.
                self.assertFalse(conn.closed)
                self.assertEqual(conn.info.transaction_status, TransactionStatus.INTRANS)
                await self.assert_nothing_was_saved()

            # Committing the transaction must not close the caller's connection.
            self.assertFalse(conn.closed)
            cursor = await conn.execute('SELECT COUNT(*) AS count FROM "CallAttempt"')
            self.assertEqual((await cursor.fetchone())["count"], 1)

        # Once the caller has finished, a fresh connection sees BOTH changes.
        task, saved_attempts = await self.read_saved_state()
        self.assertEqual(task["status"], "PROCESSING")
        self.assertIsNotNone(task["startedAt"])
        self.assertEqual(len(saved_attempts), 1)
        self.assertEqual(saved_attempts[0]["id"], attempt["id"])

    async def test_processor_rolls_back_exception_after_claim(self):
        async def stop_before_insert(task_id, conn=None):
            # This replacement runs at the insertion step in the real processor.
            # Confirm the claim already happened, then simulate an exception.
            task = await self.tasks.get_task(task_id, conn=conn)
            self.assertEqual(task["status"], "PROCESSING")
            raise RuntimeError("Failure after claim")

        with patch.object(
            processor.CallAttemptPersistence, "create_call_attempt",
            side_effect=stop_before_insert,
        ) as insert, patch.object(processor, "fake_process", new_callable=AsyncMock) as work:
            # Catch the exception outside process_task so its transaction gets
            # the exception first and can undo the claim.
            with self.assertRaisesRegex(RuntimeError, "Failure after claim"):
                await processor.process_task(SimpleNamespace(taskId=self.task_id))
            insert.assert_awaited_once()
            work.assert_not_awaited()

        await self.assert_nothing_was_saved()

    async def test_processor_rolls_back_when_database_rejects_insert(self):
        # Add a test-only rule that rejects every CallAttempt insert. This is an
        # actual PostgreSQL error, rather than a mocked insertion response.
        # The rule lives only in this test's schema and is removed during cleanup.
        async with db.get_db_connection() as conn:
            await conn.execute(
                'ALTER TABLE "CallAttempt" ADD CONSTRAINT force_insert_failure CHECK (false)'
            )

        with patch.object(processor, "fake_process", new_callable=AsyncMock) as work:
            with self.assertRaises(CheckViolation) as failure:
                await processor.process_task(SimpleNamespace(taskId=self.task_id))
            self.assertEqual(failure.exception.diag.constraint_name, "force_insert_failure")
            # Processing must never begin if creating the attempt failed.
            work.assert_not_awaited()

        await self.assert_nothing_was_saved()

    async def test_exception_after_insert_rolls_back_both_changes(self):
        # Even a successful INSERT is provisional until the caller commits.
        # Raising afterward must undo both the INSERT and the Task claim.
        with self.assertRaisesRegex(RuntimeError, "Failure after insert"):
            async with db.get_db_connection() as conn:
                async with conn.transaction():
                    claimed = await self.tasks.claim_task(self.task_id, conn=conn)
                    self.assertEqual(claimed["status"], "PROCESSING")
                    attempt = await CallAttemptPersistence().create_call_attempt(
                        self.task_id, conn=conn
                    )
                    self.assertIsNotNone(attempt)
                    raise RuntimeError("Failure after insert")

        await self.assert_nothing_was_saved()


if __name__ == "__main__":
    unittest.main()
