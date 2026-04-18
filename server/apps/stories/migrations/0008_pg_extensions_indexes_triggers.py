"""pg_trgm/tsvector 인덱스 + 자동 갱신 트리거."""

from django.db import migrations

PG_TRGM_EXTENSION = "CREATE EXTENSION IF NOT EXISTS pg_trgm;"

# branch_direction 유사도 검색용 GIN 인덱스
TRGM_INDEX_UP = """
CREATE INDEX IF NOT EXISTS idx_episode_branch_direction_trgm
ON episodes USING gin (branch_direction gin_trgm_ops);
"""
TRGM_INDEX_DOWN = "DROP INDEX IF EXISTS idx_episode_branch_direction_trgm;"

# content 전문 검색용 tsvector 생성 컬럼 + GIN 인덱스
TSVECTOR_UP = """
ALTER TABLE episodes ADD COLUMN IF NOT EXISTS content_search tsvector
    GENERATED ALWAYS AS (to_tsvector('simple', coalesce(content, ''))) STORED;
CREATE INDEX IF NOT EXISTS idx_episode_content_search
ON episodes USING gin (content_search);
"""
TSVECTOR_DOWN = """
DROP INDEX IF EXISTS idx_episode_content_search;
ALTER TABLE episodes DROP COLUMN IF EXISTS content_search;
"""

# 별점 집계 자동 갱신 트리거
RATING_TRIGGER_UP = """
CREATE OR REPLACE FUNCTION update_episode_rating_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        UPDATE episodes SET
            avg_rating = (SELECT AVG(score)::float FROM ratings WHERE episode_id = OLD.episode_id),
            rating_count = (SELECT COUNT(*) FROM ratings WHERE episode_id = OLD.episode_id)
        WHERE id = OLD.episode_id;
        RETURN OLD;
    ELSE
        UPDATE episodes SET
            avg_rating = (SELECT AVG(score)::float FROM ratings WHERE episode_id = NEW.episode_id),
            rating_count = (SELECT COUNT(*) FROM ratings WHERE episode_id = NEW.episode_id)
        WHERE id = NEW.episode_id;
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_rating_stats ON ratings;
CREATE TRIGGER trg_rating_stats
AFTER INSERT OR UPDATE OR DELETE ON ratings
FOR EACH ROW EXECUTE FUNCTION update_episode_rating_stats();
"""
RATING_TRIGGER_DOWN = """
DROP TRIGGER IF EXISTS trg_rating_stats ON ratings;
DROP FUNCTION IF EXISTS update_episode_rating_stats();
"""

# engagement_score 자동 갱신 트리거
ENGAGEMENT_TRIGGER_UP = """
CREATE OR REPLACE FUNCTION update_engagement_score()
RETURNS TRIGGER AS $$
BEGIN
    NEW.engagement_score = NEW.visit_count::float;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_engagement_score ON episode_links;
CREATE TRIGGER trg_engagement_score
BEFORE UPDATE OF visit_count ON episode_links
FOR EACH ROW EXECUTE FUNCTION update_engagement_score();
"""
ENGAGEMENT_TRIGGER_DOWN = """
DROP TRIGGER IF EXISTS trg_engagement_score ON episode_links;
DROP FUNCTION IF EXISTS update_engagement_score();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("stories", "0007_remove_episode_direction_embedding_episodelink"),
    ]

    operations = [
        migrations.RunSQL(PG_TRGM_EXTENSION, reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(TRGM_INDEX_UP, reverse_sql=TRGM_INDEX_DOWN),
        migrations.RunSQL(TSVECTOR_UP, reverse_sql=TSVECTOR_DOWN),
        migrations.RunSQL(RATING_TRIGGER_UP, reverse_sql=RATING_TRIGGER_DOWN),
        migrations.RunSQL(ENGAGEMENT_TRIGGER_UP, reverse_sql=ENGAGEMENT_TRIGGER_DOWN),
    ]
