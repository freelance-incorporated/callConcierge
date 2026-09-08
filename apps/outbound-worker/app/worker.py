import os

from bullmq import Worker

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

async def process_call(job, token):
    data = job.data

    task_id = data.get("taskId")
    recipient_phone = data.get("recipientPhone")

    print(f"Processing task {task_id} for {recipient_phone}...")
    print(f"Task {task_id} completed successfully.")

    return {
        "taskId": task_id,
        "status": "completed"
    }

def start_worker():
    print(f"Starting BullMQ worker for 'call-tasks' on redis://{REDIS_HOST}:{REDIS_PORT}...")
    worker = Worker(
        "call-tasks",
        process_call,
        {
            "connection": {
                "host": REDIS_HOST,
                "port": REDIS_PORT
            }
        }
    )
    return worker
