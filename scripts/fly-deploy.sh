#!/usr/bin/env bash
set -euo pipefail

echo "=== 2nd-if Fly.io Deploy ==="

# Check flyctl
if ! command -v flyctl &> /dev/null; then
    echo "Error: flyctl not installed. Run: curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Set secrets (first time only — uncomment and fill values)
# flyctl secrets set \
#   SECRET_KEY="your-secret-key" \
#   DATABASE_URL="postgres://..." \
#   NEO4J_BOLT_URL="neo4j+s://...@....databases.neo4j.io" \
#   ALLOWED_HOSTS=".fly.dev,your-domain.com"

# Deploy
flyctl deploy --remote-only

echo "=== Deploy complete ==="
echo "App URL: https://2nd-if.fly.dev"
