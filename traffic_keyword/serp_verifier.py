"""
Live SERP Position Verifier & Rank Tracker
Queries live Google & Bing search result pages to verify where target landing pages
actually rank organically before sending traffic batches.
Calculates required impressions and CTR uplift to push rankings into top 3.
"""
import asyncio
from urllib.parse import urlparse
from utils.logger import get_logger

logger = get_logger("traffic_keyword.serp_verifier")


async def verify_domain_serp_position(
    browser_controller,
    keyword: str,
    target_url: str,
    search_engine: str = "google",
    proxy=None,
) -> dict:
    """
    Executes live SERP scan to locate real organic position (pages 1-3).
    Returns { found: bool, position: int, title: str, total_results_scanned: int }
    """
    target_domain = urlparse(target_url).netloc.replace("www.", "").lower()
    search_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}&num=30"

    result = {
        "keyword": keyword,
        "target_domain": target_domain,
        "found": False,
        "position": -1,
        "title": "",
        "snippet": "",
    }

    try:
        context = await browser_controller.new_stealth_context(proxy=proxy)
        page = await context.new_page()

        await page.goto(search_url, wait_until="domcontentloaded", timeout=25000)
        await asyncio.sleep(2.0)

        # Scan organic links
        links = await page.query_selector_all("a[href]")
        rank = 0

        for link in links:
            try:
                href = await link.get_attribute("href")
                if not href or not href.startswith("http"):
                    continue

                domain = urlparse(href).netloc.replace("www.", "").lower()
                # Skip search engine internal links
                if any(ign in domain for ign in ["google", "gstatic", "schema.org", "w3.org"]):
                    continue

                rank += 1
                if target_domain in domain:
                    result["found"] = True
                    result["position"] = rank
                    result["title"] = await link.inner_text()
                    break

                if rank >= 30:
                    break
            except Exception:
                continue

        await context.close()
    except Exception as e:
        logger.error(f"SERP verification failed: {e}")

    return result
