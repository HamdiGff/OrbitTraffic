"""
Browser Controller — Playwright-based real browser automation
with stealth patches, proxy support, and behavioral simulation integration.
"""
import asyncio
import random
from typing import Optional
from utils.logger import get_logger
from browser.fingerprint import FingerprintProfile, get_stealth_init_script, get_context_options
from behavior.mouse import human_click, human_move_to
from behavior.scroll import natural_page_dwell, human_scroll

logger = get_logger("browser.controller")

USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0",
]


class BrowserController:
    """
    Manages Playwright browser instances with stealth, fingerprinting, and proxy support.
    Supports headless and headed (visible) modes.
    """

    def __init__(self, headless: bool = True, browser_type: str = "chromium"):
        self.headless = headless
        self.browser_type = browser_type
        self._playwright = None
        self._browser = None
        self._initialized = False

    async def init(self):
        """Initialize Playwright and launch browser."""
        from playwright.async_api import async_playwright
        self._playwright = await async_playwright().start()

        launch_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-web-security",
            f"--window-size={random.randint(1200, 1920)},{random.randint(700, 1080)}",
            "--disable-notifications",
            "--disable-popup-blocking",
        ]

        browser_launcher = getattr(self._playwright, self.browser_type)
        self._browser = await browser_launcher.launch(
            headless=self.headless,
            args=launch_args,
            ignore_default_args=["--enable-automation"],
        )
        self._initialized = True
        logger.info(f"Browser launched: {self.browser_type}, headless={self.headless}")

    async def new_stealth_context(
        self,
        profile: Optional[FingerprintProfile] = None,
        proxy=None,
    ):
        """Create a new browser context with full stealth + fingerprint overrides."""
        if not self._initialized:
            await self.init()

        if profile is None:
            profile = FingerprintProfile()

        ctx_options = get_context_options(profile)

        # Random user agent
        ua = random.choice(USER_AGENTS)
        ctx_options["user_agent"] = ua

        # Proxy configuration
        if proxy:
            ctx_options["proxy"] = {
                "server": f"{proxy.proxy_type.value}://{proxy.host}:{proxy.port}",
            }
            if proxy.username and proxy.password:
                ctx_options["proxy"]["username"] = proxy.username
                ctx_options["proxy"]["password"] = proxy.password

        context = await self._browser.new_context(**ctx_options)

        # Inject stealth scripts into every page
        init_script = get_stealth_init_script(profile)
        await context.add_init_script(init_script)

        # Seed cookies to simulate a returning user
        await self._seed_cookies(context, profile)

        return context

    async def _seed_cookies(self, context, profile: FingerprintProfile):
        """
        Pre-seed browser with analytics/ad cookies to simulate a returning user.
        This makes the browser look like it has browsing history.
        """
        import time
        base_domain = "google.com"
        cookies = [
            {
                "name": "_ga",
                "value": f"GA1.1.{random.randint(100000000, 999999999)}.{int(time.time()) - random.randint(86400, 7776000)}",
                "domain": f".{base_domain}",
                "path": "/",
                "expires": int(time.time()) + 63072000,
                "httpOnly": False,
                "secure": True,
                "sameSite": "Lax",
            },
            {
                "name": "_gid",
                "value": f"GA1.1.{random.randint(100000000, 999999999)}.{int(time.time())}",
                "domain": f".{base_domain}",
                "path": "/",
                "expires": int(time.time()) + 86400,
                "httpOnly": False,
                "secure": True,
                "sameSite": "Lax",
            },
        ]
        try:
            await context.add_cookies(cookies)
        except Exception:
            pass

    async def visit_url(
        self,
        url: str,
        proxy=None,
        fingerprint: Optional[FingerprintProfile] = None,
        referrer: str = "",
        min_dwell: float = 20,
        max_dwell: float = 180,
    ) -> float:
        """
        Visit a URL with human behavior simulation.
        Returns actual dwell time in seconds.
        """
        context = await self.new_stealth_context(profile=fingerprint, proxy=proxy)
        try:
            page = await context.new_page()

            # Navigate with realistic referer
            nav_options = {"wait_until": "domcontentloaded", "timeout": 30000}
            if referrer:
                nav_options["referer"] = referrer

            await page.goto(url, **nav_options)

            # Initial pause (page loading perception)
            await asyncio.sleep(random.uniform(0.5, 2.0))

            # Simulate reading + scrolling
            dwell = await natural_page_dwell(page, min_seconds=min_dwell, max_seconds=max_dwell)

            # Random link hover (increases engagement signals)
            await self._random_link_interactions(page)

            logger.info(f"Visited {url} — dwell: {dwell:.1f}s")
            return dwell

        except Exception as e:
            logger.error(f"visit_url failed for {url}: {e}")
            return 0
        finally:
            await context.close()

    async def search_and_click(
        self,
        search_url: str,
        target_url: str,
        proxy=None,
        fingerprint: Optional[FingerprintProfile] = None,
    ) -> float:
        """
        Full organic search flow:
        1. Go to search engine
        2. Wait + scan results (simulating reading SERP)
        3. Find and click matching result
        4. Browse target page with human behavior
        """
        from urllib.parse import urlparse

        context = await self.new_stealth_context(profile=fingerprint, proxy=proxy)
        try:
            page = await context.new_page()

            # === STEP 1: Search engine ===
            await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(random.uniform(1.0, 3.0))

            # Scroll through SERP as if reading
            await human_scroll(page, target_pixels=random.randint(200, 800), reading_mode=False)
            await asyncio.sleep(random.uniform(0.5, 2.0))

            # === STEP 2: Find target result ===
            target_domain = urlparse(target_url).netloc.replace("www.", "")
            clicked = False

            # Try to find link matching target domain
            links = await page.query_selector_all("a[href]")
            for link in links:
                try:
                    href = await link.get_attribute("href")
                    if href and target_domain in href:
                        # Move to and click the link
                        bbox = await link.bounding_box()
                        if bbox:
                            await human_click(page, bbox["x"] + bbox["width"] / 2, bbox["y"] + bbox["height"] / 2)
                            clicked = True
                            break
                except Exception:
                    continue

            if not clicked:
                # Fallback: direct navigation with search referrer
                await page.goto(target_url, wait_until="domcontentloaded", referer=search_url)

            await asyncio.sleep(random.uniform(0.5, 1.5))

            # === STEP 3: Browse target ===
            dwell = await natural_page_dwell(page, min_seconds=25, max_seconds=200)
            await self._random_link_interactions(page)

            return dwell

        except Exception as e:
            logger.error(f"search_and_click failed: {e}")
            return 0
        finally:
            await context.close()

    async def _random_link_interactions(self, page):
        """Hover over random links — increases engagement signals without navigating."""
        try:
            if random.random() < 0.5:
                links = await page.query_selector_all("a[href]")
                candidates = links[:min(len(links), 20)]
                for _ in range(random.randint(1, 4)):
                    if candidates:
                        link = random.choice(candidates)
                        bbox = await link.bounding_box()
                        if bbox:
                            await human_move_to(page, bbox["x"] + bbox["width"] / 2, bbox["y"])
                            await asyncio.sleep(random.uniform(0.3, 1.5))
        except Exception:
            pass

    async def close(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._initialized = False
