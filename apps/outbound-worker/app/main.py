import asyncio
import logging
import sys

from .worker import start_worker

async def main():
    print("Initializing outbound worker application...")
    worker = start_worker()
    
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await worker.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        if sys.platform == "win32":
            if sys.version_info >= (3, 12):
                asyncio.run(main(), loop_factory=asyncio.SelectorEventLoop)
            else:
                getattr(asyncio, "set_event_loop_policy")(asyncio.WindowsSelectorEventLoopPolicy())
                asyncio.run(main())
        else:
            asyncio.run(main())
    except KeyboardInterrupt:
        pass
