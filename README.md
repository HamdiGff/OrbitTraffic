# OrbitTraffic 🚀

> **Organic Traffic Intelligence Platform** — Generate realistic, human-like organic traffic using real browsers, AI behavioral simulation, proxy rotation, and fingerprint spoofing.

[![Release](https://img.shields.io/github/v/release/yourusername/OrbitTraffic?style=flat-square&color=6c63ff)](https://github.com/yourusername/OrbitTraffic/releases)
[![Python](https://img.shields.io/badge/python-3.12+-blue?style=flat-square)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Behavioral Engine** | Bezier mouse curves, Gaussian click timing, scroll fatigue model |
| 🕵️ **Fingerprint Spoofing** | Canvas noise, WebGL spoof, Audio context, Navigator overrides |
| 🔌 **Proxy Manager** | Async bulk checker, geolocation, health scoring, smart rotation |
| 🔑 **Keyword Engine** | Search→click flow, long-tail variants, CTR curve modeling |
| 🍪 **Cookie Intelligence** | Cookie aging, referrer chain, localStorage seeding |
| 📊 **Live Dashboard** | Real-time stats, session logs, success rate tracking |
| 🌙 **Dark GUI** | Modern PyQt6 dark-themed multi-tab interface |
| 📦 **GitHub Releases** | Auto-build Windows/Linux executables via GitHub Actions |

## 🚀 Quick Start

### Requirements
- Python 3.12+
- Windows / Linux / macOS

### Installation

```bash
git clone https://github.com/yourusername/OrbitTraffic.git
cd OrbitTraffic
pip install -r requirements.txt
playwright install chromium
python main.py
```

### First Run
1. **Proxies tab** — Import residential proxies, click "Check All"
2. **Keywords tab** — Add target keywords + URLs
3. **Campaigns tab** — Set visit count, concurrency, hit "Start Campaign"
4. **Dashboard** — Watch live stats update in real-time

## 🧠 Innovative Algorithms

### Behavioral AI
- **Bezier Mouse Curves**: Natural mouse paths with overshoot correction and microsaccades
- **Gaussian Click Timing**: Human-realistic 150-600ms reaction time distribution
- **Scroll Fatigue Model**: Speed decreases with page depth, random re-reads
- **Reading Time AI**: Dwell based on content word count estimation

### Fingerprint Spoofing Stack
```
Canvas     → Seeded pixel noise injection (imperceptible)
WebGL      → Real GPU renderer string rotation from device database  
Audio      → Oscillator output noise per session
Navigator  → Platform, concurrency, memory overrides
Screen     → Realistic resolution + DPR matching
Timing     → Performance.now() jitter (anti-timing fingerprint)
Chrome API → Full chrome.runtime mock
Permissions → Realistic permission state responses
```

### Proxy Intelligence
- Geo-matched sessions (IP country → locale, timezone, screen size)
- Health scoring (latency + success rate composite)
- Cooldown periods with auto-recovery
- Multiple rotation strategies: `best_health`, `round_robin`, `least_used`, `random`

## 📂 Project Structure

```
OrbitTraffic/
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── config/              # Settings
├── browser/             # Playwright controller + fingerprint
├── behavior/            # Mouse, scroll, timing AI
├── proxy/               # Checker, pool manager
├── keyword/             # Traffic flow engine
├── gui/                 # PyQt6 dark-themed GUI
│   └── tabs/            # Dashboard, Campaigns, Proxies, Keywords...
└── utils/               # Logger, crypto, updater
```

## ⚠️ Disclaimer

This software is for **legitimate traffic analysis, website testing, and SEO research** only. Users are responsible for complying with all applicable terms of service and local laws. Do not use to violate any platform's ToS or for fraudulent purposes.

## 📄 License

MIT © OrbitTraffic Contributors
