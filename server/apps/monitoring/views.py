from asgiref.sync import sync_to_async
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .exporters import DB_UP, NEO4J_UP


async def _check_django_db() -> bool:
    """Return True if the default Django database is reachable."""
    try:
        await sync_to_async(connection.ensure_connection)()
        return True
    except Exception:
        return False


async def _check_neo4j() -> bool:
    """Return True if the Neo4j database is reachable.

    Attempts to import neomodel and run a trivial Cypher query.  Returns
    False if neomodel is not installed or the connection fails.
    """
    try:
        from neomodel import db as neo4j_db

        results, _ = await sync_to_async(neo4j_db.cypher_query)("RETURN 1")
        return bool(results)
    except Exception:
        return False


@require_http_methods(["GET"])
async def health_check(request):
    """Health-check endpoint returning JSON with component statuses.

    Response example::

        {
            "status": "healthy",
            "db": "ok",
            "neo4j": "ok"
        }
    """
    db_ok = await _check_django_db()
    neo4j_ok = await _check_neo4j()

    # Update Prometheus gauges so the /metrics/ endpoint reflects the latest
    # health state even between health-check calls.
    DB_UP.set(1 if db_ok else 0)
    NEO4J_UP.set(1 if neo4j_ok else 0)

    payload = {
        "status": "healthy",
        "db": "ok" if db_ok else "error",
        "neo4j": "ok" if neo4j_ok else "error",
    }
    # Always return 200 — Railway healthcheck must pass even if Neo4j is down
    return JsonResponse(payload, status=200)


@require_http_methods(["GET"])
async def prometheus_metrics(request):
    """Expose all registered Prometheus metrics in text/plain format."""
    metrics_page = generate_latest()
    return HttpResponse(
        metrics_page,
        content_type=CONTENT_TYPE_LATEST,
    )
