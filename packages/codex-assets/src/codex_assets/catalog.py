"""Read-only bundled catalog. Stable author/slug IDs are independent of categories."""

import json
from functools import lru_cache
from importlib.resources import files


def read_data(name: str) -> dict:
    return json.loads(files("codex_assets").joinpath("static", "assets", "game-icons", name).read_text())


@lru_cache(maxsize=1)
def _assets() -> dict[str, dict]:
    return {asset["id"]: asset for asset in read_data("catalog.json")["icons"]}


def get_asset(asset_id: str) -> dict:
    """Return an independent copy; unknown IDs raise KeyError, never become paths."""
    import copy

    return copy.deepcopy(_assets()[asset_id])


def list_assets(*, topic: str | None = None, query: str = "") -> list[dict]:
    query = query.casefold().strip()
    return [
        get_asset(asset["id"])
        for asset in _assets().values()
        if (not topic or topic in asset["topics"])
        and (not query or query in " ".join([asset["id"], asset["name"], *asset["tags"]]).casefold())
    ]
