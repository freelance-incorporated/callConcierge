from psycopg.types.json import Jsonb

from .db import get_db_connection


class TaskPersistence:
    async def _execute(self, query, params):
        async with get_db_connection() as connection:
            cursor = await connection.execute(query, params)
            return await cursor.fetchone()

    async def get_task(self, task_id):
        return await self._execute('SELECT * FROM "Task" WHERE id = %s', (task_id,))

    async def claim_task(self, task_id):
        return await self._execute(
            '''UPDATE "Task" SET status = 'PROCESSING', "startedAt" = CURRENT_TIMESTAMP,
               "updatedAt" = CURRENT_TIMESTAMP WHERE id = %s AND status = 'QUEUED' RETURNING *''',
            (task_id,),
        )

    async def complete_task(self, task_id, result):
        return await self._execute(
            '''UPDATE "Task" SET status = 'SUCCEEDED', "completedAt" = CURRENT_TIMESTAMP,
               "updatedAt" = CURRENT_TIMESTAMP, result = %s, "failureReason" = NULL
               WHERE id = %s AND status = 'PROCESSING' RETURNING *''',
            (Jsonb(result), task_id),
        )

    async def fail_task(self, task_id, reason):
        return await self._execute(
            '''UPDATE "Task" SET status = 'FAILED', "completedAt" = CURRENT_TIMESTAMP,
               "updatedAt" = CURRENT_TIMESTAMP, result = NULL, "failureReason" = %s
               WHERE id = %s AND status = 'PROCESSING' RETURNING *''',
            (reason, task_id),
        )
