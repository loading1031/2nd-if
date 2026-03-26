#!/bin/bash
# A1 인스턴스 품절 시 5분마다 재시도
# 사용법: ./retry-apply.sh

cd "$(dirname "$0")"

while true; do
    echo "$(date) — terraform apply 시도..."
    if terraform apply -auto-approve 2>&1 | tee /tmp/tf-apply.log; then
        echo "✅ 성공!"
        break
    fi

    if ! grep -q "Out of host capacity" /tmp/tf-apply.log; then
        echo "❌ capacity 외 다른 에러 발생. 중단."
        break
    fi

    echo "⏳ 품절. 5분 후 재시도..."
    sleep 300
done
