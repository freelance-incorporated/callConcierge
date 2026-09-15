import asyncio


async def fake_process(message):
    await asyncio.sleep(0.5)
    if message.instruction == "SIMULATE_FAILURE":
        raise RuntimeError("Simulated processing failure")
    return {
        "outcome": "SIMULATED_SUCCESS",
        "summary": "Fake processing completed successfully",
    }
