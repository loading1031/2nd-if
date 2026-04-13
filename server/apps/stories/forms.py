import nh3
from django import forms

from .models import Episode, Work

ALLOWED_TAGS = {"p", "strong", "em", "br", "img", "hr", "h2", "h3", "ul", "ol", "li"}
ALLOWED_ATTRIBUTES = {
    "img": {"src", "alt"},
}


def _clean_html_content(content: str) -> str:
    if content:
        return nh3.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    return content


class WorkCreateForm(forms.ModelForm):
    class Meta:
        model = Work
        fields = ["title", "description", "license", "font"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["font"].required = False


class EpisodeCreateForm(forms.ModelForm):
    class Meta:
        model = Episode
        fields = ["title", "content", "is_paid", "price"]

    def clean_content(self):
        return _clean_html_content(self.cleaned_data.get("content", ""))


class BranchCreateForm(forms.ModelForm):
    class Meta:
        model = Episode
        fields = ["branch_direction", "title", "content", "is_paid", "price"]

    def clean_branch_direction(self):
        direction = self.cleaned_data.get("branch_direction", "")
        if len(direction) < 5:
            raise forms.ValidationError("분기 방향을 5자 이상 입력해주세요.")
        return direction

    def clean_content(self):
        return _clean_html_content(self.cleaned_data.get("content", ""))
