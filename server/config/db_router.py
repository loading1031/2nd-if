"""Read replica DB 라우터.

프로덕션에서 읽기 부하를 replica로 분산한다.
개발 환경에서는 replica가 설정되지 않으므로 default로 폴백.
"""

from django.conf import settings


class ReadReplicaRouter:
    def db_for_read(self, model, **hints):
        if "replica" in settings.DATABASES:
            return "replica"
        return "default"

    def db_for_write(self, model, **hints):
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == "default"
