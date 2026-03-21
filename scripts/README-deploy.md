# 2nd-if Fly.io Deployment

## Quick Start

### First-time setup

```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh
flyctl auth login

# 2. Run setup script
./scripts/fly-setup.sh

# 3. Set secrets
flyctl secrets set \
  SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')" \
  NEO4J_BOLT_URL="neo4j+s://user:pass@xxx.databases.neo4j.io" \
  ALLOWED_HOSTS="2nd-if.fly.dev"

# 4. Deploy
./scripts/fly-deploy.sh

# 5. Run initial migrations
flyctl ssh console -C 'cd /app/server && uv run python manage.py migrate'
```

### Subsequent deploys

```bash
./scripts/fly-deploy.sh
```

## Secret Management

```bash
# List secrets
flyctl secrets list

# Set/update a secret
flyctl secrets set KEY=value

# Required secrets:
#   SECRET_KEY       - Django secret key
#   DATABASE_URL     - Set automatically by fly postgres attach
#   NEO4J_BOLT_URL   - Neo4j Aura connection string
#   ALLOWED_HOSTS    - Comma-separated hostnames
```

## Database

```bash
# Run migrations
flyctl ssh console -C 'cd /app/server && uv run python manage.py migrate'

# Create superuser
flyctl ssh console -C 'cd /app/server && uv run python manage.py createsuperuser'

# Connect to postgres directly
flyctl postgres connect -a 2nd-if-db
```

## Monitoring

```bash
# View logs
flyctl logs

# Check app status
flyctl status

# SSH into running machine
flyctl ssh console
```

## Scaling

```bash
# Scale memory (if needed)
flyctl scale memory 512

# Scale to always-on (disable auto-stop)
flyctl scale count 1
```

## Important Notes

- **Region**: `nrt` (Tokyo) for lowest latency from Korea
- **VM**: 256MB shared CPU, auto-stop enabled (cost-saving)
- **Media**: Persistent volume mounted at `/app/server/media`
- **Static files**: Served via WhiteNoise (no S3 initially)
- **DB**: Fly Postgres (attached, DATABASE_URL auto-set)
- **uvicorn**: Required for async Django views (ASGI workers)
- **prod.py changes needed**: Add WhiteNoise middleware, DATABASE_URL support (dj-database-url)
