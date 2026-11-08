"""
Natural Dayparting & Circadian Traffic Shaping Module
Human organic traffic follows bimodal daily curves (morning rush, afternoon peak, night lull).
This module calculates dynamic hourly multipliers based on the target audience's timezone,
preventing flat 24/7 robotic traffic patterns that trigger Google Analytics anomaly detection.
"""
import math
import datetime
from typing import Dict


class CircadianTrafficShaper:
    """
    Simulates authentic 24-hour human activity curves using a bimodal Gaussian distribution.
    Peak 1: 11:30 AM (lunch research)
    Peak 2: 8:45 PM (evening leisure browsing)
    Lull: 3:00 AM - 5:00 AM (sleep)
    """

    @staticmethod
    def get_hourly_multiplier(hour: int) -> float:
        """
        Returns traffic intensity factor between 0.12 (deep night) and 1.0 (peak).
        """
        hour = hour % 24
        # Peak 1: 11.5h, Peak 2: 20.75h
        m1 = math.exp(-0.5 * ((hour - 11.5) / 2.8) ** 2)
        m2 = math.exp(-0.5 * ((hour - 20.75) / 3.2) ** 2)
        base_night = 0.12

        curve = base_night + 0.88 * max(m1, m2 * 0.95)
        return round(curve, 3)

    @classmethod
    def get_current_intensity(cls, timezone_offset_hours: int = 0) -> float:
        now = datetime.datetime.now(datetime.timezone.utc)
        target_hour = (now.hour + timezone_offset_hours) % 24
        return cls.get_hourly_multiplier(target_hour)

    @classmethod
    def get_24h_curve(cls) -> Dict[int, float]:
        """Returns 24-hour baseline curve for UI visualization."""
        return {h: cls.get_hourly_multiplier(h) for h in range(24)}
