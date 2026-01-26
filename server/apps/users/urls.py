from django.urls import path
from .views import sync_views, async_views

app_name = 'users'

urlpatterns = [
    path('signup/', sync_views.signup_page, name='signup_page'),
    path('login/', sync_views.login_page, name='login_page'),
]

# HTMX URLs
htmx_urlpatterns = [
    path('htmx/auth/signup/', async_views.htmx_signup, name='htmx_signup'),
    path('htmx/auth/login/', async_views.htmx_login, name='htmx_login'),
]

urlpatterns += htmx_urlpatterns
