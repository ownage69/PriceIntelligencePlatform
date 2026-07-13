from datetime import UTC, datetime
from decimal import Decimal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator


class ParsedPrice(BaseModel):
    """A validated price extracted from an external product page."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source_url: AnyHttpUrl
    price: Decimal = Field(gt=Decimal("0"), max_digits=12, decimal_places=2, strict=True)
    currency: str = Field(default="GBP", pattern=r"^[A-Z]{3}$", strict=True)
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> str:
        """Normalize a parser-provided ISO 4217 currency code."""
        if not isinstance(value, str):
            raise ValueError("Currency must be a string.")
        return value.upper()
