"""PostgreSQL pg_trgm 기반 유사도 검사 (Ollama 임베딩 대체)."""

from django.db.models import FloatField, Func, Value

# pg_trgm similarity 임계값 (0.0~1.0)
# cosine similarity 0.75에 대응, 한국어 짧은 텍스트 기준으로 캘리브레이션 필요
SIMILARITY_THRESHOLD = 0.3


class TrigramSimilarity(Func):
    """PostgreSQL similarity(a, b) 함수 래퍼."""

    function = "similarity"
    output_field = FloatField()


def find_similar_branches(work_id, direction_text, threshold=SIMILARITY_THRESHOLD):
    """기존 분기 중 유사한 방향을 가진 에피소드 검색.

    pg_trgm의 similarity()는 언어 무관하게 문자 trigram으로 비교하므로
    한국어에서도 별도 설정 없이 동작한다.
    """
    from .models import Episode

    return (
        Episode.objects.filter(work_id=work_id)
        .exclude(branch_direction="")
        .annotate(
            sim=TrigramSimilarity(
                "branch_direction",
                Value(direction_text),
            )
        )
        .filter(sim__gte=threshold)
        .order_by("-sim")
    )
