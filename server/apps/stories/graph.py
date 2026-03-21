from neomodel import (
    StructuredNode,
    StructuredRel,
    IntegerProperty,
    FloatProperty,
    BooleanProperty,
    RelationshipTo,
    RelationshipFrom,
    UniqueIdProperty,
)


class NextRel(StructuredRel):
    """에피소드 간 NEXT 관계 (엣지 속성)."""

    is_original = BooleanProperty(default=False)
    visit_count = IntegerProperty(default=0)
    engagement_score = FloatProperty(default=0.0)


class EpisodeNode(StructuredNode):
    """Neo4j 에피소드 노드. Django Episode 모델의 PK를 참조."""

    episode_id = IntegerProperty(unique_index=True, required=True)
    work_id = IntegerProperty(index=True, required=True)

    next_episodes = RelationshipTo("EpisodeNode", "NEXT", model=NextRel)
    prev_episodes = RelationshipFrom("EpisodeNode", "NEXT", model=NextRel)
    branches_from = RelationshipTo("EpisodeNode", "BRANCHES_FROM")
    branched_by = RelationshipFrom("EpisodeNode", "BRANCHES_FROM")

    @classmethod
    def get_or_create_node(cls, episode_id, work_id):
        """Django Episode PK로 노드 조회 또는 생성."""
        nodes = cls.nodes.filter(episode_id=episode_id)
        if nodes:
            return nodes[0]
        return cls(episode_id=episode_id, work_id=work_id).save()

    def get_next_episodes_sorted(self):
        """다음 화 목록을 engagement_score 내림차순으로 반환.
        원작(is_original=True)은 항상 첫 번째."""
        results = []
        for rel in self.next_episodes.all_relationships():
            results.append({
                "node": rel.end_node(),
                "is_original": rel.is_original,
                "visit_count": rel.visit_count,
                "engagement_score": rel.engagement_score,
            })
        results.sort(key=lambda x: (-x["is_original"], -x["engagement_score"]))
        return results

    def add_next(self, target_node, is_original=False):
        """다음 화 연결."""
        return self.next_episodes.connect(target_node, {
            "is_original": is_original,
            "visit_count": 0,
            "engagement_score": 0.0,
        })

    def add_branch(self, branch_node):
        """분기 관계 생성."""
        return self.branches_from.connect(branch_node)

    @classmethod
    def increment_visit(cls, from_episode_id, to_episode_id, episode_avg_rating):
        """경로 이동 시 visit_count 증가 (별점 3점 이하 제외)."""
        if episode_avg_rating is not None and episode_avg_rating <= 3.0:
            return

        from_node = cls.nodes.get(episode_id=from_episode_id)
        to_node = cls.nodes.get(episode_id=to_episode_id)
        rel = from_node.next_episodes.relationship(to_node)
        if rel:
            rel.visit_count += 1
            rel.engagement_score = float(rel.visit_count)
            rel.save()
