import httpx

from app.workers.parsers.base import CssSelectorPriceParser


class BooksToScrapeParser(CssSelectorPriceParser):

    def __init__(self, url: str, client: httpx.AsyncClient) -> None:
        super().__init__(
            url,
            client,
            price_selector=".product_main .price_color",
            currency="GBP",
        )
