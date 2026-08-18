import asyncio
from worker import start_worker

async def main():
    print("Initializing outbound worker application...")
    # Start the BullMQ worker
    worker = start_worker()
    
    try:
        # Keep the application alive while the worker processes jobs in the background
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        print("Shutting down worker...")
        await worker.close()
    except KeyboardInterrupt:
        print("Shutting down worker (interrupted)...")
        await worker.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
