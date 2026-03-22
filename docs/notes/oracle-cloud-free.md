# Oracle Cloud Free 티어로 이전 검토

## 동기
- Railway 비용 절감
- Terraform으로 인프라 코드화 가능

## Always Free 티어 주요 리소스
- ARM VM: 최대 4 OCPU, 24GB RAM (1~2개 인스턴스)
- AMD VM: 2개 (1/8 OCPU, 1GB RAM each)
- 블록 스토리지: 200GB
- 오브젝트 스토리지: 10GB
- Autonomous DB: 2개 (각 20GB)
- 로드밸런서: 1개 (10Mbps)

## 해야 할 것
- Terraform 구성 (VM + 네트워크 + 방화벽)
- 배포 파이프라인 구성 (GitHub Actions + SSH)
- SSL 설정 (Let's Encrypt + nginx)
- Docker 또는 직접 배포 방식 결정

## 주의사항
- ARM VM 가용량 부족 이슈 (리전 선택 중요)
- 30일 무료 크레딧 소진 후 유료 리소스 자동 삭제됨
- Railway 대비 운영 부담 증가

## 우선순위
낮음 — 급하지 않음, 현재 Railway로 운영 중
