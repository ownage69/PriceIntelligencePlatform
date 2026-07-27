import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from app.workers.parsers.base import CssSelectorPriceParser, PriceNotFoundError, InvalidPriceError, PriceParserError
from app.workers.parsers.books_to_scrape import BooksToScrapeParser
from app.workers.parsers.dynamic import PlaywrightPriceParser
from app.workers.parsers.factory import PriceParserFactory, UnsupportedSourceError

def test_css_parser_to_decimal():
    assert CssSelectorPriceParser._to_decimal("£1,234.56") == Decimal("1234.56")
    assert CssSelectorPriceParser._to_decimal("1.234,56 BYN") == Decimal("1234.56")
    assert CssSelectorPriceParser._to_decimal("1 234,56") == Decimal("1234.56")
    assert CssSelectorPriceParser._to_decimal("1234,56") == Decimal("1234.56")
    assert CssSelectorPriceParser._to_decimal("1234.56") == Decimal("1234.56")
    assert CssSelectorPriceParser._to_decimal("Цена: 100") == Decimal("100.00")

def test_css_parser_invalid_prices():
    with pytest.raises(InvalidPriceError):
        CssSelectorPriceParser._to_decimal("0")
    with pytest.raises(InvalidPriceError):
        CssSelectorPriceParser._to_decimal("-10")
    with pytest.raises(InvalidPriceError):
        CssSelectorPriceParser._to_decimal("not a price")

@pytest.mark.asyncio
async def test_css_parser_extract_price_not_found():
    client = AsyncMock(spec=httpx.AsyncClient)
    parser = CssSelectorPriceParser("http://test.com", client, price_selector=".price")
    with pytest.raises(PriceNotFoundError):
        parser.extract_price("<html><body><div>No price here</div></body></html>")

@pytest.mark.asyncio
async def test_css_parser_fetch_price():
    client = AsyncMock(spec=httpx.AsyncClient)
    client.get.return_value = MagicMock(status_code=200, text="<div class='price'>100.50</div>")
    parser = CssSelectorPriceParser("http://test.com", client, price_selector=".price")
    
    res = await parser.fetch_price()
    assert res.price == Decimal("100.50")
    assert res.currency == "GBP"

def test_factory_books():
    client = AsyncMock(spec=httpx.AsyncClient)
    parser = PriceParserFactory.create(url="http://books.toscrape.com/test", client=client)
    assert isinstance(parser, BooksToScrapeParser)
    assert parser.currency == "GBP"

def test_factory_wildberries():
    client = AsyncMock(spec=httpx.AsyncClient)
    parser = PriceParserFactory.create(url="https://wildberries.ru/catalog/1", client=client)
    assert isinstance(parser, PlaywrightPriceParser)
    assert "wildberries.by" in parser._url
    assert parser.currency == "BYN"

def test_factory_amazon():
    client = AsyncMock(spec=httpx.AsyncClient)
    parser = PriceParserFactory.create(url="https://amazon.com/dp/1", client=client)
    assert isinstance(parser, PlaywrightPriceParser)
    assert parser.currency == "USD"

def test_factory_onliner():
    client = AsyncMock(spec=httpx.AsyncClient)
    parser = PriceParserFactory.create(url="https://catalog.onliner.by/test", client=client)
    assert isinstance(parser, PlaywrightPriceParser)
    assert parser.currency == "BYN"

def test_factory_unsupported():
    client = AsyncMock(spec=httpx.AsyncClient)
    with pytest.raises(UnsupportedSourceError):
        PriceParserFactory.create(url="https://unknown.com", client=client)
    with pytest.raises(UnsupportedSourceError):
        PriceParserFactory.create(url="invalid_url_without_schema", client=client)

@pytest.fixture
def mock_playwright_env():
    with patch("app.workers.parsers.dynamic.async_playwright") as mock_ap, \
         patch("app.workers.parsers.dynamic.stealth_async"), \
         patch("app.workers.parsers.dynamic.os.makedirs"):
        
        mock_p = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_locator = AsyncMock()
        
        mock_page.locator = MagicMock(return_value=mock_locator)
        mock_locator.first = mock_locator 
        
        mock_ap.return_value.__aenter__.return_value = mock_p
        mock_p.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        mock_option = AsyncMock()
        mock_page.get_by_role = MagicMock(return_value=mock_option)
        mock_option.last = mock_option
        
        yield mock_page, mock_locator

