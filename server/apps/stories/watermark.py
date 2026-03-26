"""Zero-width 유니코드 워터마크.

텍스트에 보이지 않는 유니코드 문자로 식별자를 인코딩한다.
- ZWS (U+200B) = 비트 0
- ZWNJ (U+200C) = 비트 1
- ZWJ (U+200D) = 구분자 (시작/끝 마커)
"""

ZWS = "\u200b"  # 0
ZWNJ = "\u200c"  # 1
ZWJ = "\u200d"  # 구분자
MARKER = ZWJ + ZWS + ZWJ  # 워터마크 시작/끝 마커


def _encode(identifier: str) -> str:
    binary = "".join(format(b, "08b") for b in identifier.encode("utf-8"))
    return MARKER + "".join(ZWS if bit == "0" else ZWNJ for bit in binary) + MARKER


def _decode(zwc_string: str) -> str | None:
    binary = ""
    for char in zwc_string:
        if char == ZWS:
            binary += "0"
        elif char == ZWNJ:
            binary += "1"

    if not binary or len(binary) % 8 != 0:
        return None

    try:
        return bytes(int(binary[i : i + 8], 2) for i in range(0, len(binary), 8)).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None


def _find_text_space(html: str) -> int:
    """HTML 태그 밖의 첫 번째 공백 위치를 찾는다."""
    inside_tag = False
    for i, ch in enumerate(html):
        if ch == "<":
            inside_tag = True
        elif ch == ">":
            inside_tag = False
        elif ch == " " and not inside_tag:
            return i
    return -1


def embed_watermark(text: str, identifier: str) -> str:
    """텍스트의 첫 번째 텍스트 공백 뒤에 zero-width 워터마크 삽입.
    HTML 태그 내부의 공백은 건너뛴다."""
    if not text:
        return ""

    encoded = _encode(identifier)
    space_idx = _find_text_space(text)
    if space_idx == -1:
        return text + encoded
    return text[: space_idx + 1] + encoded + text[space_idx + 1 :]


def extract_watermark(text: str) -> str | None:
    """텍스트에서 워터마크 추출. 없거나 손상되면 None."""
    start = text.find(MARKER)
    if start == -1:
        return None

    after_start = start + len(MARKER)
    end = text.find(MARKER, after_start)
    if end == -1:
        return None

    return _decode(text[after_start:end])
