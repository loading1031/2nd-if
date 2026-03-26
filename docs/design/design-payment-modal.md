# 결제 모달 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[revenue]] - 수익 모델 (독자 → 원작자 스테이블코인 직접 결제)

## 패턴 라이브러리
- (추후 추가)

## 프로덕션 템플릿
- (추후 추가)

## 레이아웃
- DaisyUI `modal` 사용 (`modal-box max-w-md`)
- 유료 에피소드 클릭 시 표시
- 이미 구매한 에피소드는 모달 없이 바로 열람

### 모달 구성
1. **헤더**: 에피소드 제목 + 가격 표시 (예: `0.5 USDC`)
2. **토큰 선택**: USDC / USDT 라디오 카드
3. **결제 버튼**: "MetaMask로 결제" (`btn btn-primary w-full`)
4. **닫기**: `modal-backdrop` 클릭 또는 X 버튼

### 토큰 선택 UI
- DaisyUI `radio` 카드 스타일 (2열 그리드, `grid grid-cols-2 gap-3`)
- 각 카드: 토큰 아이콘 + 이름 (USDC / USDT)
- 선택 시 `border-primary` 하이라이트
- 기본 선택: USDC

## 상태별 UI

### 기본 상태
- 토큰 선택 라디오 카드 + "MetaMask로 결제" 버튼

### MetaMask 미설치
- `alert alert-warning` — "MetaMask가 설치되어 있지 않습니다."
- "MetaMask 설치하기" 외부 링크 (`btn btn-outline btn-sm`, https://metamask.io)
- 결제 버튼 비활성화 (`btn-disabled`)

### 네트워크 틀림
- `alert alert-warning` — "Polygon 네트워크로 전환해주세요."
- "Polygon으로 전환" 버튼 (`btn btn-warning btn-sm`)
- 결제 버튼 비활성화 (`btn-disabled`)

### 결제 중
- 결제 버튼 → `loading loading-spinner` + "트랜잭션 확인 중..."
- 모달 닫기 비활성화 (backdrop 클릭 무시)
- 토큰 선택 비활성화

### 성공
- `alert alert-success` — "결제가 완료되었습니다!"
- 2초 후 자동으로 에피소드 열람 페이지로 이동
- 또는 "에피소드 읽기" 버튼 (`btn btn-primary`)

### 실패
- `alert alert-error` — "결제에 실패했습니다."
- "다시 시도" 버튼 (`btn btn-error btn-outline`)
- 토큰 선택으로 돌아감

### 잔액 부족
- `alert alert-error` — "잔액이 부족합니다."
- 결제 버튼 비활성화

## 반응형
- 모바일: `modal-bottom` (하단에서 슬라이드 업)
- 데스크톱: 화면 중앙 (`modal-middle`)
- 토큰 선택 카드: 모바일에서도 2열 유지 (`grid-cols-2`)

## 사용 컴포넌트
- DaisyUI `modal`, `alert`, `btn`, `radio`, `loading`
- (추후 `components/payment_modal.html` 생성)

## 개발
- (추후 추가)
