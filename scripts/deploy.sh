#!/bin/bash
set -euo pipefail

# ──────────────────────────────────────────────
# Blue-Green 배포 스크립트
#
# 흐름:
#   1. 현재 활성 슬롯 확인 (blue/green)
#   2. 새 이미지 빌드
#   3. 비활성 슬롯에 새 컨테이너 시작
#   4. Health check + 테스트 실행
#   5. 통과 → Caddy 전환 → 이전 슬롯 중지
#   6. 실패 → 비활성 슬롯 중지 → 서비스 무사
# ──────────────────────────────────────────────

APP_DIR="/opt/app"
COMPOSE="docker compose -f ${APP_DIR}/docker-compose.prod.yml"
HEALTH_URL="http://localhost:8000/health/"
MAX_RETRIES=30
RETRY_INTERVAL=2

cd "$APP_DIR"

# ── 1. 현재 활성 슬롯 확인 ──
if docker ps --format '{{.Names}}' | grep -q 'django-blue'; then
    ACTIVE="blue"
    NEXT="green"
else
    ACTIVE="green"
    NEXT="blue"
fi

echo "▶ 현재 활성: $ACTIVE → 새 배포: $NEXT"

# ── 2. 새 이미지 빌드 ──
echo "▶ 이미지 빌드 중..."
docker build -t 2nd-if:latest .

# ── 3. 비활성 슬롯에 새 컨테이너 시작 ──
echo "▶ $NEXT 컨테이너 시작..."
$COMPOSE --profile "$NEXT" up -d "django-$NEXT"

# ── 4. Health check ──
echo "▶ Health check 대기 중..."
NEXT_CONTAINER="django-$NEXT"
for i in $(seq 1 $MAX_RETRIES); do
    if docker exec "$NEXT_CONTAINER" curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
        echo "  ✓ Health check 통과 (${i}/${MAX_RETRIES})"
        break
    fi
    if [ "$i" -eq "$MAX_RETRIES" ]; then
        echo "  ✗ Health check 실패! $NEXT 롤백"
        $COMPOSE --profile "$NEXT" stop "django-$NEXT"
        exit 1
    fi
    echo "  ... 재시도 (${i}/${MAX_RETRIES})"
    sleep $RETRY_INTERVAL
done

# ── 5. 테스트 실행 ──
echo "▶ 테스트 실행 중..."
if ! docker exec "$NEXT_CONTAINER" uv run python -m pytest \
    apps/core/tests.py \
    apps/users/tests.py \
    apps/stories/tests.py \
    -v --tb=short 2>&1; then
    echo "  ✗ 테스트 실패! $NEXT 롤백"
    $COMPOSE --profile "$NEXT" stop "django-$NEXT"
    exit 1
fi
echo "  ✓ 테스트 통과"

# ── 6. Caddy 전환 ──
echo "▶ Caddy를 $NEXT로 전환..."
# Caddy 환경변수 업데이트 후 재시작
UPSTREAM="django-${NEXT}:8000"
$COMPOSE stop caddy
UPSTREAM="$UPSTREAM" $COMPOSE up -d caddy
echo "  ✓ Caddy → $NEXT"

# ── 7. 이전 슬롯 중지 ──
echo "▶ $ACTIVE 컨테이너 중지..."
$COMPOSE --profile "$ACTIVE" stop "django-$ACTIVE"

# ── 정리 ──
docker image prune -f
echo "✅ 배포 완료: $ACTIVE → $NEXT"
