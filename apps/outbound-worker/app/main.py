import asyncio
from worker import start_worker

async def main():
    print("Initializing outbound worker application...")
    worker = start_worker()
    
    try:
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
