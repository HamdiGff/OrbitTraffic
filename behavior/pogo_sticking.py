"""
Advanced Behavioral Module — RankBrain Pogo-Sticking Algorithm
Simulates the 'Pogo-Sticking' effect in search engines:
A user searches, clicks a competitor link, quickly bounces back to SERP (dissatisfied),
then clicks the target client website and stays for a long dwell time + interacts.
This is one of Google's strongest RankBrain ranking signals for user satisfaction.
"""
import asyncio
import random
from urllib.parse import urlparse
from utils.logger import get_logger
from behavior.mouse import human_click, human_move_to
from behavior.scroll import human_scroll, natural_page_dwell

logger = get_logger("behavior.pogo_sticking")


async def execute_pogo_sticking_flow(
    page,
    search_url: str,
    target_url: str,
    competitor_dwell_range: tuple = (3, 7),
    target_min_dwell: float = 60,
    target_max_dwell: float = 240,
) -> dict:
    """
    Executes a high-potency Pogo-Sticking user journey:
    1. Navigate to Search Engine (Google / Bing / DuckDuckGo)
    2. Identify top organic competitor results
    3. Click competitor, dwell briefly (3-7s), scroll minimally -> Discontent signal
    4. Hit browser back button -> Return to SERP
    5. Find target URL, click with intent
    6. Conduct deep reading dwell (60-240s) + multi-section engagement -> Satisfaction signal
    """
    stats = {
        "competitor_visited": None,
        "competitor_dwell": 0,
        "target_dwell": 0,
        "success": False,
        "pogo_executed": False,
    }

    target_domain = urlparse(target_url).netloc.replace("www.", "").lower()

    # Step 1: Navigate to Search Engine
    logger.info(f"Pogo-Stick: Navigating to SERP -> {search_url[:60]}...")
    await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(random.uniform(1.5, 3.0))

    # Natural SERP scanning scroll
    await human_scroll(page, target_pixels=random.randint(250, 600), reading_mode=False)
    await asyncio.sleep(random.uniform(1.0, 2.0))

    # Step 2: Discover organic competitor links
    all_links = await page.query_selector_all("a[href]")
    competitor_candidates = []

    for link in all_links:
        try:
            href = await link.get_attribute("href")
            if not href or not href.startswith("http"):
                continue
            parsed = urlparse(href)
            domain = parsed.netloc.replace("www.", "").lower()

            # Exclude search engine internal links, target domain, and ad domains
            ignored = [
                "google", "googleusercontent", "gstatic", "bing", "duckduckgo",
                "youtube", "schema.org", "wikipedia.org", target_domain
            ]
            if not any(ign in domain for ign in ignored) and len(domain) > 3:
                competitor_candidates.append((link, href, domain))
        except Exception:
            continue

    # Step 3: Pogo-stick on a competitor (if found)
    if competitor_candidates and random.random() < 0.85:
        comp_link, comp_href, comp_domain = random.choice(competitor_candidates[:3])
        logger.info(f"Pogo-Stick: Simulating competitor bounce on {comp_domain}")
        stats["competitor_visited"] = comp_domain

        try:
            bbox = await comp_link.bounding_box()
            if bbox:
                await human_click(page, bbox["x"] + bbox["width"] / 2, bbox["y"] + bbox["height"] / 2)
            else:
                await page.goto(comp_href, wait_until="domcontentloaded", timeout=20000)

            # Short dwell on competitor (3-7s) showing dissatisfaction
            dwell = random.uniform(*competitor_dwell_range)
            stats["competitor_dwell"] = round(dwell, 1)
            # Quick shallow scroll
            await page.mouse.wheel(0, random.randint(150, 350))
            await asyncio.sleep(dwell)

            # Step 4: Click Back button to return to SERP
            logger.info("Pogo-Stick: User dissatisfied -> Clicking Back to SERP")
            await page.go_back(wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(random.uniform(1.5, 3.5))
            stats["pogo_executed"] = True

        except Exception as e:
            logger.warning(f"Competitor bounce failed, recovering to SERP: {e}")
            await page.goto(search_url, wait_until="domcontentloaded", timeout=20000)

    # Step 5: Locate Target Result on SERP
    logger.info(f"Pogo-Stick: Finding target domain '{target_domain}' on SERP")
    target_link = None
    all_links_after = await page.query_selector_all("a[href]")

    for link in all_links_after:
        try:
            href = await link.get_attribute("href")
            if href and target_domain in href.lower():
                target_link = link
                break
        except Exception:
            continue

    if target_link:
        bbox = await target_link.bounding_box()
        if bbox:
            await human_click(page, bbox["x"] + bbox["width"] / 2, bbox["y"] + bbox["height"] / 2)
        else:
            await page.goto(target_url, wait_until="domcontentloaded", referer=page.url)
    else:
        # Fallback to direct navigation with search referrer
        logger.info(f"Target not visible on 1st page, navigating with SERP referrer")
        await page.goto(target_url, wait_until="domcontentloaded", referer=search_url)

    # Step 6: Deep Dwell and Reading on Target Site
    dwell = await natural_page_dwell(page, min_seconds=target_min_dwell, max_seconds=target_max_dwell)
    stats["target_dwell"] = round(dwell, 1)
    stats["success"] = True

    logger.info(f"Pogo-Stick Completed! Target dwell: {dwell:.1f}s | Pogo: {stats['pogo_executed']}")
    return stats
