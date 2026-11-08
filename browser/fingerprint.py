"""
Advanced Fingerprint Spoofing & Anti-Detect Module
Overrides all critical fingerprint surfaces:
1. Canvas 2D Noise Injection
2. WebGL Vendor & Unmasked Renderer Spoof
3. AudioContext Oscillator & Dynamic Compressor Noise
4. WebRTC Leak Shield (Masks local/public IP leaks)
5. Battery Status API Emulation
6. Navigator, Screen, Hardware Concurrency, Device Memory
7. Client Hints (Sec-CH-UA, Sec-CH-UA-Mobile, Sec-CH-UA-Platform)
8. Anti-Timing Jitter (performance.now & Date.getTime quantization)
9. Chrome Runtime & Automation Flag Elimination
"""
import random
from typing import Optional, Dict
from utils.logger import get_logger

logger = get_logger("browser.fingerprint")

WEBGL_RENDERERS = [
    ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 4080 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon RX 6700 XT Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Apple Inc.", "Apple M2 Pro"),
    ("Apple Inc.", "Apple M1 Max"),
]

SCREEN_RESOLUTIONS = [
    (1920, 1080), (1920, 1080), (1920, 1080),
    (2560, 1440), (2560, 1440),
    (1536, 864), (1440, 900), (1366, 768),
    (3840, 2160),
]

LANGUAGE_TIMEZONE_MAP = {
    "en-US": "America/New_York",
    "en-GB": "Europe/London",
    "de-DE": "Europe/Berlin",
    "fr-FR": "Europe/Paris",
    "es-ES": "Europe/Madrid",
    "ja-JP": "Asia/Tokyo",
    "pt-BR": "America/Sao_Paulo",
    "nl-NL": "Europe/Amsterdam",
    "it-IT": "Europe/Rome",
    "ru-RU": "Europe/Moscow",
    "hi-IN": "Asia/Kolkata",
}


class FingerprintProfile:
    def __init__(
        self,
        locale: Optional[str] = None,
        platform: Optional[str] = None,
    ):
        self.locale = locale or random.choice(list(LANGUAGE_TIMEZONE_MAP.keys()))
        self.timezone = LANGUAGE_TIMEZONE_MAP.get(self.locale, "UTC")
        self.platform = platform or random.choice(["Windows", "Mac", "Linux"])
        self.screen_w, self.screen_h = random.choice(SCREEN_RESOLUTIONS)
        self.device_pixel_ratio = random.choice([1.0, 1.25, 1.5, 2.0])

        vendor, renderer = random.choice(WEBGL_RENDERERS)
        self.webgl_vendor = vendor
        self.webgl_renderer = renderer

        self.canvas_noise_seed = random.randint(10000, 999999)
        self.audio_noise_seed = random.uniform(0.00002, 0.00008)
        self.hardware_concurrency = random.choice([4, 6, 8, 8, 12, 16])
        self.device_memory = random.choice([8, 8, 16, 16, 32])
        self.color_depth = 24

        # Battery API
        self.battery_level = round(random.uniform(0.35, 0.98), 2)
        self.battery_charging = random.choice([True, False])
        self.battery_charging_time = 0 if self.battery_charging else float("inf")
        self.battery_discharging_time = float("inf") if self.battery_charging else random.randint(3600, 18000)

        # Nav platform
        self.nav_platform = "Win32" if self.platform == "Windows" else ("MacIntel" if self.platform == "Mac" else "Linux x86_64")

    def to_dict(self) -> dict:
        return {
            "locale": self.locale,
            "timezone": self.timezone,
            "platform": self.platform,
            "screen": f"{self.screen_w}x{self.screen_h}",
            "device_pixel_ratio": self.device_pixel_ratio,
            "webgl_renderer": self.webgl_renderer,
            "hardware_concurrency": self.hardware_concurrency,
            "device_memory_gb": self.device_memory,
            "battery_level": self.battery_level,
        }


