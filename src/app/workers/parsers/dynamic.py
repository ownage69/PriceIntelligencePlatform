import logging
import re
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from decimal import Decimal

from app.workers.parsers.base import CssSelectorPriceParser, PriceParserError
from app.workers.parsers.schemas import ParsedPrice

logger = logging.getLogger(__name__)

class PlaywrightPriceParser(CssSelectorPriceParser):

    async def fetch_price(self) -> ParsedPrice:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080}
                )
                page = await context.new_page()
                await stealth_async(page)
                
                await page.goto(self._url, wait_until="domcontentloaded")
                
                locator = page.locator(self._price_selector).first
                
                try:
                    await locator.wait_for(state="attached", timeout=15000)
                except Exception:
                    pass
                
                raw_text = await locator.inner_text()
                await browser.close()

                clean_string = re.sub(r'[^\d,.]', '', raw_text)
                clean_price = Decimal(clean_string.replace(',', '.'))

            return ParsedPrice(
                source_url=self._url,
                price=clean_price,
                currency=self.currency,
            )
        except Exception as error:
            raise PriceParserError(str(error)) from error
