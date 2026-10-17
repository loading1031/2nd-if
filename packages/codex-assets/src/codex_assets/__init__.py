"""Reusable SVG assets for Django; no project settings or database required."""

from .catalog import get_asset, list_assets
from .colors import nearest_color, normalize_color

__all__ = ["get_asset", "list_assets", "nearest_color", "normalize_color"]
