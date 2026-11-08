"""
Keyword-to-Traffic Flow Engine
Simulates: Google Search → result click → site browse → optional return visit.
Implements CTR curves, SERP position modeling, long-tail expansion, and bounce control.
"""
import asyncio
import random
import re
from typing import List, Optional, Dict
from dataclasses import dataclass, field
from utils.logger import get_logger

logger = get_logger("keyword.engine")

# Realistic organic CTR by SERP position (based on industry studies)
SERP_CTR_BY_POSITION = {
    1: 0.287,
    2: 0.153,
    3: 0.097,
    4: 0.071,
    5: 0.051,
    6: 0.040,
    7: 0.034,
    8: 0.027,
    9: 0.021,
    10: 0.017,
}

SEARCH_ENGINES = {
    "google": "https://www.google.com/search?q={query}&hl={lang}",
    "bing": "https://www.bing.com/search?q={query}&setlang={lang}",
    "duckduckgo": "https://duckduckgo.com/?q={query}&kl={lang}",
}

# Common referrer sources for organic traffic variety
REFERRER_SOURCES = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://duckduckgo.com/",
    "https://www.reddit.com/",
    "https://www.facebook.com/",
    "https://t.co/",  # Twitter/X
    "https://www.linkedin.com/",
    "https://news.ycombinator.com/",
    "",  # Direct traffic (no referrer)
]


@dataclass
class Keyword:
    text: str
    target_url: str
    search_engine: str = "google"
    language: str = "en"
    target_position: int = 1  # Desired SERP position to click
    weight: float = 1.0
    daily_visits: int = 10
    tags: List[str] = field(default_factory=list)

    def get_ctr(self) -> float:
        return SERP_CTR_BY_POSITION.get(self.target_position, 0.015)

    def get_search_url(self) -> str:
        tpl = SEARCH_ENGINES.get(self.search_engine, SEARCH_ENGINES["google"])
        return tpl.format(query=self.text.replace(" ", "+"), lang=self.language)

    def long_tail_variants(self) -> List[str]:
        """Generate long-tail variants of the keyword for natural search variety."""
        base = self.text
        variants = [
            base,
            f"best {base}",
            f"{base} review",
            f"{base} 2025",
            f"how to {base}",
            f"{base} near me",
            f"cheap {base}",
            f"{base} guide",
            f"what is {base}",
        ]
        # Shuffle and return a random subset
        random.shuffle(variants)
        return variants[:random.randint(1, 3)]


class KeywordEngine:
    """
    Orchestrates keyword → traffic sessions end-to-end.
    """

    def __init__(self, browser_controller, proxy_pool=None):
        self.browser = browser_controller
        self.proxy_pool = proxy_pool
        self._session_count = 0

    async def execute_keyword_session(
        self,
        keyword: Keyword,
        fingerprint=None,
        progress_cb=None,
    ) -> dict:
        """
        Full session: search → find result → click → browse target.
        Returns session result dict.
        """
        import time
        result = {
            "keyword": keyword.text, "target": keyword.target_url,
            "success": False, "source": "search",
            "dwell_seconds": 0, "timestamp": time.time(),
        }

        try:
            proxy = self.proxy_pool.get() if self.proxy_pool else None
            search_url = self._pick_search_url(keyword)

            # Randomly choose: direct or via search
            if random.random() < 0.25:
                # Direct traffic with referrer variation
                result["source"] = "direct"
                dwell = await self.browser.visit_url(
                    keyword.target_url,
                    proxy=proxy,
                    fingerprint=fingerprint,
                    referrer=random.choice(REFERRER_SOURCES),
                )
            else:
                # Search → click flow
                result["source"] = "organic_search"
                dwell = await self.browser.search_and_click(
                    search_url=search_url,
                    target_url=keyword.target_url,
                    proxy=proxy,
                    fingerprint=fingerprint,
                )

            result["dwell_seconds"] = dwell
            result["success"] = True
            self._session_count += 1

            if proxy:
                self.proxy_pool.mark_success(proxy)

        except Exception as e:
            logger.error(f"Keyword session failed for '{keyword.text}': {e}")
            result["error"] = str(e)
            if proxy:
                self.proxy_pool.mark_failed(proxy)

        if progress_cb:
            progress_cb(result)
        return result

    def _pick_search_url(self, keyword: Keyword) -> str:
        """Pick search URL with realistic engine distribution."""
        engine_weights = {"google": 0.91, "bing": 0.07, "duckduckgo": 0.02}
        engines = list(engine_weights.keys())
        weights = list(engine_weights.values())
        engine = random.choices(engines, weights=weights)[0]
        variant = random.choice(keyword.long_tail_variants())
        tpl = SEARCH_ENGINES[engine]
        return tpl.format(query=variant.replace(" ", "+"), lang=keyword.language)

    async def run_campaign(
        self,
        keywords: List[Keyword],
        total_visits: int,
        concurrency: int = 3,
        on_progress=None,
    ):
        """
        Run a full traffic campaign across multiple keywords.
        Distributes visits proportionally by keyword weight.
        """
        from browser.fingerprint import FingerprintProfile
        import asyncio

        total_weight = sum(k.weight for k in keywords)
        visit_plan = []
        for kw in keywords:
            visits = max(1, int((kw.weight / total_weight) * total_visits))
            visit_plan.extend([kw] * visits)

        random.shuffle(visit_plan)
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded_session(kw: Keyword):
            async with semaphore:
                fp = FingerprintProfile()
                res = await self.execute_keyword_session(kw, fingerprint=fp, progress_cb=on_progress)
                # Natural inter-session delay
                await asyncio.sleep(random.uniform(2, 15))
                return res

        tasks = [bounded_session(kw) for kw in visit_plan]
        return await asyncio.gather(*tasks)
