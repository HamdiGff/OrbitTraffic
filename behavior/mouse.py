"""
Behavioral AI Engine — Human Mouse Movement
Generates realistic mouse paths using Bezier curves with overshoot,
microsaccades, fatigue, and speed variance.
"""
import random
import math
import asyncio
from typing import List, Tuple
import numpy as np
from utils.logger import get_logger

logger = get_logger("behavior.mouse")

Point = Tuple[float, float]


def _cubic_bezier(p0: Point, p1: Point, p2: Point, p3: Point, t: float) -> Point:
    """Compute cubic Bezier point at parameter t."""
    u = 1 - t
    x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
    y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
    return (x, y)


def _add_noise(x: float, y: float, intensity: float = 1.0) -> Point:
    """Add Gaussian noise for microsaccades / hand tremor."""
    return (
        x + random.gauss(0, intensity),
        y + random.gauss(0, intensity),
    )


def generate_mouse_path(
    start: Point,
    end: Point,
    overshoot: bool = True,
    tremor_intensity: float = 0.8,
    num_steps: int = 0,
    speed_profile: str = "natural",  # "natural" | "fast" | "slow"
) -> List[Tuple[Point, float]]:
    """
    Generate a list of (position, delay_ms) tuples representing a human mouse path.

    Args:
        start: Starting (x, y)
        end: Target (x, y)
        overshoot: Whether to simulate overshoot correction
        tremor_intensity: Hand tremor noise level
        num_steps: Number of path points (0 = auto)
        speed_profile: Movement speed characteristic
    Returns:
        List of ((x, y), delay_ms) for each step
    """
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx**2 + dy**2)

    if distance < 1:
        return [(end, 0)]

    # Auto steps based on distance
    if num_steps == 0:
        num_steps = max(20, int(distance / 5))

    # Bezier control points with random deviation
    deviation = min(distance * 0.4, 150)
    cp1 = (
        start[0] + dx * 0.3 + random.uniform(-deviation, deviation),
        start[1] + dy * 0.3 + random.uniform(-deviation, deviation),
    )
    cp2 = (
        start[0] + dx * 0.7 + random.uniform(-deviation, deviation),
        start[1] + dy * 0.7 + random.uniform(-deviation, deviation),
    )

    # Build base path
    path_points = []
    for i in range(num_steps + 1):
        t = i / num_steps
        pt = _cubic_bezier(start, cp1, cp2, end, t)
        path_points.append(pt)

    # Speed curve: ease-in-out with Gaussian distribution
    # Humans accelerate then decelerate
    t_values = np.linspace(0, 1, num_steps + 1)
    if speed_profile == "natural":
        speeds = np.exp(-8 * (t_values - 0.5) ** 2) + 0.1
    elif speed_profile == "fast":
        speeds = np.ones(num_steps + 1) * 0.3 + np.random.uniform(0, 0.1, num_steps + 1)
    else:  # slow
        speeds = np.ones(num_steps + 1) * 0.7 + np.random.uniform(0, 0.2, num_steps + 1)

    speeds = speeds / speeds.sum() * distance
    base_speed_ms = 0.5 if speed_profile == "fast" else 1.2

    result = []
    for i, pt in enumerate(path_points):
        # Add tremor noise
        noisy_pt = _add_noise(pt[0], pt[1], tremor_intensity * (1 - t_values[i] * 0.5))
        delay = max(1, speeds[i] * base_speed_ms + random.gauss(0, 0.3))
        result.append((noisy_pt, delay))

    # Overshoot simulation: continue 2-8px past target, then correct
    if overshoot and distance > 50 and random.random() < 0.4:
        overshoot_dist = random.uniform(2, 8)
        angle = math.atan2(dy, dx)
        overshoot_pt = (
            end[0] + math.cos(angle) * overshoot_dist,
            end[1] + math.sin(angle) * overshoot_dist,
        )
        correction_steps = random.randint(3, 8)
        for j in range(correction_steps):
            t = j / correction_steps
            pt = (
                overshoot_pt[0] + (end[0] - overshoot_pt[0]) * t,
                overshoot_pt[1] + (end[1] - overshoot_pt[1]) * t,
            )
            result.append((_add_noise(pt[0], pt[1], 0.3), random.uniform(5, 20)))

    return result


async def human_move_to(page, x: float, y: float, **kwargs):
    """
    Async helper: move Playwright page mouse along a human path to (x, y).
    """
    try:
        pos = await page.evaluate("() => ({ x: 0, y: 0 })")  # We start from last known or 0,0
        current = (0, 0)
        path = generate_mouse_path(current, (x, y), **kwargs)
        for (px, py), delay_ms in path:
            await page.mouse.move(px, py)
            await asyncio.sleep(delay_ms / 1000)
    except Exception as e:
        logger.warning(f"Mouse move error: {e}")
        await page.mouse.move(x, y)


async def human_click(page, x: float, y: float, button: str = "left"):
    """Click with pre-movement and human-like delay."""
    await human_move_to(page, x, y)
    # Pre-click pause (reaction time: 80–300ms Gaussian)
    await asyncio.sleep(max(0.05, random.gauss(0.15, 0.06)))
    await page.mouse.down(button=button)
    # Hold time: 60–180ms
    await asyncio.sleep(random.uniform(0.06, 0.18))
    await page.mouse.up(button=button)
    # Post-click drift
    drift_x = x + random.gauss(0, 3)
    drift_y = y + random.gauss(0, 3)
    await page.mouse.move(drift_x, drift_y)
