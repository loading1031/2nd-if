from django import forms

from .models import Work, Episode


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
