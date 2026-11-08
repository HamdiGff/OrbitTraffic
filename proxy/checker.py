"""
Async Proxy Checker & Manager
Validates proxies concurrently with configurable timeout, type detection,
geolocation, latency scoring, and auto-rotation logic.
"""
import asyncio
import aiohttp
import time
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict
from utils.logger import get_logger

logger = get_logger("proxy.checker")

TEST_URLS = [
    "https://httpbin.org/ip",
    "https://api.ipify.org?format=json",
    "https://ip-api.com/json",
]

PROXY_PATTERN = re.compile(
    r"^(?P<proto>https?|socks[45])?:?"
    r"/{0,2}(?:(?P<user>[^:@]+):(?P<password>[^@]+)@)?"
    r"(?P<host>[^:@/]+):(?P<port>\d{2,5})$"
)


class ProxyType(str, Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"
    UNKNOWN = "unknown"


class ProxyStatus(str, Enum):
    UNCHECKED = "unchecked"
    ALIVE = "alive"
    DEAD = "dead"
    SLOW = "slow"


@dataclass
class Proxy:
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: ProxyType = ProxyType.HTTP
    status: ProxyStatus = ProxyStatus.UNCHECKED
    latency_ms: float = 0.0
    country: str = ""
    city: str = ""
    isp: str = ""
    is_anonymous: bool = True
    failure_count: int = 0
    success_count: int = 0
    last_checked: float = 0.0
    tags: List[str] = field(default_factory=list)

    @property
    def url(self) -> str:
        proto = self.proxy_type.value
        if self.username and self.password:
            return f"{proto}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{proto}://{self.host}:{self.port}"

    @property
    def health_score(self) -> float:
        """0.0–1.0 health score based on latency + success rate."""
        if self.success_count + self.failure_count == 0:
            return 0.5
        success_rate = self.success_count / (self.success_count + self.failure_count)
        latency_score = max(0, 1 - self.latency_ms / 10000)
        return success_rate * 0.6 + latency_score * 0.4

    def to_dict(self) -> dict:
        return {
            "host": self.host, "port": self.port,
            "username": self.username, "password": self.password,
            "proxy_type": self.proxy_type.value, "status": self.status.value,
            "latency_ms": self.latency_ms, "country": self.country,
            "city": self.city, "isp": self.isp, "health_score": round(self.health_score, 3),
        }

    @classmethod
    def from_string(cls, proxy_str: str) -> Optional["Proxy"]:
        proxy_str = proxy_str.strip()
        m = PROXY_PATTERN.match(proxy_str)
        if not m:
            return None
        g = m.groupdict()
        proto = (g.get("proto") or "http").lower()
        ptype_map = {
            "http": ProxyType.HTTP, "https": ProxyType.HTTPS,
            "socks4": ProxyType.SOCKS4, "socks5": ProxyType.SOCKS5,
        }
        return cls(
            host=g["host"], port=int(g["port"]),
            username=g.get("user"), password=g.get("password"),
            proxy_type=ptype_map.get(proto, ProxyType.HTTP),
        )


async def _check_single(proxy: Proxy, timeout: int = 10) -> Proxy:
    """Check a single proxy against test URLs and update its status."""
    connector_kwargs = {}
    proxy_url = proxy.url

    # Build aiohttp connector
    try:
        from aiohttp_socks import ProxyConnector, ProxyType as SocksType
        if proxy.proxy_type in (ProxyType.SOCKS4, ProxyType.SOCKS5):
            st = SocksType.SOCKS5 if proxy.proxy_type == ProxyType.SOCKS5 else SocksType.SOCKS4
            connector = ProxyConnector(
                proxy_type=st, host=proxy.host, port=proxy.port,
                username=proxy.username, password=proxy.password,
                rdns=True,
            )
        else:
            connector = aiohttp.TCPConnector(ssl=False)
    except ImportError:
        connector = aiohttp.TCPConnector(ssl=False)
        proxy_url = proxy.url

    start = time.monotonic()
    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            kw = {"timeout": aiohttp.ClientTimeout(total=timeout)}
            if proxy.proxy_type in (ProxyType.HTTP, ProxyType.HTTPS):
                kw["proxy"] = proxy.url
            async with session.get(TEST_URLS[1], **kw) as resp:
                if resp.status == 200:
                    proxy.latency_ms = (time.monotonic() - start) * 1000
                    proxy.status = ProxyStatus.SLOW if proxy.latency_ms > 5000 else ProxyStatus.ALIVE
                    proxy.success_count += 1
                    # Try geo-lookup
                    try:
                        geo_url = f"http://ip-api.com/json/{proxy.host}?fields=country,city,isp,proxy"
                        async with session.get(geo_url, timeout=aiohttp.ClientTimeout(total=5)) as gr:
                            if gr.status == 200:
                                geo = await gr.json()
                                proxy.country = geo.get("country", "")
                                proxy.city = geo.get("city", "")
                                proxy.isp = geo.get("isp", "")
                                proxy.is_anonymous = geo.get("proxy", False)
                    except Exception:
                        pass
                else:
                    proxy.status = ProxyStatus.DEAD
                    proxy.failure_count += 1
    except Exception as e:
        proxy.status = ProxyStatus.DEAD
        proxy.failure_count += 1
        logger.debug(f"Proxy {proxy.host}:{proxy.port} failed: {type(e).__name__}")
    finally:
        proxy.last_checked = time.time()

    return proxy


async def check_proxies_bulk(
    proxies: List[Proxy],
    timeout: int = 10,
    concurrency: int = 50,
    on_progress=None,
) -> List[Proxy]:
    """
    Check a list of proxies concurrently.
    Calls on_progress(checked, total) after each result.
    """
    semaphore = asyncio.Semaphore(concurrency)
    results = []
    total = len(proxies)
    checked = 0

    async def bounded_check(p: Proxy) -> Proxy:
        nonlocal checked
        async with semaphore:
            result = await _check_single(p, timeout)
            checked += 1
            if on_progress:
                on_progress(checked, total)
            return result

    tasks = [bounded_check(p) for p in proxies]
    results = await asyncio.gather(*tasks)
    alive = sum(1 for p in results if p.status == ProxyStatus.ALIVE)
    logger.info(f"Proxy check complete: {alive}/{total} alive")
    return list(results)


def parse_proxy_list(text: str) -> List[Proxy]:
    """Parse a newline-separated proxy list string into Proxy objects."""
    proxies = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        proxy = Proxy.from_string(line)
        if proxy:
            proxies.append(proxy)
        else:
            logger.warning(f"Could not parse proxy: {line!r}")
    return proxies


class ProxyPool:
    """
    Manages a pool of proxies with smart rotation strategies.
    Strategies: round_robin | least_used | best_health | random
    """

    def __init__(self, strategy: str = "best_health"):
        self.proxies: List[Proxy] = []
        self.strategy = strategy
        self._rr_index = 0
        self._cooldowns: Dict[str, float] = {}
        self.cooldown_secs: int = 60

    def add(self, proxy: Proxy):
        self.proxies.append(proxy)

    def add_many(self, proxies: List[Proxy]):
        self.proxies.extend(proxies)

    def alive(self) -> List[Proxy]:
        now = time.time()
        return [
            p for p in self.proxies
            if p.status == ProxyStatus.ALIVE
            and now - self._cooldowns.get(p.url, 0) > self.cooldown_secs
        ]

    def get(self) -> Optional[Proxy]:
        candidates = self.alive()
        if not candidates:
            return None

        if self.strategy == "round_robin":
            p = candidates[self._rr_index % len(candidates)]
            self._rr_index += 1
        elif self.strategy == "best_health":
            p = max(candidates, key=lambda x: x.health_score)
        elif self.strategy == "least_used":
            p = min(candidates, key=lambda x: x.success_count)
        else:
            import random
            p = random.choice(candidates)

        return p

    def mark_failed(self, proxy: Proxy):
        proxy.failure_count += 1
        if proxy.failure_count >= 3:
            proxy.status = ProxyStatus.DEAD
        self._cooldowns[proxy.url] = time.time()

    def mark_success(self, proxy: Proxy):
        proxy.success_count += 1

    def stats(self) -> dict:
        total = len(self.proxies)
        alive = len([p for p in self.proxies if p.status == ProxyStatus.ALIVE])
        dead = len([p for p in self.proxies if p.status == ProxyStatus.DEAD])
        return {"total": total, "alive": alive, "dead": dead, "unchecked": total - alive - dead}
