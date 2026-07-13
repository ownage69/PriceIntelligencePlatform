from __future__ import annotations

import re
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation

import httpx
from bs4 import BeautifulSoup

from app.workers.parsers.schemas import ParsedPrice


class PriceParserError(RuntimeError):
    pass


class PriceNotFoundError(PriceParserError):
    pass


class InvalidPriceError(PriceParserError):
    pass


class BasePriceParser(ABC):

    currency: str = "GBP"

    def __init__(self, url: str, client: httpx.AsyncClient) -> None:
        self._url = url
        self._client = client

    async def fetch_price(self) -> ParsedPrice:
        response = await self._client.get(self._url)
        response.raise_for_status()

        return ParsedPrice(
            source_url=self._url,
            price=self.extract_price(response.text),
            currency=self.currency,
        )

    @abstractmethod
    def extract_price(self, html: str) -> Decimal:
        pass


class CssSelectorPriceParser(BasePriceParser):

    def __init__(
        self,
        url: str,
        client: httpx.AsyncClient,
        *,
        price_selector: str,
        currency: str = "GBP",
    ) -> None:
        super().__init__(url, client)
        self._price_selector = price_selector
        self.currency = currency

    def extract_price(self, html: str) -> Decimal:
        soup = BeautifulSoup(html, "html.parser")
        price_element = soup.select_one(self._price_selector)
        if price_element is None:
            raise PriceNotFoundError(
                f"Price selector '{self._price_selector}' was not found for {self._url}."
            )

        return self._to_decimal(price_element.get_text(strip=True))

    @staticmethod
    def _to_decimal(raw_price: str) -> Decimal:
        normalized = raw_price.replace("\u00a0", "").replace(" ", "")
        numeric_value = re.sub(r"[^0-9,.-]", "", normalized)

        if numeric_value.count(",") and numeric_value.count("."):
            decimal_separator = "," if numeric_value.rfind(",") > numeric_value.rfind(".") else "."
            thousands_separator = "." if decimal_separator == "," else ","
            numeric_value = numeric_value.replace(thousands_separator, "").replace(
                decimal_separator,
                ".",
            )
        elif numeric_value.count(","):
            numeric_value = numeric_value.replace(",", ".")

        try:
            value = Decimal(numeric_value)
        except InvalidOperation as error:
            raise InvalidPriceError(f"Cannot parse price value: {raw_price!r}") from error

        if value <= Decimal("0"):
            raise InvalidPriceError(f"Price must be greater than zero: {raw_price!r}")

        return value
