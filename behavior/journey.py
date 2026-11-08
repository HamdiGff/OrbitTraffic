"""
Multi-Page Organic Journey Engine
Simulates full multi-hop browsing sessions on target websites:
1. Enter via Search / Direct / Social Referrer
2. Dwell & read first page
3. Extract valid internal domain links (filtering out login, logout, external, mailto, etc.)
4. Navigate through 1 to 4 internal pages in sequence
5. Micro-interactions: random scroll bursts, mouse hovering over headlines, simulated text highlights
6. Flawless GA4 / Google Analytics session depth & engagement time metrics
"""
import asyncio
import random
from urllib.parse import urlparse, urljoin
from utils.logger import get_logger
from behavior.mouse import human_click, human_move_to
from behavior.scroll import natural_page_dwell, human_scroll

logger = get_logger("behavior.journey")


class OrganicJourneyEngine:
    def __init__(self, page, target_domain: str):
        self.page = page
        self.target_domain = target_domain.replace("www.", "").lower()
        self.visited_urls = set()

    async def extract_internal_links(self) -> list:
        """Find clickable, relevant internal navigation links."""
        candidates = []
        try:
            elements = await self.page.query_selector_all("a[href]")
            current_url = self.page.url

            for el in elements:
                try:
                    href = await el.get_attribute("href")
                    if not href:
                        continue

                    # Clean absolute URL
                    full_url = urljoin(current_url, href)
                    parsed = urlparse(full_url)

                    # Verify same domain
                    domain = parsed.netloc.replace("www.", "").lower()
                    if domain != self.target_domain:
                        continue

                    # Filter out fragments, downloads, auth paths, or already visited
                    path = parsed.path.lower()
                    if any(path.endswith(ext) for ext in [".pdf", ".jpg", ".png", ".zip", ".exe"]):
                        continue
                    if any(sub in path for sub in ["logout", "signout", "cart", "checkout", "login", "register"]):
                        continue
                    if full_url in self.visited_urls or full_url == current_url:
                        continue

                    # Check visibility
                    is_visible = await el.is_visible()
                    if is_visible:
                        candidates.append((el, full_url))
                except Exception:
                    continue
        except Exception as e:
            logger.debug(f"Link extraction warning: {e}")

        return candidates

    async def simulate_micro_gestures(self):
        """Simulate realistic micro-gestures: headline hover, text selection, subtle mouse wandering."""
        try:
            # 1. Hover on major headlines
            headings = await self.page.query_selector_all("h1, h2, h3, p")
            if headings and random.random() < 0.7:
                sample_headings = random.sample(headings, min(len(headings), 3))
                for h in sample_headings:
                    box = await h.bounding_box()
                    if box and box["width"] > 20 and box["height"] > 10:
                        await human_move_to(self.page, box["x"] + random.uniform(10, box["width"] * 0.8), box["y"] + 10)
                        await asyncio.sleep(random.uniform(0.4, 1.2))

            # 2. Text selection simulation (frequently done by curious human readers)
            if random.random() < 0.35:
                paragraphs = await self.page.query_selector_all("p")
                if paragraphs:
                    p = random.choice(paragraphs)
                    box = await p.bounding_box()
                    if box:
                        start_x = box["x"] + 15
                        start_y = box["y"] + 10
                        end_x = start_x + random.uniform(80, min(250, box["width"] - 20))
                        await self.page.mouse.move(start_x, start_y)
                        await self.page.mouse.down()
                        await self.page.mouse.move(end_x, start_y)
                        await asyncio.sleep(random.uniform(0.3, 0.8))
                        await self.page.mouse.up()
                        # Click elsewhere to deselect
                        await self.page.mouse.click(box["x"] + 5, box["y"] + 5)
        except Exception:
            pass

    async def execute_journey(
        self,
        max_hops: int = 3,
        hop_min_dwell: float = 20,
        hop_max_dwell: float = 75,
    ) -> dict:
        """
        Execute deep journey through multiple internal pages.
        """
        journey_log = []
        current_url = self.page.url
        self.visited_urls.add(current_url)

        # First page initial dwell
        first_dwell = await natural_page_dwell(self.page, min_seconds=hop_min_dwell, max_seconds=hop_max_dwell)
        await self.simulate_micro_gestures()
        journey_log.append({"url": current_url, "dwell_seconds": round(first_dwell, 1)})

        for hop_index in range(1, max_hops):
            # Roll probability to continue journey (decay curve: 75% -> 50% -> 30%)
            continue_prob = max(0.2, 0.85 - (hop_index * 0.25))
            if random.random() > continue_prob:
                logger.info(f"Journey stopped naturally at hop {hop_index}")
                break

            # Find next internal page
            internal_links = await self.extract_internal_links()
            if not internal_links:
                logger.info("No more unvisited internal links found. Concluding journey.")
                break

            link_el, next_url = random.choice(internal_links[:5])
            logger.info(f"Journey Hop {hop_index + 1}: Navigating to {next_url}")

            try:
                box = await link_el.bounding_box()
                if box:
                    await human_click(self.page, box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                    await self.page.wait_for_load_state("domcontentloaded", timeout=15000)
                else:
                    await self.page.goto(next_url, wait_until="domcontentloaded", timeout=15000)

                self.visited_urls.add(next_url)
                await asyncio.sleep(random.uniform(1.0, 2.5))

                dwell = await natural_page_dwell(self.page, min_seconds=hop_min_dwell, max_seconds=hop_max_dwell)
                await self.simulate_micro_gestures()
                journey_log.append({"url": next_url, "dwell_seconds": round(dwell, 1)})

            except Exception as e:
                logger.warning(f"Hop navigation error: {e}")
                break

        total_dwell = sum(item["dwell_seconds"] for item in journey_log)
        return {
            "total_hops": len(journey_log),
            "total_dwell_seconds": round(total_dwell, 1),
            "pages": journey_log,
        }
