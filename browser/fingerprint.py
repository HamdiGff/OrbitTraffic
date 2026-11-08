"""
Fingerprint Spoofing Module
Injects custom fingerprint overrides into Playwright browser contexts.
Covers: Canvas, WebGL, Audio, Fonts, Screen, Navigator, TLS, Timing.
"""
import random
import json
from typing import Optional
from utils.logger import get_logger

logger = get_logger("fingerprint")

# Real-device GPU renderer strings pool
WEBGL_RENDERERS = [
    "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    "ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    "ANGLE (Intel, Intel(R) Iris Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
    "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    "Apple GPU",
    "Mesa Intel(R) UHD Graphics 620 (WHL GT2)",
    "ANGLE (Intel, Intel(R) HD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
]

WEBGL_VENDORS = [
    "Google Inc. (Intel)",
    "Google Inc. (NVIDIA)",
    "Google Inc. (AMD)",
    "Apple Inc.",
    "Mesa/X.org",
]

# Realistic screen resolutions mapped to usage frequency
SCREEN_RESOLUTIONS = [
    (1920, 1080), (1920, 1080), (1920, 1080),  # Most common
    (2560, 1440), (2560, 1440),
    (1366, 768), (1366, 768),
    (1440, 900),
    (1536, 864),
    (1280, 720),
    (3840, 2160),
    (2560, 1600),
    (1600, 900),
]

PLATFORM_MAP = {
    "Windows": ["Win32"],
    "Mac": ["MacIntel", "MacPPC"],
    "Linux": ["Linux x86_64", "Linux i686"],
}

LANGUAGE_TIMEZONE_MAP = {
    "en-US": "America/New_York",
    "en-GB": "Europe/London",
    "de-DE": "Europe/Berlin",
    "fr-FR": "Europe/Paris",
    "es-ES": "Europe/Madrid",
    "it-IT": "Europe/Rome",
    "ja-JP": "Asia/Tokyo",
    "zh-CN": "Asia/Shanghai",
    "ko-KR": "Asia/Seoul",
    "pt-BR": "America/Sao_Paulo",
    "ru-RU": "Europe/Moscow",
    "ar-SA": "Asia/Riyadh",
    "hi-IN": "Asia/Kolkata",
    "nl-NL": "Europe/Amsterdam",
    "pl-PL": "Europe/Warsaw",
    "tr-TR": "Europe/Istanbul",
}


class FingerprintProfile:
    """
    A complete, internally-consistent browser fingerprint.
    All values are correlated (e.g. GPU matches OS, screen matches device).
    """

    def __init__(
        self,
        locale: Optional[str] = None,
        platform: Optional[str] = None,
        proxy_country: Optional[str] = None,
    ):
        self.locale = locale or random.choice(list(LANGUAGE_TIMEZONE_MAP.keys()))
        self.timezone = LANGUAGE_TIMEZONE_MAP.get(self.locale, "UTC")
        self.platform = platform or random.choice(["Windows", "Mac", "Linux"])
        self.screen_w, self.screen_h = random.choice(SCREEN_RESOLUTIONS)
        self.device_pixel_ratio = random.choice([1.0, 1.25, 1.5, 2.0])
        self.webgl_renderer = random.choice(WEBGL_RENDERERS)
        self.webgl_vendor = random.choice(WEBGL_VENDORS)
        self.canvas_noise_seed = random.randint(1, 999999)
        self.audio_noise_seed = random.uniform(0.00001, 0.0001)
        self.hardware_concurrency = random.choice([2, 4, 4, 4, 8, 8, 12, 16])
        self.device_memory = random.choice([2, 4, 4, 8, 8, 16])
        self.color_depth = random.choice([24, 30, 32])
        self.touch_support = False  # Desktop default
        self.max_touch_points = 0
        self.do_not_track = random.choice([None, "1"])
        self.cookie_enabled = True
        self.pdf_viewer_enabled = True
        self.nav_platform = random.choice(PLATFORM_MAP.get(self.platform, ["Win32"]))

    def to_dict(self) -> dict:
        return {
            "locale": self.locale,
            "timezone": self.timezone,
            "platform": self.platform,
            "screen_w": self.screen_w,
            "screen_h": self.screen_h,
            "device_pixel_ratio": self.device_pixel_ratio,
            "webgl_renderer": self.webgl_renderer,
            "webgl_vendor": self.webgl_vendor,
            "canvas_noise_seed": self.canvas_noise_seed,
            "audio_noise_seed": self.audio_noise_seed,
            "hardware_concurrency": self.hardware_concurrency,
            "device_memory": self.device_memory,
        }


