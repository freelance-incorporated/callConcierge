from fastapi import FastAPI

app = FastAPI(
    title="Outbound Worker API",
    version="0.1.0",
)

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Outbound worker API is running"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
