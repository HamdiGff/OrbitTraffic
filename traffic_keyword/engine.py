"""
Keyword-to-Traffic Flow Engine
Orchestrates end-to-end organic traffic generation with:
1. Pogo-Sticking (RankBrain competitor dissatisfaction -> Target satisfaction)
2. Multi-Page Organic Journeys (GA4 internal link exploration)
3. Persona pre-warming with authentic third-party cookies
4. Real-time telemetry callbacks
"""
import asyncio
import random
from typing import List, Optional, Dict
from dataclasses import dataclass, field
from utils.logger import get_logger
from behavior.pogo_sticking import execute_pogo_sticking_flow
from behavior.journey import OrganicJourneyEngine
from browser.persona import CookieFarmManager

logger = get_logger("traffic_keyword.engine")

SERP_CTR_BY_POSITION = {
    1: 0.287, 2: 0.153, 3: 0.097, 4: 0.071, 5: 0.051,
    6: 0.040, 7: 0.034, 8: 0.027, 9: 0.021, 10: 0.017,
}

SEARCH_ENGINES = {
    "google": "https://www.google.com/search?q={query}&hl={lang}",
    "bing": "https://www.bing.com/search?q={query}&setlang={lang}",
    "duckduckgo": "https://duckduckgo.com/?q={query}&kl={lang}",
}

REFERRER_SOURCES = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://duckduckgo.com/",
    "https://www.reddit.com/",
    "https://www.facebook.com/",
    "https://t.co/",
    "https://www.linkedin.com/",
    "",
]


@dataclass
class Keyword:
    text: str
    target_url: str
    search_engine: str = "google"
    language: str = "en"
    target_position: int = 1
    weight: float = 1.0
    daily_visits: int = 10
    enable_pogo: bool = True
    journey_hops: int = 2
    tags: List[str] = field(default_factory=list)

    def get_ctr(self) -> float:
        return SERP_CTR_BY_POSITION.get(self.target_position, 0.015)

    def get_search_url(self) -> str:
        tpl = SEARCH_ENGINES.get(self.search_engine, SEARCH_ENGINES["google"])
        return tpl.format(query=self.text.replace(" ", "+"), lang=self.language)

    def long_tail_variants(self) -> List[str]:
        base = self.text
        variants = [
            base,
            f"best {base}",
            f"{base} review",
            f"{base} 2026",
            f"how to {base}",
            f"{base} online",
            f"{base} guide",
        ]
        random.shuffle(variants)
        return variants[:2]


class KeywordEngine:
    def __init__(self, browser_controller, proxy_pool=None):
        self.browser = browser_controller
        self.proxy_pool = proxy_pool
        self.persona_manager = CookieFarmManager()
        self._session_count = 0

    async def execute_keyword_session(
        self,
        keyword: Keyword,
        fingerprint=None,
        progress_cb=None,
        action_cb=None,
    ) -> dict:
        import time
        result = {
            "keyword": keyword.text,
            "target": keyword.target_url,
            "success": False,
            "source": "organic_search",
            "dwell_seconds": 0,
            "timestamp": time.time(),
            "hops_completed": 1,
            "pogo_used": False,
            "proxy_ip": "Direct",
        }

        proxy = self.proxy_pool.get() if self.proxy_pool else None
        if proxy:
            result["proxy_ip"] = f"{proxy.host}:{proxy.port}"

        try:
            if action_cb:
                action_cb("Generating stealth fingerprint & persona...")

            from browser.fingerprint import FingerprintProfile
            from behavior.device_matrix import get_device_options
            fp = fingerprint or FingerprintProfile()
            dev_profile = get_device_options("auto")

            # Create context with mobile / desktop emulation
            context = await self.browser.new_stealth_context(
                profile=fp, proxy=proxy, device_profile=dev_profile
            )

            # Optional persona warm-up
            if random.random() < 0.4:
                if action_cb:
                    action_cb("Warming up cookies with authoritative seeds...")
                await self.persona_manager.warm_up_context(context, fast_mode=True)

            page = await context.new_page()

            search_url = self._pick_search_url(keyword)

            if keyword.enable_pogo and random.random() < 0.75:
                # Pogo-Sticking execution
                if action_cb:
                    action_cb(f"Executing Pogo-Stick simulation on '{keyword.text}'...")
                pogo_res = await execute_pogo_sticking_flow(
                    page=page,
                    search_url=search_url,
                    target_url=keyword.target_url,
                    target_min_dwell=30,
                    target_max_dwell=120,
                )
                result["pogo_used"] = pogo_res.get("pogo_executed", False)
                result["dwell_seconds"] = pogo_res.get("target_dwell", 0)
            else:
                # Direct or standard search
                if action_cb:
                    action_cb(f"Navigating to SERP for '{keyword.text}'...")
                dwell = await self.browser.search_and_click(
                    search_url=search_url,
                    target_url=keyword.target_url,
                    proxy=proxy,
                    fingerprint=fp,
                )
                result["dwell_seconds"] = dwell

            # Multi-Hop Organic Journey
            if keyword.journey_hops > 1:
                from urllib.parse import urlparse
                domain = urlparse(keyword.target_url).netloc
                journey_engine = OrganicJourneyEngine(page, target_domain=domain)
                if action_cb:
                    action_cb(f"Exploring internal site pages ({keyword.journey_hops} hops)...")
                journey_res = await journey_engine.execute_journey(
                    max_hops=keyword.journey_hops,
                    hop_min_dwell=15,
                    hop_max_dwell=45,
                )
                result["hops_completed"] = journey_res["total_hops"]
                result["dwell_seconds"] += journey_res["total_dwell_seconds"]

            await context.close()
            result["success"] = True
            self._session_count += 1

            if proxy:
                self.proxy_pool.mark_success(proxy)

        except Exception as e:
            logger.error(f"Keyword session failed: {e}")
            result["error"] = str(e)
            if proxy:
                self.proxy_pool.mark_failed(proxy)

        if progress_cb:
            progress_cb(result)
        return result

    def _pick_search_url(self, keyword: Keyword) -> str:
        engine = keyword.search_engine if keyword.search_engine in SEARCH_ENGINES else "google"
        tpl = SEARCH_ENGINES[engine]
        variant = random.choice(keyword.long_tail_variants())
        return tpl.format(query=variant.replace(" ", "+"), lang=keyword.language)

    async def run_campaign(
        self,
        keywords: List[Keyword],
        total_visits: int,
        concurrency: int = 3,
        on_progress=None,
        on_action=None,
    ):
        total_weight = sum(k.weight for k in keywords) or 1.0
        visit_plan = []
        for kw in keywords:
            visits = max(1, int((kw.weight / total_weight) * total_visits))
            visit_plan.extend([kw] * visits)

        random.shuffle(visit_plan)
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded_session(idx: int, kw: Keyword):
            async with semaphore:
                def worker_action(msg):
                    if on_action:
                        on_action(idx % concurrency + 1, msg, kw.text)

                res = await self.execute_keyword_session(
                    kw, progress_cb=on_progress, action_cb=worker_action
                )
                from behavior.dayparting import CircadianTrafficShaper
                intensity = CircadianTrafficShaper.get_current_intensity()
                base_delay = random.uniform(2, 6)
                # Night hours delay more naturally, peak hours flow faster
                pacing_delay = base_delay / max(0.2, intensity)
                await asyncio.sleep(pacing_delay)
                return res

        tasks = [bounded_session(i, kw) for i, kw in enumerate(visit_plan)]
        return await asyncio.gather(*tasks)
