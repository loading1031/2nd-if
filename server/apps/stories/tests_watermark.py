from apps.stories.watermark import embed_watermark, extract_watermark


class TestWatermark:
    def test_embed_and_extract_user_id(self):
        """시나리오 1: user.id로 워터마크 삽입 → 추출 시 동일 ID."""
        text = "옛날 옛적에 한 소년이 있었습니다."
        wm_id = "42"
        watermarked = embed_watermark(text, wm_id)
        assert watermarked != text  # 워터마크가 삽입됨
        assert extract_watermark(watermarked) == wm_id

    def test_embed_and_extract_session_key(self):
        """시나리오 2: 세션 키로 워터마크."""
        text = "어두운 숲속을 걸어가고 있었다."
        wm_id = "anon:abc123def456"
        watermarked = embed_watermark(text, wm_id)
        assert extract_watermark(watermarked) == wm_id

    def test_empty_text(self):
        """시나리오 3: 빈 텍스트."""
        assert embed_watermark("", "42") == ""

    def test_special_characters(self):
        """시나리오 4: 특수문자/이모지 포함."""
        text = "안녕하세요! 🎉 특수문자 테스트 <b>bold</b>"
        wm_id = "99"
        watermarked = embed_watermark(text, wm_id)
        assert extract_watermark(watermarked) == wm_id

    def test_long_identifier(self):
        """시나리오 5: 매우 긴 식별자."""
        text = "테스트 텍스트입니다."
        wm_id = "anon:a1b2c3d4e5f6g7h8i9j0k1l2m3n4"
        watermarked = embed_watermark(text, wm_id)
        assert extract_watermark(watermarked) == wm_id

    def test_extract_no_watermark(self):
        """시나리오 6: 워터마크 없는 텍스트."""
        assert extract_watermark("일반 텍스트입니다.") is None

    def test_extract_damaged_watermark(self):
        """시나리오 7: 손상된 워터마크."""
        text = "텍스트\u200b\u200c\u200b"  # 불완전한 워터마크
        assert extract_watermark(text) is None

    def test_visible_text_unchanged(self):
        """워터마크 삽입 후 보이는 텍스트는 동일."""
        text = "보이는 텍스트는 변하지 않습니다."
        wm_id = "42"
        watermarked = embed_watermark(text, wm_id)
        # zero-width 문자 제거 후 비교
        visible = watermarked.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")
        assert visible == text