@pytest.mark.asyncio
async def test_playwright_success(mock_playwright_env):
    mock_page, mock_locator = mock_playwright_env
    mock_locator.all_inner_texts.return_value = ["\n 1 200,50 \n"]
    
    parser = PlaywrightPriceParser("http://test.com", AsyncMock(), price_selector=".price")
    res = await parser.fetch_price()
    
    assert res.price == Decimal("1200.50")
    mock_page.goto.assert_called_once()
    mock_page.screenshot.assert_called()

@pytest.mark.asyncio
async def test_playwright_fallback_to_text_contents(mock_playwright_env):
    mock_page, mock_locator = mock_playwright_env
    mock_locator.all_inner_texts.return_value = ["   ", ""]
    mock_locator.all_text_contents.return_value = ["\n,1 500.99"]
    
    parser = PlaywrightPriceParser("http://test.com", AsyncMock(), price_selector=".price")
    res = await parser.fetch_price()
    assert res.price == Decimal("1500.99")

@pytest.mark.asyncio
async def test_playwright_amazon_region_change(mock_playwright_env):
    mock_page, mock_locator = mock_playwright_env
    mock_locator.all_inner_texts.return_value = ["$150.00"]
    
    parser = PlaywrightPriceParser("http://amazon.com", AsyncMock(), price_selector=".price")
    res = await parser.fetch_price()
    
    assert res.price == Decimal("150.00")
    assert mock_page.locator.call_count >= 2 
    mock_page.reload.assert_called_once()

@pytest.mark.asyncio
async def test_playwright_amazon_region_change_error_handled(mock_playwright_env):
    mock_page, mock_locator = mock_playwright_env
    mock_locator.all_inner_texts.return_value = ["150.00"]
    
    mock_locator.click.side_effect = Exception("Click failed")
    
    parser = PlaywrightPriceParser("http://amazon.com", AsyncMock(), price_selector=".price")
    res = await parser.fetch_price()
    assert res.price == Decimal("150.00")

@pytest.mark.asyncio
async def test_playwright_no_valid_price(mock_playwright_env):
    mock_page, mock_locator = mock_playwright_env
    mock_locator.all_inner_texts.return_value = ["", "   ", "Not a price"]
    mock_locator.all_text_contents.return_value = []
    
    parser = PlaywrightPriceParser("http://test.com", AsyncMock(), price_selector=".price")
    with pytest.raises(PriceParserError) as exc:
        await parser.fetch_price()
    assert "No valid number found" in str(exc.value)

@pytest.mark.asyncio
async def test_playwright_goto_exception_handled(mock_playwright_env):
    mock_page, mock_locator = mock_playwright_env
    mock_locator.all_inner_texts.return_value = ["10.00"]
    mock_page.goto.side_effect = Exception("Timeout on goto")
    
    parser = PlaywrightPriceParser("http://test.com", AsyncMock(), price_selector=".price")
    res = await parser.fetch_price()
    assert res.price == Decimal("10.00")

@pytest.mark.asyncio
async def test_playwright_unexpected_fatal_exception(mock_playwright_env):
    mock_page, mock_locator = mock_playwright_env
    mock_locator.wait_for.side_effect = Exception("Target closed")
    
    parser = PlaywrightPriceParser("http://test.com", AsyncMock(), price_selector=".price")
    with pytest.raises(PriceParserError) as exc:
        await parser.fetch_price()
    assert "The price was not found" in str(exc.value)

@pytest.mark.asyncio
async def test_playwright_decimal_conversion_warning(mock_playwright_env):
    mock_page, mock_locator = mock_playwright_env
    mock_locator.all_inner_texts.return_value = ["100", "150.00"]
    
    with patch("app.workers.parsers.dynamic.Decimal", side_effect=[Exception("Oops"), Decimal("150.00")]):
        parser = PlaywrightPriceParser("http://test.com", AsyncMock(), price_selector=".price")
        res = await parser.fetch_price()
        assert res.price == Decimal("150.00")

from app.workers.parsers.schemas import ParsedPrice
from app.workers.parsers.base import BasePriceParser

def test_parsed_price_currency_not_string():
    with pytest.raises(ValueError, match="Currency must be a string"):
        ParsedPrice(source_url="http://test.com", price=Decimal("10"), currency=123)

@pytest.mark.asyncio
async def test_playwright_global_exception():
    with patch("app.workers.parsers.dynamic.async_playwright", side_effect=Exception("Critical Failure")):
        parser = PlaywrightPriceParser("http://test.com", AsyncMock(), price_selector=".price")
        with pytest.raises(PriceParserError, match="Critical Failure"):
            await parser.fetch_price()

def test_base_parser_abstract_method():
    BasePriceParser.extract_price(None, "")
