"""
Persona & Cookie Farming Engine
Generates authentic browsing identities and pre-warms browser contexts.
Before hitting target sites, a realistic user profile acquires legitimate
third-party cookies from authoritative domains (Wikipedia, News, Reddit, Tech blogs),
ensuring Google Analytics and Cloudflare see genuine browsing history.
"""
import random
import time
import os
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from utils.logger import get_logger

logger = get_logger("browser.persona")

WARMUP_SEED_DOMAINS = [
    "https://en.wikipedia.org/wiki/Special:Random",
    "https://news.ycombinator.com/",
    "https://www.bbc.com/news",
    "https://www.reddit.com/r/technology/",
    "https://medium.com/",
    "https://github.com/explore",
]

INTEREST_CATEGORIES = [
    "Tech & Software", "Health & Fitness", "Finance & Crypto",
    "Travel & Hospitality", "E-commerce & Fashion", "Education & Science"
]


@dataclass
class BrowserPersona:
    id: str
    name: str
    age: int
    gender: str
    category: str
    locale: str
    device_type: str  # desktop | mobile
    created_at: float = field(default_factory=time.time)
    sessions_completed: int = 0
    cookies_stored: List[Dict] = field(default_factory=list)

    @classmethod
    def generate(cls, locale: str = "en-US") -> "BrowserPersona":
        first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Jamie", "Pat", "Riley", "Casey"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson", "Anderson"]
        persona_id = f"pers_{random.randint(100000, 999999)}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        age = random.randint(21, 58)
        gender = random.choice(["M", "F", "Other"])
        category = random.choice(INTEREST_CATEGORIES)
        device = "desktop" if random.random() < 0.8 else "mobile"

        return cls(
            id=persona_id,
            name=name,
            age=age,
            gender=gender,
            category=category,
            locale=locale,
            device_type=device,
        )


class CookieFarmManager:
    """Manages persona creation, storage, and pre-warming routines."""

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = storage_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "config", "personas"
        )
        os.makedirs(self.storage_dir, exist_ok=True)
        self.personas: List[BrowserPersona] = []
        self._load_all()

    def _load_all(self):
        for f in os.listdir(self.storage_dir):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(self.storage_dir, f), "r") as fp:
                        data = json.load(fp)
                        self.personas.append(BrowserPersona(**data))
                except Exception:
                    pass

    def get_or_create(self, locale: str = "en-US") -> BrowserPersona:
        if self.personas:
            p = random.choice(self.personas)
            p.sessions_completed += 1
            return p
        p = BrowserPersona.generate(locale=locale)
        self.personas.append(p)
        self.save(p)
        return p

    def save(self, persona: BrowserPersona):
        path = os.path.join(self.storage_dir, f"{persona.id}.json")
        try:
            with open(path, "w") as fp:
                json.dump(persona.__dict__, fp, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist persona {persona.id}: {e}")

    async def warm_up_context(self, context, fast_mode: bool = True):
        """
        Visits 1-2 authoritative seed domains to organically harvest authentic cookies.
        """
        targets = random.sample(WARMUP_SEED_DOMAINS, 1 if fast_mode else 2)
        logger.info(f"Warming up browser context with {len(targets)} seeds...")

        page = await context.new_page()
        try:
            for url in targets:
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=12000)
                    # Quick scroll
                    await page.mouse.wheel(0, random.randint(200, 500))
                    await asyncio.sleep(random.uniform(1.0, 2.5))
                except Exception:
                    continue
        finally:
            await page.close()
        logger.info("Context pre-warming finished.")
