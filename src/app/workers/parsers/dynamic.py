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
                
                os.makedirs("/app/debug_screenshots", exist_ok=True)
                domain = urlparse(self._url).netloc.replace("www.", "")
                
                try:
                    await page.goto(self._url, wait_until="domcontentloaded", timeout=30000)
                except Exception:
                    pass
                    
                await page.screenshot(path=f"/app/debug_screenshots/{domain}_step_1_loaded.png")
                logger.info(f"Step 1: Page {self._url} loaded. Screenshot saved.")
                    
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
                        await page.reload(wait_until="domcontentloaded", timeout=30000)
                        await page.wait_for_timeout(2000)
                        
                        await page.screenshot(path=f"/app/debug_screenshots/{domain}_step_1.5_amazon_region.png")
                    except Exception as e:
                        logger.info(f"The region change was missed or failed: {e}")

                locator = page.locator(self._price_selector)
                clean_price = None
                raw_texts = []
                
                try:
                    await locator.first.wait_for(state="attached", timeout=30000)
                    
                    await page.screenshot(path=f"/app/debug_screenshots/{domain}_step_2_locator_attached.png")
                    logger.info(f"Step 2: Selector '{self._price_selector}' found on the page. Screenshot saved.")
                    
                    for i in range(10):
                        raw_texts = await locator.all_inner_texts()
                        
                        if not any(t.strip() for t in raw_texts):
                            raw_texts = await locator.all_text_contents()
                        
                        logger.info(f"Extraction attempt {i+1}. Found raw texts: {raw_texts}")
                            
                        for raw_text in raw_texts:
                            if not raw_text or not raw_text.strip():
                                continue
                            
                            text_fixed = raw_text.replace('\n,', ',').replace('\n.', '.')
                            
                            match = re.search(r'(\d+(?:[\s\xa0\u202f\u200b\n]+\d+)*(?:[.,]\d{1,2})?)', text_fixed)
                            
                            if match:
                                clean_string = re.sub(r'[^\d,.]', '', match.group(1))
                                
                                if ',' in clean_string and '.' in clean_string:
                                    clean_string = clean_string.replace(',', '')
                                else:
                                    clean_string = clean_string.replace(',', '.')
                                    
                                try:
                                    clean_price = Decimal(clean_string)
                                    if clean_price > Decimal("0"):
                                        break
                                except Exception as e:
                                    logger.warning(f"Couldn't convert {clean_string} into Decimal: {e}")
                                    continue
                        
                        if clean_price is not None:
                            await page.screenshot(path=f"/app/debug_screenshots/{domain}_step_3_price_parsed.png")
                            logger.info(f"Step 3: Price {clean_price} successfully parsed. Screenshot saved.")
                            break 
                            
                        await page.wait_for_timeout(1000)
                        
                except Exception as e:
                    screenshot_path = f"/app/debug_screenshots/error_{domain}_final.png"
                    await page.screenshot(path=screenshot_path)
                    logger.error(f"Error when searching for an item: {e}")
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
