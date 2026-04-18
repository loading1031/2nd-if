"""PostgreSQL 기반 에피소드 그래프 (Neo4j 대체)."""

from django.db.models import F

from .models import EpisodeLink


async def aget_or_create_link(from_episode_id, to_episode_id, link_type, is_original=False):
    """에피소드 링크 생성 또는 조회."""
    return await EpisodeLink.objects.aget_or_create(
        from_episode_id=from_episode_id,
        to_episode_id=to_episode_id,
        link_type=link_type,
        defaults={
            "is_original": is_original,
            "visit_count": 0,
            "engagement_score": 0.0,
        },
    )


def get_next_episodes_sorted(episode_id):
    """다음 화 목록: 원작 우선, engagement_score 내림차순."""
    return (
        EpisodeLink.objects.filter(
            from_episode_id=episode_id,
            link_type=EpisodeLink.LinkType.NEXT,
        )
        .select_related("to_episode", "to_episode__author")
        .order_by("-is_original", "-engagement_score")
    )


async def increment_visit(from_episode_id, to_episode_id, episode_avg_rating):
    """경로 이동 시 visit_count 증가 (별점 3점 이하 제외).

    engagement_score는 DB 트리거가 자동 갱신.
    """
    if episode_avg_rating is not None and episode_avg_rating <= 3.0:
        return

    await EpisodeLink.objects.filter(
        from_episode_id=from_episode_id,
        to_episode_id=to_episode_id,
        link_type=EpisodeLink.LinkType.NEXT,
    ).aupdate(visit_count=F("visit_count") + 1)
