from pydantic import BaseModel, ConfigDict, Field


class StoreCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=255)
    domain: str = Field(min_length=1, max_length=255)


class StoreUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=255)
    domain: str | None = Field(default=None, min_length=1, max_length=255)


class StoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    domain: str