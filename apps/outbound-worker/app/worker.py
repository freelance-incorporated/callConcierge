import os
from bullmq import Worker

# Default to localhost for local development outside docker
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

async def process_call(job, token):
    data = job.data

    call_id = data.get("callId")
    phone_number = data.get("phoneNumber")

    print(f"Processing call {call_id} to {phone_number}...")

    # TODO:
    # result = await outbound_call(...)
    
    print(f"Call {call_id} completed successfully.")

    return {
        "callId": call_id,
        "status": "completed"
    }

def start_worker():
    print(f"Starting BullMQ worker for 'outbound-calls-queue' on redis://{REDIS_HOST}:{REDIS_PORT}...")
    worker = Worker(
        "outbound-calls-queue",
        process_call,
        {
            "connection": {
                "host": REDIS_HOST,
                "port": REDIS_PORT
            }
        }
    )
    return worker
