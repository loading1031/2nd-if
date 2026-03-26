from django.urls import path

from .views import async_views, password_views, sync_views, wallet_views

app_name = "users"

urlpatterns = [
    path("signup/", sync_views.signup_page, name="signup_page"),
    path("login/", sync_views.login_page, name="login_page"),
    path("password-reset/", password_views.password_reset_page, name="password_reset"),
    path("password-reset/<uidb64>/<token>/", password_views.password_reset_confirm_page, name="password_reset_confirm"),
    path("wallet/", wallet_views.wallet_settings_page, name="wallet_settings"),
]

# HTMX URLs
htmx_urlpatterns = [
    path("htmx/auth/signup/", async_views.htmx_signup, name="htmx_signup"),
    path("htmx/auth/login/", async_views.htmx_login, name="htmx_login"),
    path("htmx/auth/logout/", async_views.htmx_logout, name="htmx_logout"),
    path("htmx/auth/password-reset/", password_views.htmx_password_reset, name="htmx_password_reset"),
    path(
        "htmx/auth/password-reset/<uidb64>/<token>/",
        password_views.htmx_password_reset_confirm,
        name="htmx_password_reset_confirm",
    ),
    path("htmx/wallet/save/", wallet_views.htmx_save_wallet, name="htmx_save_wallet"),
]

urlpatterns += htmx_urlpatterns
