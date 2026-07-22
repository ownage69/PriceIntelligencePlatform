import os
import logging
import re
from decimal import Decimal
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

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
                
                try:
                    await page.goto(self._url, wait_until="domcontentloaded", timeout=15000)
                except Exception:
                    pass
                    
                if "amazon.com" in self._url.lower():
                    try:
                        await page.locator("#nav-global-location-data-modal-action").click(timeout=5000)
                        await page.wait_for_timeout(1500)
                        
                        await page.locator("#GLUXCountryListDropdown").click(timeout=5000)
                        await page.wait_for_timeout(1000)
                        
                        await page.get_by_role("option", name="Mexico").last.press("Enter", timeout=5000)
                        await page.wait_for_timeout(1000)
                        
                        await page.locator("[name='glowDoneButton']").click(force=True, timeout=5000)
                        
                        await page.wait_for_timeout(2000)
                        await page.reload(wait_until="domcontentloaded", timeout=15000)
                        await page.wait_for_timeout(2000)
                    except Exception as e:
                        logger.info(f"The region change was missed or failed: {e}")

                locator = page.locator(self._price_selector)
                clean_price = None
                raw_texts = []
                
                try:
                    await locator.first.wait_for(state="attached", timeout=10000)
                    
                    for _ in range(10):
                        raw_texts = await locator.all_inner_texts()
                        
                        if not any(t.strip() for t in raw_texts):
                            raw_texts = await locator.all_text_contents()
                            
                        for raw_text in raw_texts:
                            if not raw_text or not raw_text.strip():
                                continue
                            
                            clean_string = re.sub(r'[^\d,.]', '', raw_text).strip(',.')
                            
                            while '..' in clean_string:
                                clean_string = clean_string.replace('..', '.')
                                
                            if any(char.isdigit() for char in clean_string):
                                if ',' in clean_string and '.' in clean_string:
                                    clean_string = clean_string.replace(',', '')
                                else:
                                    clean_string = clean_string.replace(',', '.')
                                    
                                clean_price = Decimal(clean_string)
                                break
                        
                        if clean_price is not None:
                            break 
                            
                        await page.wait_for_timeout(1000)
                        
                except Exception:
                    os.makedirs("/app/debug_screenshots", exist_ok=True)
                    domain = urlparse(self._url).netloc.replace("www.", "")
                    screenshot_path = f"/app/debug_screenshots/error_{domain}_final.png"
                    await page.screenshot(path=screenshot_path)
                    raise PriceParserError(f"The price was not found. Saved debug screenshot: error_{domain}_final.png")

                await browser.close()

                if clean_price is None:
                    raise PriceParserError(f"No valid number found in the elements: {raw_texts}")

            return ParsedPrice(
                source_url=self._url,
                price=clean_price,
                currency=self.currency,
            )
            
        except PriceParserError:
            raise
        except Exception as error:
            raise PriceParserError(str(error)) from error
