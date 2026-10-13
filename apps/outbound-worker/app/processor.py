from .telephony import place_greeting_call


async def process_outbound_call(message):
    call_sid = await place_greeting_call(message.recipientPhone)

    return {
        "outcome": "CALL_INITIATED",
        "callSid": call_sid,
        "recipientPhone": message.recipientPhone,
        "summary": "Twilio accepted the outbound call request.",
    }