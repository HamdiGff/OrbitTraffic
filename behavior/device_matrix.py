"""
Device Matrix & Mobile Touch Emulation
Provides authentic mobile and tablet profiles with genuine TouchEvent APIs,
mobile user-agents, device pixel ratios, and viewport dimensions.
Over 60% of real Google searches happen on mobile devices.
"""
import random
from typing import Dict, Optional

MOBILE_DEVICES = [
    {
        "name": "Apple iPhone 15 Pro",
        "viewport": {"width": 393, "height": 852},
        "device_scale_factor": 3.0,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        "sec_ch_ua": '"Chromium";v="131", "AppleWebKit";v="605"',
        "platform": "iPhone",
    },
    {
        "name": "Samsung Galaxy S24 Ultra",
        "viewport": {"width": 412, "height": 915},
        "device_scale_factor": 2.625,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Mobile Safari/537.36",
        "sec_ch_ua": '"Android";v="14", "Chrome";v="131"',
        "platform": "Linux armv8l",
    },
    {
        "name": "Google Pixel 8 Pro",
        "viewport": {"width": 412, "height": 892},
        "device_scale_factor": 2.625,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Mobile Safari/537.36",
        "sec_ch_ua": '"Android";v="14", "Google Chrome";v="131"',
        "platform": "Linux aarch64",
    },
    {
        "name": "Apple iPad Pro 11",
        "viewport": {"width": 834, "height": 1194},
        "device_scale_factor": 2.0,
        "is_mobile": False,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        "sec_ch_ua": '"AppleWebKit";v="605"',
        "platform": "iPad",
    },
]


def get_random_mobile_profile() -> Dict:
    return random.choice(MOBILE_DEVICES)


def get_device_options(device_type: str = "auto") -> Optional[Dict]:
    """
    device_type: 'desktop' | 'mobile' | 'auto'
    In 'auto' mode, simulates 60% mobile / 40% desktop distribution.
    """
    if device_type == "mobile" or (device_type == "auto" and random.random() < 0.60):
        return get_random_mobile_profile()
    return None