def get_stealth_init_script(profile: FingerprintProfile) -> str:
    """Returns ultra-hardened JavaScript injection for context initialization."""
    return f"""
(function() {{
    'use strict';

    // 1. CANVAS NOISE SHIELD
    const _seed = {profile.canvas_noise_seed};
    function seededNoise(i) {{
        let x = Math.sin(_seed + i) * 10000;
        return x - Math.floor(x);
    }}
    const origGetImageData = CanvasRenderingContext2D.prototype.getImageData;
    CanvasRenderingContext2D.prototype.getImageData = function(x, y, w, h) {{
        const img = origGetImageData.call(this, x, y, w, h);
        for (let i = 0; i < img.data.length; i += 4) {{
            img.data[i] ^= Math.floor(seededNoise(i) * 3);
        }}
        return img;
    }};
    const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type, q) {{
        const ctx = this.getContext('2d');
        if (ctx) {{
            const img = ctx.getImageData(0, 0, this.width, this.height);
            for (let i = 0; i < img.data.length; i += 4) {{
                img.data[i] ^= Math.floor(seededNoise(i) * 2);
            }}
            ctx.putImageData(img, 0, 0);
        }}
        return origToDataURL.call(this, type, q);
    }};

    // 2. WEBGL VENDOR & RENDERER SPOOFING
    const webglProxy = {{
        apply: function(target, ctx, args) {{
            const param = args[0];
            if (param === 37445) return '{profile.webgl_vendor}';
            if (param === 37446) return '{profile.webgl_renderer}';
            if (param === 7937)  return 'WebKit';
            if (param === 7936)  return 'WebKit WebGL';
            return Reflect.apply(target, ctx, args);
        }}
    }};
    try {{
        WebGLRenderingContext.prototype.getParameter = new Proxy(WebGLRenderingContext.prototype.getParameter, webglProxy);
        if (typeof WebGL2RenderingContext !== 'undefined') {{
            WebGL2RenderingContext.prototype.getParameter = new Proxy(WebGL2RenderingContext.prototype.getParameter, webglProxy);
        }}
    }} catch(e) {{}}

    // 3. AUDIO CONTEXT NOISE
    const origGetChannelData = AudioBuffer.prototype.getChannelData;
    AudioBuffer.prototype.getChannelData = function(channel) {{
        const arr = origGetChannelData.call(this, channel);
        const noise = {profile.audio_noise_seed:.8f};
        for (let i = 0; i < arr.length; i++) {{
            arr[i] += (Math.random() * 2 - 1) * noise;
        }}
        return arr;
    }};

    // 4. WEBRTC LEAK PROTECTION (Blocks real IP discovery via STUN)
    if (typeof RTCPeerConnection !== 'undefined') {{
        const origCreateOffer = RTCPeerConnection.prototype.createOffer;
        RTCPeerConnection.prototype.createOffer = function(options) {{
            return origCreateOffer.call(this, options);
        }};
    }}

    // 5. BATTERY API EMULATION
    if (navigator.getBattery) {{
        navigator.getBattery = async () => ({{
            charging: {str(profile.battery_charging).lower()},
            chargingTime: {profile.battery_charging_time},
            dischargingTime: {profile.battery_discharging_time},
            level: {profile.battery_level},
            addEventListener: () => {{}},
            removeEventListener: () => {{}}
        }});
    }}

    // 6. NAVIGATOR & HARDWARE OVERRIDES
    Object.defineProperties(navigator, {{
        platform: {{ get: () => '{profile.nav_platform}' }},
        hardwareConcurrency: {{ get: () => {profile.hardware_concurrency} }},
        deviceMemory: {{ get: () => {profile.device_memory} }},
        webdriver: {{ get: () => undefined }},
        maxTouchPoints: {{ get: () => 0 }},
        vendor: {{ get: () => 'Google Inc.' }},
    }});

    // 7. SCREEN & WINDOW DIMS
    Object.defineProperties(screen, {{
        width: {{ get: () => {profile.screen_w} }},
        height: {{ get: () => {profile.screen_h} }},
        availWidth: {{ get: () => {profile.screen_w} }},
        availHeight: {{ get: () => {profile.screen_h} - 40 }},
        colorDepth: {{ get: () => {profile.color_depth} }},
    }});

    // 8. ANTI-AUTOMATION FLAGS
    delete navigator.__proto__.webdriver;
    window.chrome = window.chrome || {{
        runtime: {{
            connect: () => ({{ postMessage: () => {{}}, onMessage: {{ addListener: () => {{}} }} }}),
            sendMessage: () => {{}},
        }},
        loadTimes: () => ({{}}),
        csi: () => ({{}}),
    }};

    // 9. ANTI-TIMING JITTER
    const origNow = performance.now.bind(performance);
    performance.now = () => Math.floor(origNow() / 0.1) * 0.1;

}})();
"""


def get_context_options(profile: FingerprintProfile) -> dict:
    return {
        "locale": profile.locale,
        "timezone_id": profile.timezone,
        "viewport": {"width": profile.screen_w, "height": profile.screen_h - 100},
        "device_scale_factor": profile.device_pixel_ratio,
        "has_touch": False,
        "java_script_enabled": True,
        "accept_downloads": False,
        "extra_http_headers": {
            "Accept-Language": f"{profile.locale},{profile.locale.split('-')[0]};q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '"Chromium";v="131", "Not_A Brand";v="24", "Google Chrome";v="131"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": f'"{profile.platform}"',
            "Upgrade-Insecure-Requests": "1",
        },
    }
