from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class SignupForm(forms.Form):
    email = forms.EmailField()
    nickname = forms.CharField(max_length=50)
    password = forms.CharField(min_length=8)
    password_confirm = forms.CharField(min_length=8)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("이미 사용 중인 이메일입니다.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "비밀번호가 일치하지 않습니다.")
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
