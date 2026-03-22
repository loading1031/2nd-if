"""Custom Prometheus metrics for the 2nd-if platform.

These gauges/counters are updated by application code (views, signals, etc.)
and exposed automatically via the ``/metrics/`` endpoint.
"""

from prometheus_client import Counter, Gauge

# ---------------------------------------------------------------------------
# Story metrics
# ---------------------------------------------------------------------------

STORY_VIEWS_TOTAL = Counter(
    "app_story_views_total",
    "Total story view events",
)

BRANCH_CREATIONS_TOTAL = Counter(
    "app_branch_creations_total",
    "Total branch (분기) creation events",
)

STORY_RATINGS_TOTAL = Counter(
    "app_story_ratings_total",
    "Total story rating submissions",
)

# ---------------------------------------------------------------------------
# User metrics
# ---------------------------------------------------------------------------

ACTIVE_USERS_GAUGE = Gauge(
    "app_active_users",
    "Approximate number of active users (updated periodically)",
)

# ---------------------------------------------------------------------------
# Infrastructure metrics
# ---------------------------------------------------------------------------

NEO4J_UP = Gauge(
    "app_neo4j_up",
    "Neo4j connection health (1 = up, 0 = down)",
)

DB_UP = Gauge(
    "app_db_up",
    "Django default database health (1 = up, 0 = down)",
)
