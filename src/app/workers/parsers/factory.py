from urllib.parse import urlparse

import httpx

from app.workers.parsers.base import BasePriceParser, PriceParserError
from app.workers.parsers.books_to_scrape import BooksToScrapeParser
from app.workers.parsers.dynamic import PlaywrightPriceParser


class UnsupportedSourceError(PriceParserError):
    pass


class PriceParserFactory:

    _books_to_scrape_hosts = frozenset({"books.toscrape.com", "www.books.toscrape.com"})
    
    @classmethod
    def create(cls, *, url: str, client: httpx.AsyncClient) -> BasePriceParser:
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        
        if host is not None:
            host_lower = host.lower()
            
            if host_lower in {"wildberries.ru", "www.wildberries.ru"}:
                host_lower = host_lower.replace(".ru", ".by")
                url = url.replace(parsed_url.hostname, host_lower)
            
            if host_lower in cls._books_to_scrape_hosts:
                return BooksToScrapeParser(url, client)
            
            if host_lower in {"wildberries.by", "www.wildberries.by", "by.wildberries.ru"}:
                return PlaywrightPriceParser(
                    url=url,
                    client=client,
                    price_selector="text=ƃ",
                    currency="BYN"
                )
                
            if host_lower in {"amazon.com", "www.amazon.com"}:
                return PlaywrightPriceParser(
                    url=url,
                    client=client,
                    price_selector=".priceToPay, .apexPriceToPay",
                    currency="USD"
                )

        raise UnsupportedSourceError(f"No parser is registered for URL: {url}")
