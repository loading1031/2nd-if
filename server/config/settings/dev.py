"""
Django settings for project - Development configuration.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# WhiteNoise — uvicorn(ASGI)에서도 static 파일 서빙
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Development-specific apps
INSTALLED_APPS += [
    "django_extensions",
    "pattern_library",
]

# CORS for development
CORS_ALLOW_ALL_ORIGINS = True

# 분기 제한 완화 (개발용)
BRANCH_EPISODE_GAP = 0

# Polygon Amoy 테스트넷 (개발용)
POLYGON_CHAIN_ID = "0x13882"
POLYGON_CHAIN_NAME = "Polygon Amoy Testnet"
POLYGON_RPC_URL = "https://rpc-amoy.polygon.technology"
POLYGON_EXPLORER_URL = "https://amoy.polygonscan.com"
POLYGON_CURRENCY_SYMBOL = "POL"
POLYGON_USDC_ADDRESS = "0x41E94Eb019C0762f9Bfcf9Fb1E58725BfB0e7582"  # Amoy USDC
POLYGON_USDT_ADDRESS = "0x1616d425Cd540B256475cBfb604586C8598eC0FB"  # Amoy USDT

# Pattern library iframe rendering
X_FRAME_OPTIONS = "SAMEORIGIN"

# Pattern library loader_tags (dev only)
TEMPLATES[0]["OPTIONS"]["builtins"] = [
    "pattern_library.loader_tags",
]

# Pattern Library Configuration
PATTERN_LIBRARY = {
    "SECTIONS": (
        ("components", ["patterns/components"]),
        ("pages", ["patterns/pages"]),
    ),
    "TEMPLATE_SUFFIX": ".html",
    "PATTERN_BASE_TEMPLATE_NAME": "patterns/base.html",
    "BASE_TEMPLATE_NAMES": ["patterns/base_page.html"],
}
