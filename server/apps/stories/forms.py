import nh3
from django import forms

from .models import Episode, Work

ALLOWED_TAGS = {"p", "strong", "em", "br", "img", "hr", "h2", "h3", "ul", "ol", "li"}
ALLOWED_ATTRIBUTES = {"img": {"src", "alt"}}


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
        content = self.cleaned_data.get("content", "")
        if content:
            content = nh3.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
        return content
