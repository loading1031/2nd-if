"""템플릿 컨텍스트 프로세서."""

import json

from django.conf import settings


def polygon_config(request):
    """Polygon 네트워크 설정을 템플릿에 전달."""
    config = {
        "chainId": settings.POLYGON_CHAIN_ID,
        "chainName": settings.POLYGON_CHAIN_NAME,
        "rpcUrl": settings.POLYGON_RPC_URL,
        "explorerUrl": settings.POLYGON_EXPLORER_URL,
        "currencySymbol": settings.POLYGON_CURRENCY_SYMBOL,
        "tokens": {
            "USDC": {"address": settings.POLYGON_USDC_ADDRESS, "decimals": 6},
            "USDT": {"address": settings.POLYGON_USDT_ADDRESS, "decimals": 6},
        },
    }
    return {"polygon_config_json": json.dumps(config)}
