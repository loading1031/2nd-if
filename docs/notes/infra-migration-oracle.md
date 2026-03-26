# 오라클 클라우드 통합 인프라 이주 검토

> 아이디어 메모 (프로덕션 준비 시)

## 현재
- Django: Railway
- Dify: 별도 배포 예정
- Neo4j: Aura Free (비활성 시 자동 Pause)
- 모니터링: Grafana Cloud

## 검토 안
- 오라클 클라우드 Free tier (ARM Ampere, 24GB RAM)에 전부 통합
- Docker Compose: Django + Dify + Ollama + Neo4j + PostgreSQL
- 장점: 비용 $0, 한 곳에서 관리, Ollama로 임베딩/LLM 무료
- 단점: 단일 장애점, 24GB로 전부 감당 가능한지 확인 필요

## LLM/임베딩 전략
- 로컬 개발: Ollama (무료)
- 프로덕션: Gemini API (저렴, Dify에서 설정)
- 또는 오라클에 Ollama 직접 → 완전 무료
