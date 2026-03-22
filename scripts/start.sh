#!/bin/sh
set -e

# 1. Run migrations
uv run --no-dev python manage.py migrate --noinput

# 2. Start Alloy in background (metrics push to Grafana Cloud)
if [ -n "$GRAFANA_CLOUD_PROM_URL" ]; then
    /usr/local/bin/alloy run /etc/alloy/config.alloy \
        --server.http.listen-addr=127.0.0.1:12345 \
        --stability.level=generally-available &
    echo "Alloy started (metrics push enabled)"
else
    echo "Alloy skipped (GRAFANA_CLOUD_PROM_URL not set)"
fi

# 3. Start gunicorn (foreground)
exec uv run --no-dev gunicorn config.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    -b 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
