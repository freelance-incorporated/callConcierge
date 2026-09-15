import logging
import os

from bullmq import UnrecoverableError, Worker
from pydantic import ValidationError

from .contracts import CallTaskV1
from .processor import fake_process
from .tasks import TaskPersistence


logger = logging.getLogger(__name__)


async def process_call(job, token):
    try:
        message = CallTaskV1.model_validate(job.data)
    except ValidationError as error:
        raise UnrecoverableError("Invalid call task V1 message") from error
    task_id = str(message.taskId)
    if job.name != "outbound-call" or job.id != task_id:
        raise UnrecoverableError("Job name or ID does not match the call task contract")

    tasks = TaskPersistence()
    claimed = await tasks.claim_task(task_id)
    if claimed is None:
        existing = await tasks.get_task(task_id)
        if existing is None:
            raise UnrecoverableError("Task does not exist")
        if existing["status"] == "QUEUING":
            raise RuntimeError("Queue publication is not recorded yet; retry the task")
        if existing["status"] == "SUCCEEDED":
            return {"taskId": task_id, "status": "SUCCEEDED", "result": existing["result"]}
        if existing["status"] == "FAILED":
            raise UnrecoverableError(existing["failureReason"] or "Task already failed")
        raise RuntimeError(f'Task cannot be claimed from {existing["status"]}')

    logger.info("Task %s entered PROCESSING", task_id)
    try:
        result = await fake_process(message)
    except Exception as error:
        failed = await tasks.fail_task(task_id, str(error))
        if failed is None:
            raise RuntimeError("Task failure transition was rejected") from error
        logger.info("Task %s entered FAILED", task_id)
        raise UnrecoverableError(str(error)) from error

    completed = await tasks.complete_task(task_id, result)
    if completed is None:
        raise RuntimeError("Task completion transition was rejected")
    logger.info("Task %s entered SUCCEEDED", task_id)
    return {"taskId": task_id, "status": "SUCCEEDED", "result": result}


def start_worker():
    worker = Worker(
        "call-tasks",
        process_call,
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