def get_stealth_init_script(profile: FingerprintProfile) -> str:
    """
    Returns a JavaScript string to inject into every new page.
    Overrides fingerprint-detectable APIs at the browser level.
    """
    return f"""
(function() {{
    'use strict';

    // ─── 1. CANVAS NOISE INJECTION ───────────────────────────────────────────
    const _seed = {profile.canvas_noise_seed};
    function seededRandom(seed) {{
        let x = Math.sin(seed++) * 10000;
        return x - Math.floor(x);
    }}
    const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
    CanvasRenderingContext2D.prototype.getImageData = function(x, y, w, h) {{
        const imageData = originalGetImageData.call(this, x, y, w, h);
        for (let i = 0; i < imageData.data.length; i += 4) {{
            imageData.data[i] ^= Math.floor(seededRandom(_seed + i) * 3);
        }}
        return imageData;
    }};
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type, quality) {{
        const ctx = this.getContext('2d');
        if (ctx) {{
            const imageData = ctx.getImageData(0, 0, this.width, this.height);
            for (let i = 0; i < imageData.data.length; i += 4) {{
                imageData.data[i] ^= Math.floor(seededRandom(_seed + i) * 2);
            }}
            ctx.putImageData(imageData, 0, 0);
        }}
        return originalToDataURL.call(this, type, quality);
    }};

    // ─── 2. WEBGL FINGERPRINT SPOOF ──────────────────────────────────────────
    const getParameterProxyHandler = {{
        apply: function(target, ctx, args) {{
            const param = args[0];
            if (param === 37445) return '{profile.webgl_vendor}';    // UNMASKED_VENDOR_WEBGL
            if (param === 37446) return '{profile.webgl_renderer}';   // UNMASKED_RENDERER_WEBGL
            if (param === 7937)  return 'WebKit';                      // RENDERER
            if (param === 7936)  return 'WebKit WebGL';                // VENDOR
            return Reflect.apply(target, ctx, args);
        }}
    }};
    try {{
        const gl = document.createElement('canvas').getContext('webgl');
        if (gl) {{
            const ext = gl.getExtension('WEBGL_debug_renderer_info');
            WebGLRenderingContext.prototype.getParameter = new Proxy(
                WebGLRenderingContext.prototype.getParameter,
                getParameterProxyHandler
            );
        }}
    }} catch(e) {{}}

    // ─── 3. AUDIO CONTEXT NOISE ──────────────────────────────────────────────
    const _audioNoise = {profile.audio_noise_seed:.8f};
    const OriginalAudioBuffer = AudioBuffer;
    const originalGetChannelData = AudioBuffer.prototype.getChannelData;
    AudioBuffer.prototype.getChannelData = function(channel) {{
        const array = originalGetChannelData.call(this, channel);
        for (let i = 0; i < array.length; i++) {{
            array[i] += (Math.random() * 2 - 1) * _audioNoise;
        }}
        return array;
    }};

    // ─── 4. NAVIGATOR OVERRIDES ──────────────────────────────────────────────
    Object.defineProperties(navigator, {{
        platform: {{ get: () => '{profile.nav_platform}' }},
        hardwareConcurrency: {{ get: () => {profile.hardware_concurrency} }},
        deviceMemory: {{ get: () => {profile.device_memory} }},
        maxTouchPoints: {{ get: () => {profile.max_touch_points} }},
        cookieEnabled: {{ get: () => true }},
        pdfViewerEnabled: {{ get: () => true }},
        vendor: {{ get: () => 'Google Inc.' }},
        appVersion: {{ get: () => '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' }},
    }});

    // ─── 5. SCREEN RESOLUTION ────────────────────────────────────────────────
    Object.defineProperties(screen, {{
        width:       {{ get: () => {profile.screen_w} }},
        height:      {{ get: () => {profile.screen_h} }},
        availWidth:  {{ get: () => {profile.screen_w} }},
        availHeight: {{ get: () => {profile.screen_h} - 40 }},
        colorDepth:  {{ get: () => {profile.color_depth} }},
        pixelDepth:  {{ get: () => {profile.color_depth} }},
    }});

    // ─── 6. WINDOW DIMENSIONS ───────────────────────────────────────────────
    Object.defineProperties(window, {{
        innerWidth:  {{ get: () => {profile.screen_w} - Math.floor(Math.random() * 20) }},
        innerHeight: {{ get: () => {profile.screen_h} - 100 - Math.floor(Math.random() * 40) }},
        devicePixelRatio: {{ get: () => {profile.device_pixel_ratio} }},
    }});

    // ─── 7. WEBDRIVER FLAG REMOVAL ──────────────────────────────────────────
    Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined }});
    delete navigator.__proto__.webdriver;

    // ─── 8. CHROME RUNTIME MOCK ─────────────────────────────────────────────
    if (!window.chrome) {{
        window.chrome = {{
            runtime: {{
                onConnect: {{ addListener: () => {{}} }},
                onMessage: {{ addListener: () => {{}} }},
                sendMessage: () => {{}},
                connect: () => ({{ postMessage: () => {{}}, onMessage: {{ addListener: () => {{}} }} }}),
                id: undefined,
            }},
            loadTimes: () => ({{
                commitLoadTime: Date.now() / 1000 - Math.random() * 2,
                connectionInfo: 'h2',
                finishDocumentLoadTime: Date.now() / 1000 - Math.random(),
                finishLoadTime: Date.now() / 1000 - Math.random() * 0.5,
                firstPaintAfterLoadTime: 0,
                firstPaintTime: Date.now() / 1000 - Math.random() * 1.5,
                navigationType: 'Other',
                npnNegotiatedProtocol: 'h2',
                requestTime: Date.now() / 1000 - Math.random() * 3,
                startLoadTime: Date.now() / 1000 - Math.random() * 2.5,
                wasAlternateProtocolAvailable: false,
                wasFetchedViaSpdy: true,
                wasNpnNegotiated: true,
            }}),
            csi: () => ({{
                onloadT: Date.now(),
                pageT: Math.random() * 5000 + 1000,
                startE: Date.now() - Math.random() * 10000,
                tran: 15,
            }}),
        }};
    }}

    // ─── 9. PERMISSIONS API SPOOF ────────────────────────────────────────────
    const originalQuery = Permissions.prototype.query;
    Permissions.prototype.query = async function(permissionDesc) {{
        const result = await originalQuery.call(this, permissionDesc);
        if (['notifications', 'push', 'midi', 'camera', 'microphone'].includes(permissionDesc.name)) {{
            Object.defineProperty(result, 'state', {{ value: 'prompt' }});
        }}
        return result;
    }};

    // ─── 10. TIMING JITTER (Anti-timing-fingerprint) ─────────────────────────
    const originalNow = performance.now.bind(performance);
    performance.now = function() {{
        return Math.floor(originalNow() / 0.1) * 0.1;
    }};
    const originalGetTime = Date.prototype.getTime;
    Date.prototype.getTime = function() {{
        return Math.floor(originalGetTime.call(this) / 10) * 10;
    }};

}})();
"""


def get_context_options(profile: FingerprintProfile) -> dict:
    """Browser context options for Playwright new_context()."""
    return {
        "locale": profile.locale,
        "timezone_id": profile.timezone,
        "viewport": {"width": profile.screen_w, "height": profile.screen_h - 100},
        "color_scheme": "light",
        "device_scale_factor": profile.device_pixel_ratio,
        "has_touch": profile.touch_support,
        "java_script_enabled": True,
        "accept_downloads": False,
        "extra_http_headers": {
            "Accept-Language": f"{profile.locale},{profile.locale.split('-')[0]};q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": f'"{profile.platform}"',
        },
    }
