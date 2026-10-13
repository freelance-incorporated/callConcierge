
import asyncio
from dotenv import load_dotenv

from app.telephony import place_greeting_call


async def main():
    load_dotenv()

    recipient = input("Enter your verified test phone number: ").strip()

    call_sid = await place_greeting_call(recipient)

    print(f"Call requested successfully. Call SID: {call_sid}")


if __name__ == "__main__":
    asyncio.run(main())
