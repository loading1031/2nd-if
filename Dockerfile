# ============================================================
# 2nd-if Production Dockerfile
# Django 6.0 + HTMX + Tailwind v4 + DaisyUI
# ============================================================

# --- Stage 1: Build static assets ---
FROM python:3.14-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system dependencies for build
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --extra prod

# Install Node dependencies (DaisyUI plugin for Tailwind v4)
COPY package.json yarn.lock ./
RUN npm install --production

# Download Tailwind CSS v4 standalone CLI (ARM/x64 자동 감지)
ARG TARGETARCH
RUN TAILWIND_ARCH=$([ "$TARGETARCH" = "arm64" ] && echo "arm64" || echo "x64") && \
    curl -sLO "https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-${TAILWIND_ARCH}" && \
    mv "tailwindcss-linux-${TAILWIND_ARCH}" /usr/local/bin/tailwindcss && \
    chmod +x /usr/local/bin/tailwindcss

# Copy application code
COPY server/ ./server/

# Copy node_modules into server/ so @plugin "daisyui" resolves
RUN cp -r node_modules server/node_modules

# Build Tailwind CSS (minified production build)
RUN cd server && tailwindcss -i static/css/input.css -o static/css/output.css --minify

# Remove source CSS (prevent WhiteNoise post-processing error)
RUN rm -f server/static/css/input.css

# Collect static files
ENV DJANGO_SETTINGS_MODULE=config.settings.prod
ARG SECRET_KEY=build-only-secret-key
RUN cd server && uv run --no-dev python manage.py collectstatic --noinput

# --- Stage 2: Production runtime ---
FROM python:3.14-slim AS runtime

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy Grafana Alloy binary from official image
COPY --from=grafana/alloy:latest /bin/alloy /usr/local/bin/alloy

WORKDIR /app

# Install Python dependencies (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --extra prod

# Copy application code from builder
COPY --from=builder /app/server/ ./server/

# Copy collected static files
COPY --from=builder /app/server/staticfiles/ ./server/staticfiles/

# Copy Alloy config + start script
COPY docker/alloy/config.alloy /etc/alloy/config.alloy
COPY scripts/start.sh /app/start.sh

# Create data directory (Railway Volume mounts to /data)
RUN mkdir -p /data/media

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app /data
USER appuser

WORKDIR /app/server

EXPOSE 8000

CMD ["/app/start.sh"]
