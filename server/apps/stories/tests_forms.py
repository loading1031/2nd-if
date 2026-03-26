"""폼 검증 및 HTML 새니타이징 테스트."""

from django.contrib.auth import get_user_model

from apps.stories.forms import BranchCreateForm, EpisodeCreateForm, WorkCreateForm, _clean_html_content
from apps.stories.models import Work

User = get_user_model()


class TestCleanHtmlContent:
    """_clean_html_content 새니타이징 테스트."""

    def test_allows_safe_tags(self):
        html = "<p>Hello <strong>world</strong></p>"
        assert _clean_html_content(html) == html

    def test_strips_script_tag(self):
        html = '<p>Hello</p><script>alert("xss")</script>'
        result = _clean_html_content(html)
        assert "<script>" not in result
        assert "<p>Hello</p>" in result

    def test_strips_onclick(self):
        html = '<p onclick="alert(1)">Click me</p>'
        result = _clean_html_content(html)
        assert "onclick" not in result

    def test_allows_img_src_alt(self):
        html = '<img src="http://example.com/img.jpg" alt="photo">'
        result = _clean_html_content(html)
        assert "src=" in result
        assert "alt=" in result

    def test_strips_img_onerror(self):
        html = '<img src="x" onerror="alert(1)">'
        result = _clean_html_content(html)
        assert "onerror" not in result

    def test_allows_heading_tags(self):
        html = "<h2>Title</h2><h3>Subtitle</h3>"
        assert _clean_html_content(html) == html

    def test_strips_iframe(self):
        html = '<iframe src="http://evil.com"></iframe><p>text</p>'
        result = _clean_html_content(html)
        assert "<iframe" not in result
        assert "<p>text</p>" in result

    def test_empty_string(self):
        assert _clean_html_content("") == ""

    def test_none_returns_none(self):
        assert _clean_html_content(None) is None

    def test_allows_list_tags(self):
        html = "<ul><li>one</li><li>two</li></ul>"
        assert _clean_html_content(html) == html

    def test_allows_br_hr(self):
        html = "<p>line1<br>line2</p><hr>"
        result = _clean_html_content(html)
        assert "<br>" in result
        assert "<hr>" in result


class TestWorkCreateForm:
    """WorkCreateForm 테스트."""

    def test_valid_with_all_fields(self):
        form = WorkCreateForm(
            data={
                "title": "Test Work",
                "description": "A test work",
                "license": "free",
                "font": "serif",
            }
        )
        assert form.is_valid()

    def test_valid_without_font(self):
        """font는 선택 필드."""
        form = WorkCreateForm(
            data={
                "title": "Test Work",
                "description": "A test",
                "license": "free",
            }
        )
        assert form.is_valid()

    def test_invalid_without_title(self):
        form = WorkCreateForm(
            data={
                "title": "",
                "license": "free",
            }
        )
        assert not form.is_valid()
        assert "title" in form.errors

    def test_font_choices(self):
        """모든 Font 선택지가 유효한지 확인."""
        for font_value, _ in Work.Font.choices:
            form = WorkCreateForm(
                data={
                    "title": "Test",
                    "license": "free",
                    "font": font_value,
                }
            )
            assert form.is_valid(), f"Font '{font_value}' should be valid"


class TestEpisodeCreateForm:
    """EpisodeCreateForm 테스트."""

    def test_content_sanitized(self):
        form = EpisodeCreateForm(
            data={
                "title": "Episode 1",
                "content": "<p>Good</p><script>bad()</script>",
                "is_paid": False,
            }
        )
        assert form.is_valid()
        assert "<script>" not in form.cleaned_data["content"]
        assert "<p>Good</p>" in form.cleaned_data["content"]

    def test_valid_paid_episode(self):
        form = EpisodeCreateForm(
            data={
                "title": "Paid Episode",
                "content": "<p>Content</p>",
                "is_paid": True,
                "price": "0.50",
            }
        )
        assert form.is_valid()


class TestBranchCreateForm:
    """BranchCreateForm 테스트."""

    def test_direction_too_short(self):
        form = BranchCreateForm(
            data={
                "branch_direction": "Hi",
                "title": "Branch Episode",
                "content": "<p>Content</p>",
                "is_paid": False,
            }
        )
        assert not form.is_valid()
        assert "branch_direction" in form.errors

    def test_direction_exactly_5_chars(self):
        form = BranchCreateForm(
            data={
                "branch_direction": "12345",
                "title": "Branch Episode",
                "content": "<p>Content</p>",
                "is_paid": False,
            }
        )
        assert form.is_valid()

    def test_direction_valid(self):
        form = BranchCreateForm(
            data={
                "branch_direction": "The hero goes to the dark forest",
                "title": "Branch",
                "content": "<p>Adventure</p>",
                "is_paid": False,
            }
        )
        assert form.is_valid()

    def test_content_sanitized(self):
        form = BranchCreateForm(
            data={
                "branch_direction": "Different direction taken",
                "title": "Branch",
                "content": "<p>Good</p><script>evil()</script>",
                "is_paid": False,
            }
        )
        assert form.is_valid()
        assert "<script>" not in form.cleaned_data["content"]
