"""
Scroll Behavior Simulation
Human-like scrolling with fatigue model, speed decay, random pauses, and reading simulation.
"""
import asyncio
import random
import math
from utils.logger import get_logger

logger = get_logger("behavior.scroll")


async def human_scroll(
    page,
    target_pixels: int = None,
    reading_mode: bool = True,
    words_per_minute: int = None,
):
    """
    Simulate human scrolling behavior on a page.

    Args:
        page: Playwright page object
        target_pixels: Total pixels to scroll (None = scroll to natural stopping point)
        reading_mode: If True, pause based on content density for realistic dwell
        words_per_minute: Reading speed (default: random 180-280 WPM)
    """
    if words_per_minute is None:
        words_per_minute = random.randint(180, 280)

    if target_pixels is None:
        # Get page height
        try:
            page_height = await page.evaluate("document.body.scrollHeight")
            viewport_height = await page.evaluate("window.innerHeight")
            # Humans rarely scroll to the absolute bottom; stop at 60-90%
            stop_fraction = random.uniform(0.55, 0.92)
            target_pixels = int((page_height - viewport_height) * stop_fraction)
        except Exception:
            target_pixels = random.randint(1000, 4000)

    target_pixels = max(100, target_pixels)
    scrolled = 0

    # --- Fatigue model: scroll bursts with pauses ---
    while scrolled < target_pixels:
        remaining = target_pixels - scrolled

        # Burst: scroll 80-350px at a time
        burst_size = random.randint(80, min(350, remaining + 1))

        # Speed decreases as fatigue increases (more scrolled → slower)
        fatigue_factor = 1.0 - (scrolled / target_pixels) * 0.4
        num_micro_steps = random.randint(3, 8)
        step_size = burst_size / num_micro_steps

        for _ in range(num_micro_steps):
            jitter = random.gauss(0, step_size * 0.15)
            actual_step = max(10, step_size + jitter)
            await page.mouse.wheel(0, actual_step)
            # Micro-delay between wheel events (10-40ms)
            await asyncio.sleep(random.uniform(0.010, 0.040) / fatigue_factor)

        scrolled += burst_size

        # Reading pause probability increases mid-page
        pause_chance = 0.35 + (scrolled / target_pixels) * 0.25
        if reading_mode and random.random() < pause_chance:
            # Estimate reading time for viewport content (assume ~200 words visible)
            words_visible = random.randint(80, 250)
            read_seconds = (words_visible / words_per_minute) * 60
            read_seconds *= random.uniform(0.6, 1.4)  # Variance
            read_seconds = min(read_seconds, 8.0)  # Cap at 8 seconds
            await asyncio.sleep(max(0.3, read_seconds))
        else:
            # Short pause between bursts (100-600ms)
            await asyncio.sleep(random.uniform(0.08, 0.6))

        # Occasional upward scroll (re-reading)
        if random.random() < 0.08 and scrolled > 300:
            reread_px = random.randint(50, 200)
            await page.mouse.wheel(0, -reread_px)
            scrolled = max(0, scrolled - reread_px)
            await asyncio.sleep(random.uniform(0.5, 2.5))

        # Occasional long pause (distraction / phone check)
        if random.random() < 0.04:
            await asyncio.sleep(random.uniform(2.0, 8.0))


async def natural_page_dwell(page, min_seconds: float = 20, max_seconds: float = 180):
    """
    Simulate full-page dwell: initial reading, scrolling, micro-interactions.
    Returns actual time spent (seconds).
    """
    import time
    start = time.time()

    # Initial static read (above-the-fold)
    await asyncio.sleep(random.uniform(1.5, 4.0))

    # Scroll through page
    await human_scroll(page, reading_mode=True)

    # Possible scroll back up
    if random.random() < 0.3:
        back_px = random.randint(300, 1500)
        await page.mouse.wheel(0, -back_px)
        await asyncio.sleep(random.uniform(1.0, 4.0))

    # Pad to minimum dwell time
    elapsed = time.time() - start
    if elapsed < min_seconds:
        additional = random.uniform(min_seconds - elapsed, max_seconds - elapsed)
        await asyncio.sleep(max(0, additional))

    return time.time() - start
