#!/usr/bin/env bash
set -euo pipefail

echo "=== 2nd-if Fly.io Initial Setup ==="

# Create app
flyctl apps create 2nd-if --region nrt

# Create persistent volume for media uploads
flyctl volumes create media_data --region nrt --size 1

# Create Fly Postgres (free tier)
flyctl postgres create --name 2nd-if-db --region nrt --vm-size shared-cpu-1x --volume-size 1 --initial-cluster-size 1

# Attach database (sets DATABASE_URL automatically)
flyctl postgres attach 2nd-if-db

echo ""
echo "=== Setup complete ==="
echo "Next steps:"
echo "1. Set secrets: flyctl secrets set SECRET_KEY=... NEO4J_BOLT_URL=... ALLOWED_HOSTS=..."
echo "2. Deploy: flyctl deploy --remote-only"
echo "3. Run migrations: flyctl ssh console -C 'cd /app/server && uv run python manage.py migrate'"
