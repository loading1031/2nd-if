"""Polygon 트랜잭션 검증 유틸리티."""

from decimal import Decimal

import httpx
from django.conf import settings

TOKEN_DECIMALS = 6  # USDC, USDT 모두 6 decimals


def _get_token_addresses():
    return {
        "USDC": settings.POLYGON_USDC_ADDRESS,
        "USDT": settings.POLYGON_USDT_ADDRESS,
    }


# ERC-20 transfer(address,uint256) 함수 시그니처
TRANSFER_SELECTOR = "0xa9059cbb"


async def _rpc_call(method: str, params: list) -> dict:
    """Polygon JSON-RPC 호출."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            settings.POLYGON_RPC_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params,
            },
        )
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise ValueError(f"RPC error: {data['error']}")
        return data.get("result")


def _parse_transfer_input(input_data: str) -> tuple[str, int] | None:
    """ERC-20 transfer input data를 파싱하여 (recipient, amount) 반환.

    input data 구조:
      0xa9059cbb
      + to_address (32bytes, 좌측 0 패딩)
      + amount (32bytes)
    """
    if not input_data or len(input_data) < 138:
        return None

    selector = input_data[:10]
    if selector.lower() != TRANSFER_SELECTOR:
        return None

    # to_address: 10~74 (32bytes), 마지막 20bytes가 실제 주소
    recipient_raw = input_data[10:74]
    recipient = "0x" + recipient_raw[-40:]

    # amount: 74~138 (32bytes)
    amount_hex = input_data[74:138]
    amount = int(amount_hex, 16)

    return recipient, amount


async def verify_transaction(
    tx_hash: str,
    expected_to: str,
    expected_token: str,
    expected_amount: Decimal,
) -> dict:
    """트랜잭션 해시로 결제를 검증.

    Returns:
        {"valid": True/False, "error": "에러 메시지" or None}

    검증 항목:
    1. 트랜잭션이 존재하고 성공했는지
    2. to 주소가 토큰 컨트랙트 주소인지 (ERC-20 transfer)
    3. input data에서 recipient과 amount 디코딩
    4. recipient == expected_to (작가 지갑)
    5. amount >= expected_amount
    """
    token_addresses = _get_token_addresses()
    if expected_token not in token_addresses:
        return {"valid": False, "error": f"지원하지 않는 토큰: {expected_token}"}

    token_contract = token_addresses[expected_token]

    # 1. 트랜잭션 receipt 조회 (성공 여부 확인)
    try:
        receipt = await _rpc_call("eth_getTransactionReceipt", [tx_hash])
    except (httpx.HTTPError, ValueError) as e:
        return {"valid": False, "error": f"RPC 호출 실패: {e}"}

    if receipt is None:
        return {"valid": False, "error": "트랜잭션을 찾을 수 없습니다."}

    # status: 0x1 = 성공, 0x0 = 실패
    status = receipt.get("status")
    if status != "0x1":
        return {"valid": False, "error": "트랜잭션이 실패한 상태입니다."}

    # 2. 트랜잭션 상세 조회 (input data 확인)
    try:
        tx = await _rpc_call("eth_getTransactionByHash", [tx_hash])
    except (httpx.HTTPError, ValueError) as e:
        return {"valid": False, "error": f"트랜잭션 조회 실패: {e}"}

    if tx is None:
        return {"valid": False, "error": "트랜잭션 데이터를 찾을 수 없습니다."}

    # to 주소가 토큰 컨트랙트인지 확인
    tx_to = tx.get("to", "")
    if tx_to.lower() != token_contract.lower():
        return {
            "valid": False,
            "error": f"토큰 컨트랙트가 일치하지 않습니다. (expected: {expected_token})",
        }

    # 3. input data 파싱
    input_data = tx.get("input", "")
    parsed = _parse_transfer_input(input_data)
    if parsed is None:
        return {"valid": False, "error": "ERC-20 transfer 호출이 아닙니다."}

    recipient, raw_amount = parsed

    # 4. recipient 검증 (작가 지갑 주소)
    if recipient.lower() != expected_to.lower():
        return {
            "valid": False,
            "error": "수신자 주소가 작가 지갑과 일치하지 않습니다.",
        }

    # 5. amount 검증
    # raw_amount는 토큰의 최소 단위 (6 decimals)
    actual_amount = Decimal(raw_amount) / Decimal(10**TOKEN_DECIMALS)
    if actual_amount < expected_amount:
        return {
            "valid": False,
            "error": f"결제 금액이 부족합니다. (필요: {expected_amount}, 실제: {actual_amount})",
        }

    return {"valid": True, "error": None}
