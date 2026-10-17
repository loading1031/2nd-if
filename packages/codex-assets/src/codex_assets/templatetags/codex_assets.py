"""Usage: load codex_assets, then codex_asset asset_id color='파란색'."""

from django import template
from django.templatetags.static import static
from django.utils.html import format_html

from codex_assets import get_asset, nearest_color

register = template.Library()


@register.inclusion_tag("codex_assets/asset.html")
def codex_asset(
    asset_id: str, color: str = "", label: str = "", size: int = 96, palette: str = "", background: bool = False
) -> dict:
    """Render a known bundled asset; invalid color falls back to black."""
    asset = get_asset(asset_id)
    size = max(1, min(int(size), 2048))
    appearance = nearest_color(color, palette or None) if color else None
    foreground = appearance["foreground"] if appearance else "#000000"
    backdrop = appearance["background"] if appearance and background else "transparent"
    url = static("assets/game-icons/" + asset["relative_path"])
    # Only trusted catalog paths and validated/computed colors reach CSS.
    style = format_html(
        "--codex-size:{}px;--codex-color:{};--codex-background:{};--codex-mask:url('{}')",
        size,
        foreground,
        backdrop,
        url,
    )
    return {"asset": asset, "label": label or asset["name"], "style": style, "appearance": appearance, "url": url}
