import time

from prometheus_client import Counter, Gauge, Histogram

REQUEST_COUNT = Counter(
    "django_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "django_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

ACTIVE_REQUESTS = Gauge(
    "django_http_requests_active",
    "Number of active HTTP requests",
)


def _normalise_path(path: str) -> str:
    """Collapse numeric path segments to reduce cardinality.

    ``/stories/42/branches/7/`` becomes ``/stories/{id}/branches/{id}/``.
    """
    parts = path.strip("/").split("/")
    normalised = []
    for part in parts:
        normalised.append("{id}" if part.isdigit() else part)
    return "/" + "/".join(normalised) + "/" if normalised else "/"


class PrometheusMetricsMiddleware:
    """Collect per-request Prometheus metrics.

    Tracks request count (by method/path/status), latency histogram, and a
    gauge of currently active requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Support both sync and async Django middleware
        if callable(get_response):
            import asyncio

            if asyncio.iscoroutinefunction(get_response):
                self._is_async = True
            else:
                self._is_async = False

    async def __acall__(self, request):
        path = _normalise_path(request.path)
        method = request.method

        ACTIVE_REQUESTS.inc()
        start = time.perf_counter()

        try:
            response = await self.get_response(request)
        except Exception:
            ACTIVE_REQUESTS.dec()
            raise

        duration = time.perf_counter() - start
        status = str(response.status_code)

        REQUEST_COUNT.labels(method=method, path=path, status=status).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(duration)
        ACTIVE_REQUESTS.dec()

        return response

    def __call__(self, request):
        if self._is_async:
            # Let Django's ASGIHandler use __acall__

            return self.__acall__(request)

        path = _normalise_path(request.path)
        method = request.method

        ACTIVE_REQUESTS.inc()
        start = time.perf_counter()

        try:
            response = self.get_response(request)
        except Exception:
            ACTIVE_REQUESTS.dec()
            raise

        duration = time.perf_counter() - start
        status = str(response.status_code)

        REQUEST_COUNT.labels(method=method, path=path, status=status).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(duration)
        ACTIVE_REQUESTS.dec()

        return response
