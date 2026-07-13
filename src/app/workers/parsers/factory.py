from urllib.parse import urlparse

import httpx

from app.workers.parsers.base import BasePriceParser, PriceParserError
from app.workers.parsers.books_to_scrape import BooksToScrapeParser


class UnsupportedSourceError(PriceParserError):
    pass


class PriceParserFactory:
    pass

    _books_to_scrape_hosts = frozenset({"books.toscrape.com", "www.books.toscrape.com"})

    @classmethod
    def create(cls, *, url: str, client: httpx.AsyncClient) -> BasePriceParser:
        host = urlparse(url).hostname
        if host is not None and host.lower() in cls._books_to_scrape_hosts:
            return BooksToScrapeParser(url, client)

        raise UnsupportedSourceError(f"No parser is registered for URL: {url}")
