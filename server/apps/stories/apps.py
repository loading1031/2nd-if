from django.apps import AppConfig


class StoriesConfig(AppConfig):
    name = 'apps.stories'

    def ready(self):
        from django.conf import settings
        from neomodel import config
        config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL
