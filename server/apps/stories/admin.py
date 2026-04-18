from django.contrib import admin

from .models import Episode, EpisodeLink, Rating, Work


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "license", "status", "created_at")
    list_filter = ("status", "license")
    search_fields = ("title", "author__nickname")


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("work", "episode_number", "title", "author", "is_paid", "view_count", "avg_rating")
    list_filter = ("is_paid", "work")
    search_fields = ("title", "work__title")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("episode", "user", "score", "created_at")


@admin.register(EpisodeLink)
class EpisodeLinkAdmin(admin.ModelAdmin):
    list_display = ("from_episode", "to_episode", "link_type", "is_original", "visit_count", "engagement_score")
    list_filter = ("link_type", "is_original")
