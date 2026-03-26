from apps.stories.watermark import _find_text_space, embed_watermark, extract_watermark


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


class TestFindTextSpace:
    """_find_text_space HTML 대응 테스트."""

    def test_plain_text_space(self):
        assert _find_text_space("hello world") == 5

    def test_html_tag_space_skipped(self):
        """HTML 태그 내부의 공백은 무시."""
        html = '<p class="test">hello world</p>'
        idx = _find_text_space(html)
        # 태그 속성 내부 공백(class="test")은 건너뛰고, 텍스트 공백을 찾아야 함
        assert html[idx] == " "
        # 공백 앞의 문자가 텍스트여야 함
        assert html[idx - 1] == "o"  # "hello"의 o

    def test_no_text_space(self):
        """텍스트 공백이 없으면 -1."""
        assert _find_text_space("<p>nospace</p>") == -1

    def test_empty_string(self):
        assert _find_text_space("") == -1

    def test_only_tags(self):
        assert _find_text_space("<br><hr>") == -1

    def test_multiple_tags_then_text_space(self):
        html = '<div><span class="x">first second</span></div>'
        idx = _find_text_space(html)
        assert html[idx] == " "
        # "first second" 사이의 공백이어야 함
        assert html[idx - 1] == "t"

    def test_space_before_tag(self):
        html = "hello <b>world</b>"
        idx = _find_text_space(html)
        assert idx == 5
        assert html[idx] == " "


class TestEmbedWatermarkHtml:
    """HTML 콘텐츠에 워터마크 삽입 테스트."""

    def test_html_content(self):
        html = "<p>Hello world</p>"
        wm_id = "42"
        result = embed_watermark(html, wm_id)
        assert extract_watermark(result) == wm_id
        # 태그 구조는 깨지지 않아야 함
        assert result.startswith("<p>")
        assert result.endswith("</p>")

    def test_no_space_appends_to_end(self):
        text = "nospace"
        wm_id = "42"
        result = embed_watermark(text, wm_id)
        assert extract_watermark(result) == wm_id
        assert result.startswith("nospace")

    def test_html_with_attributes(self):
        html = '<p class="prose">First paragraph with text</p>'
        wm_id = "user:123"
        result = embed_watermark(html, wm_id)
        assert extract_watermark(result) == wm_id
