"""Push Prometheus metrics to Grafana Cloud at regular intervals.

Grafana Cloud accepts Prometheus text format via the Influx-style import
endpoint.  A background daemon thread POSTs the output of
``prometheus_client.generate_latest()`` every ``PUSH_INTERVAL`` seconds.

Required environment variables (set in Railway Variables):
    GRAFANA_CLOUD_PROM_URL  – e.g. https://influx-prod-xx-xxx.grafana.net/api/v1/push/influx/write
    GRAFANA_CLOUD_PROM_USER – Prometheus username (numeric ID)
    GRAFANA_CLOUD_API_KEY   – Access policy token with metrics:write scope
"""

import logging
import os
import threading
import time

import requests
from prometheus_client import generate_latest

logger = logging.getLogger(__name__)

PUSH_INTERVAL = int(os.environ.get("GRAFANA_PUSH_INTERVAL", "60"))


def _push_loop():
    """Blocking loop that pushes metrics forever."""
    url = os.environ.get("GRAFANA_CLOUD_PROM_URL", "")
    user = os.environ.get("GRAFANA_CLOUD_PROM_USER", "")
    api_key = os.environ.get("GRAFANA_CLOUD_API_KEY", "")

    if not all([url, user, api_key]):
        logger.info("Grafana Cloud credentials not set — metrics push disabled.")
        return

    logger.info("Metrics push to Grafana Cloud started (interval=%ds).", PUSH_INTERVAL)

    while True:
        time.sleep(PUSH_INTERVAL)
        try:
            metrics = generate_latest()
            resp = requests.post(
                url,
                data=metrics,
                headers={"Content-Type": "text/plain"},
                auth=(user, api_key),
                timeout=10,
            )
            if resp.status_code >= 400:
                logger.warning("Metrics push failed: %s %s", resp.status_code, resp.text[:200])
        except Exception:
            logger.exception("Metrics push error")


def start_push_thread():
    """Start the background push thread (idempotent, safe to call multiple times)."""
    t = threading.Thread(target=_push_loop, daemon=True, name="grafana-push")
    t.start()
