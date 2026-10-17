"""Pure Python palette mapping, matching the gallery's weighted OKLab metric."""

import json
import math
import re
from functools import lru_cache
from importlib.resources import files

from .catalog import read_data


@lru_cache(maxsize=1)
def _names() -> dict[str, str]:
    return json.loads(files("codex_assets").joinpath("color-names.json").read_text())


def normalize_color(value: str) -> str | None:
    value = value.strip().lower()
    if value in _names():
        return _names()[value]
    if re.fullmatch(r"#?[0-9a-f]{6}", value):
        return "#" + value.lstrip("#").upper()
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        return "#" + "".join(c * 2 for c in value[1:]).upper()
    return None


@lru_cache(maxsize=1)
def _palettes() -> list[dict]:
    return read_data("palettes.json")["palettes"]


def _oklab(value: str) -> tuple[float, float, float]:
    rgb = [int(value[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
    long = math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return (
        0.2104542553 * long + 0.793617785 * m - 0.0040720468 * s,
        1.9779984951 * long - 2.428592205 * m + 0.4505937099 * s,
        0.0259040371 * long + 0.7827717662 * m - 0.808675766 * s,
    )


def nearest_color(value: str, palette_id: str | None = None) -> dict | None:
    """Return requestedColor/paletteId/foreground/background/distance or None."""
    value = normalize_color(value)
    if not value:
        return None
    target = _oklab(value)
    best = None
    for palette in _palettes():
        if palette_id and palette["id"] != palette_id:
            continue
        for foreground in palette["colors"]:
            lab = _oklab(foreground)
            dc = math.hypot(*target[1:]) - math.hypot(*lab[1:])
            dh2 = max(0, (target[1] - lab[1]) ** 2 + (target[2] - lab[2]) ** 2 - dc**2)
            distance = math.sqrt(0.25 * (target[0] - lab[0]) ** 2 + dc**2 + 9 * dh2)
            if best is None or distance < best["distance"]:
                best = dict(
                    requestedColor=value,
                    paletteId=palette["id"],
                    foreground=foreground,
                    background=palette["background"],
                    distance=distance,
                )
    return best
