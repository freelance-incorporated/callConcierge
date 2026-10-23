import logging
import os

from bullmq import UnrecoverableError, Worker
from pydantic import ValidationError

from .contracts import CallTaskV1
from .processor import process_task
from .errors import (
    TaskNotFoundError,
    TaskAlreadyFailedError,
    TaskNotReadyError, 
    TaskUnclaimableError, 
    TaskExecutionFailedError, 
    TaskStateTransitionError,
    CallAttemptCreationFailedError
)# better practice than importing *

logger = logging.getLogger(__name__)


async def validate_call(job, token):
    try:
        message = CallTaskV1.model_validate(job.data)
    except ValidationError as error:
        raise UnrecoverableError("Invalid call task V1 message") from error
    task_id = str(message.taskId)
    if job.name != "outbound-call" or job.id != task_id:
        raise UnrecoverableError("Job name or ID does not match the call task contract")
    
    try:
        result = await process_task(message)
        return result
    except (TaskNotFoundError, TaskUnclaimableError, TaskAlreadyFailedError) as e:
        raise UnrecoverableError(str(e)) from e
    except TaskNotReadyError as e:
        logger.warning("Task %s is still QUEUING, throwing back to BullMQ for retry.", task_id)
        raise
    except TaskExecutionFailedError as e:
        logger.warning("Task %s failed via Simulated Failure!", task_id)
        raise
    except TaskStateTransitionError as e:
        logger.warning("Task %s state could not be changed!", task_id)
        raise
    except CallAttemptCreationFailedError as e:
        logger.warning("Failed to create Call Attmept for Task %s", task_id)
        raise UnrecoverableError(str(e)) from e


def start_worker():
    worker = Worker(
        "call-tasks",
        validate_call,
        {
            "connection": os.environ.get("REDIS_URL") or {
                "host": os.environ.get("REDIS_HOST", "localhost"),
                "port": int(os.environ.get("REDIS_PORT", "6379")),
            },
            "prefix": os.environ.get("BULLMQ_PREFIX", "bull"),
        },
    )
    worker.on("error", lambda error, *args: logger.error("BullMQ worker error: %s", error))
    worker.on("failed", lambda job, error: logger.warning("Job %s failed: %s", job.id, error))
    return worker
