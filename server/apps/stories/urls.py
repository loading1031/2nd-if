from django.urls import path

from .views import async_views, sync_views

app_name = "stories"

urlpatterns = [
    # 페이지 뷰
    path("", sync_views.work_list, name="work_list"),
    path("create/", sync_views.work_create, name="work_create"),
    path("<int:pk>/", sync_views.work_detail, name="work_detail"),
    path("<int:work_pk>/episodes/write/", sync_views.episode_write, name="episode_write"),
    path("<int:work_pk>/episodes/<int:episode_number>/", sync_views.episode_read, name="episode_read"),
    path("<int:work_pk>/episodes/<int:episode_number>/branch/", sync_views.branch_create, name="branch_create"),
]

# HTMX 엔드포인트
htmx_urlpatterns = [
    path("htmx/works/", async_views.htmx_work_list, name="htmx_work_list"),
    path("htmx/works/create/", async_views.htmx_work_create, name="htmx_work_create"),
    path("htmx/<int:work_pk>/episodes/", async_views.htmx_episode_list, name="htmx_episode_list"),
    path("htmx/<int:work_pk>/episodes/create/", async_views.htmx_episode_create, name="htmx_episode_create"),
    path("htmx/<int:work_pk>/episodes/<int:episode_number>/", async_views.htmx_episode_read, name="htmx_episode_read"),
    path(
        "htmx/<int:work_pk>/episodes/<int:episode_number>/rate/",
        async_views.htmx_rate_episode,
        name="htmx_rate_episode",
    ),
    path(
        "htmx/<int:work_pk>/episodes/<int:episode_number>/next/",
        async_views.htmx_next_episodes,
        name="htmx_next_episodes",
    ),
    path(
        "htmx/<int:work_pk>/episodes/<int:episode_number>/branch/",
        async_views.htmx_branch_create,
        name="htmx_branch_create",
    ),
    path(
        "htmx/<int:work_pk>/episodes/<int:from_number>/visit/<int:to_number>/",
        async_views.htmx_visit_episode,
        name="htmx_visit_episode",
    ),
]

urlpatterns += htmx_urlpatterns
