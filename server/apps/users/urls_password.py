from django.urls import path

from .views import password_views

# These should be added to users/urls.py by the main agent after merge
urlpatterns = [
    path("password-reset/", password_views.password_reset_page, name="password_reset"),
    path("password-reset/<uidb64>/<token>/", password_views.password_reset_confirm_page, name="password_reset_confirm"),
    path("htmx/auth/password-reset/", password_views.htmx_password_reset, name="htmx_password_reset"),
    path(
        "htmx/auth/password-reset/<uidb64>/<token>/",
        password_views.htmx_password_reset_confirm,
        name="htmx_password_reset_confirm",
    ),
]
