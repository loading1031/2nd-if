import os

from asgiref.sync import sync_to_async
from django.db import connection
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_http_methods
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .exporters import DB_UP


async def _check_django_db() -> bool:
    """Return True if the default Django database is reachable."""
    try:
        await sync_to_async(connection.ensure_connection)()
        return True
    except Exception:
        return False


@require_http_methods(["GET"])
async def health_check(request):
    """Health-check endpoint returning JSON with component statuses."""
    db_ok = await _check_django_db()

    DB_UP.set(1 if db_ok else 0)

    payload = {
        "status": "healthy" if db_ok else "unhealthy",
        "db": "ok" if db_ok else "error",
    }
    return JsonResponse(payload, status=200 if db_ok else 503)


@require_http_methods(["GET"])
async def prometheus_metrics(request):
    """Expose all registered Prometheus metrics in text/plain format.

    Access is restricted by METRICS_TOKEN environment variable.
    If not set, allows all requests (development mode).
    """
    metrics_token = os.environ.get("METRICS_TOKEN")
    if metrics_token:
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header != f"Bearer {metrics_token}":
            return HttpResponseForbidden("Forbidden")

    metrics_page = generate_latest()
    return HttpResponse(
        metrics_page,
        content_type=CONTENT_TYPE_LATEST,
    )
