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
        asyncio.run(main(), loop_factory=asyncio.SelectorEventLoop if sys.platform == "win32" else None)
    except KeyboardInterrupt:
        pass
