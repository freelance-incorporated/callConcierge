from pydantic import BaseModel, ConfigDict, Field, JsonValue, UUID4


class CallTaskV1(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    schemaVersion: int = Field(ge=1, le=1)
    taskId: UUID4 = Field(strict=False)
    userPhone: str = Field(pattern=r"^\+?[1-9][0-9]{1,14}$")
    recipientPhone: str = Field(pattern=r"^\+?[1-9][0-9]{1,14}$")
    instruction: str = Field(min_length=5, max_length=2000)
    userName: str | None = Field(default=None, min_length=3, max_length=60)
    recipientName: str | None = Field(default=None, min_length=3, max_length=60)
    userData: dict[str, JsonValue] | None = None
