"""Django logging handler that pushes logs to Grafana Cloud Loki.

Buffers log records and flushes to Loki's ``/loki/api/v1/push`` endpoint
every ``FLUSH_INTERVAL`` seconds or when the buffer reaches ``BATCH_SIZE``.

Required environment variables (set in Railway Variables):
    GRAFANA_CLOUD_LOKI_URL  – e.g. https://logs-prod-xx.grafana.net
    GRAFANA_CLOUD_LOKI_USER – Loki username (numeric ID)
    GRAFANA_CLOUD_API_KEY   – Access policy token with logs:write scope
"""

import logging
import os
import threading
import time

import requests


class LokiHandler(logging.Handler):
    """Logging handler that batches and pushes to Grafana Cloud Loki."""

    FLUSH_INTERVAL = 10  # seconds
    BATCH_SIZE = 50  # flush after this many records

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = os.environ.get("GRAFANA_CLOUD_LOKI_URL", "")
        self.user = os.environ.get("GRAFANA_CLOUD_LOKI_USER", "")
        self.api_key = os.environ.get("GRAFANA_CLOUD_API_KEY", "")
        self._buffer = []
        self._lock = threading.Lock()
        self._enabled = all([self.url, self.user, self.api_key])

        if self._enabled:
            self._start_flush_thread()

    def _start_flush_thread(self):
        t = threading.Thread(target=self._flush_loop, daemon=True, name="loki-flush")
        t.start()

    def _flush_loop(self):
        while True:
            time.sleep(self.FLUSH_INTERVAL)
            self._flush()

    def emit(self, record):
        if not self._enabled:
            return
        ts = str(int(record.created * 1e9))  # nanoseconds as string
        line = self.format(record)
        with self._lock:
            self._buffer.append((ts, line, record.levelname.lower()))
            if len(self._buffer) >= self.BATCH_SIZE:
                self._flush_locked()

    def _flush(self):
        with self._lock:
            self._flush_locked()

    def _flush_locked(self):
        """Must be called with self._lock held."""
        if not self._buffer:
            return

        # Group by level
        streams = {}
        for ts, line, level in self._buffer:
            if level not in streams:
                streams[level] = []
            streams[level].append([ts, line])
        self._buffer.clear()

        payload = {
            "streams": [
                {
                    "stream": {
                        "app": "2nd-if",
                        "level": level,
                    },
                    "values": values,
                }
                for level, values in streams.items()
            ]
        }

        push_url = f"{self.url.rstrip('/')}/loki/api/v1/push"
        try:
            requests.post(
                push_url,
                json=payload,
                auth=(self.user, self.api_key),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
        except Exception:
            pass  # Don't let logging failures crash the app
