
import asyncio
import os

from twilio.rest import Client


def _place_greeting_call(to_phone: str) -> str:
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    from_phone = os.environ["TWILIO_PHONE_NUMBER"]

    client = Client(account_sid, auth_token)

    call = client.calls.create(
        to=to_phone,
        from_=from_phone,
        url="https://webhooks.twilio.com/v1/Voice/Template/voice_speech_recognition",
    )

    if not call.sid:
        raise RuntimeError("Twilio call creation failed: call SID was not returned.")

    return call.sid


async def place_greeting_call(to_phone: str) -> str:
    return await asyncio.to_thread(_place_greeting_call, to_phone)