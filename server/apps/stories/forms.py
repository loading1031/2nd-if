from django import forms

from .models import Work, Episode


class WorkCreateForm(forms.ModelForm):
    class Meta:
        model = Work
        fields = ["title", "description", "license"]


class EpisodeCreateForm(forms.ModelForm):
    class Meta:
        model = Episode
        fields = ["title", "content", "is_paid", "price"]
