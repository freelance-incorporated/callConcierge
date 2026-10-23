from uuid import uuid4

from .db import get_db_connection

class CallAttemptPersistence:
    async def _execute(self, query, params, conn=None):
        if conn is not None:
            cursor= await conn.execute(query,params)
            return await cursor.fetchone()
        async with get_db_connection() as connection:
            cursor= await connection.execute(query,params)
            return await cursor.fetchone()
        
    async def create_call_attempt(self, task_id, conn=None):
        return await self._execute(''' INSERT INTO "CallAttempt"
            (id, "taskId", "attemptNumber", status, "updatedAt") 
            VALUES (%s, %s, %s, %s::"CallAttemptStatus", CURRENT_TIMESTAMP)
            RETURNING * ''', (str(uuid4()), task_id, 1, "CREATED"), conn=conn)

    async def complete_call_attempt(self, call_attempt_id, conn=None):
        return await self._execute(
            ''' UPDATE "CallAttempt" SET status = 'COMPLETED', 
                "endedAt" = CURRENT_TIMESTAMP, "updatedAt"= CURRENT_TIMESTAMP
                WHERE id = %s AND status = 'CONNECTED' 
                RETURNING * ''',
            (call_attempt_id,), 
            conn=conn
        )
    async def fail_call_attempt(self, call_attempt_id, failure_reason, conn=None):
        return await self._execute(
            ''' UPDATE "CallAttempt" SET status = 'FAILED', 
                "failureReason" = %s, "endedAt" = CURRENT_TIMESTAMP,                
                "updatedAt"= CURRENT_TIMESTAMP
                WHERE id = %s 
                AND status NOT IN
                ('COMPLETED', 'FAILED', 'BUSY', 'REJECTED', 'NO_ANSWER')
                RETURNING * ''',
            (failure_reason, call_attempt_id), 
            conn=conn
            )

    async def connect_call_attempt(self, call_attempt_id, conn=None):
        return await self._execute(
            ''' UPDATE "CallAttempt"
            SET status = %s::"CallAttemptStatus", "answeredAt" = CURRENT_TIMESTAMP,
                "updatedAt" = CURRENT_TIMESTAMP
            WHERE id=%s AND status = 'CREATED'
            RETURNING * ''',
            ('CONNECTED', call_attempt_id), 
            conn=conn
        )
