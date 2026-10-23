import asyncio
import logging

from .db import get_db_connection
from .tasks import TaskPersistence
from .callAttempts import CallAttemptPersistence
from .errors import (
    TaskNotFoundError,
    TaskAlreadyFailedError,
    TaskNotReadyError, 
    TaskUnclaimableError, 
    TaskExecutionFailedError, 
    TaskStateTransitionError,
    CallAttemptCreationFailedError,
    CallAttemptStateTransitionError
)

logger = logging.getLogger(__name__)

async def process_task(message):
    tasks = TaskPersistence()
    task_id = str(message.taskId)
    async with get_db_connection() as connection:
        async with connection.transaction():
            claimed = await tasks.claim_task(task_id, conn=connection)
            if claimed is None:
                existing = await tasks.get_task(task_id, conn=connection)
                if existing is None:
                    raise TaskNotFoundError("Task does not exist")
                if existing["status"] == "QUEUING":
                    raise TaskNotReadyError("Queue publication is not recorded yet; retry the task")
                if existing["status"] == "SUCCEEDED":
                    return {"taskId": task_id, "status": "SUCCEEDED", "result": existing["result"]}
                if existing["status"] == "FAILED":
                    raise TaskAlreadyFailedError(existing["failureReason"] or "Task already failed")
                raise TaskUnclaimableError(f'Task cannot be claimed from {existing["status"]}')
            
            attempts = CallAttemptPersistence()
            call = await attempts.create_call_attempt(task_id, conn=connection)

            if call is None:
                raise CallAttemptCreationFailedError("Call Attempt could not be created!")
            
    logger.info("Task %s entered PROCESSING", task_id)

    call_attempt_id = call["id"]

    async with get_db_connection() as conn:   
        connected_call = await attempts.connect_call_attempt(call_attempt_id, conn)

        if connected_call is None:
            raise CallAttemptStateTransitionError("Call Attempt could not be connected!")
        
    try:
        result = await fake_process(message)
    #Task Failure block:
    except TaskExecutionFailedError as e:
        async with get_db_connection() as conn:
            async with conn.transaction():
                attempt_failure = await attempts.fail_call_attempt(call_attempt_id, str(e), conn = conn)
                if attempt_failure is None:
                    raise CallAttemptStateTransitionError(f"CallAttempt {call_attempt_id} could not transition to FAILED")
                
                task_failure = await tasks.fail_task(task_id=task_id, reason = str(e), conn = conn)
                if task_failure is None:
                    raise TaskStateTransitionError(f"Task {task_id} could not transition to FAILED")
        raise
    #Successful completion block:
    else:
        async with get_db_connection() as conn:
            async with conn.transaction():
                attempt_completion= await attempts.complete_call_attempt(call_attempt_id, conn=conn)
                if attempt_completion is None:
                    raise CallAttemptStateTransitionError(f"CallAttempt {call_attempt_id} could not transition to COMPLETED")
                
                task_completion= await tasks.complete_task(task_id=task_id, result=result, conn=conn)
                if task_completion is None:
                    raise TaskStateTransitionError(f"Task {task_id} could not transition to SUCCEEDED")
        return result
    
async def fake_process(message):
    await asyncio.sleep(0.5)
    if message.instruction == "SIMULATE_FAILURE":
        raise TaskExecutionFailedError("Simulated processing failure")
    
    return {
        "outcome": "SIMULATED_SUCCESS",
        "summary": "Fake processing completed successfully",
    }
