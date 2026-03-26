# 지갑 주소 설정 UI 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[revenue]] - 수익 모델 (원작자 지갑 주소 등록)
- [[auth]] - 인증 시스템 (프로필 설정)

## 패턴 라이브러리
- (추후 추가)

## 프로덕션 템플릿
- (추후 추가)

## 레이아웃
- 프로필 설정 페이지 내 별도 섹션
- DaisyUI `card bg-base-100 shadow-xl` 안에 구성

### 카드 구성
1. **제목**: "지갑 주소" (`card-title`)
2. **현재 주소 표시**: 등록된 주소가 있으면 `badge badge-lg` 또는 모노스페이스 텍스트로 표시 (앞 6자 + ... + 뒤 4자 축약)
3. **지갑 주소 입력 필드**: `input input-bordered w-full`, placeholder `0x...`
4. **버튼 영역**:
   - "MetaMask에서 가져오기" (`btn btn-outline`, MetaMask 아이콘) — MetaMask 연결하여 주소 자동 입력
   - "저장" (`btn btn-primary`)

## 필드
| 필드 | 타입 | placeholder | 검증 |
|------|------|-------------|------|
| wallet_address | text | 0x... | `0x` + 40자 hex (정규식: `^0x[0-9a-fA-F]{40}$`) |

## 상태별 UI

### 지갑 미등록
- 입력 필드 비어 있음
- "지갑 주소를 등록하면 유료 에피소드를 발행할 수 있습니다." 안내 텍스트 (`text-sm text-base-content/60`)

### 지갑 등록됨
- 현재 주소 표시 (축약형: `0x1234...abcd`)
- 입력 필드에 기존 주소 채워짐
- "저장" 버튼으로 변경 가능

### MetaMask 미설치
- "MetaMask에서 가져오기" 클릭 시 `alert alert-warning` — "MetaMask가 설치되어 있지 않습니다."
- 직접 입력은 가능

### 저장 성공
- `alert alert-success` — "지갑 주소가 저장되었습니다."
- HTMX로 카드 영역 갱신

### 저장 실패 (형식 오류)
- 입력 필드 `input-error` 스타일
- `label-text-alt text-error` — "올바른 Polygon 지갑 주소를 입력해주세요. (0x + 40자리 16진수)"

## 반응형
- 모바일: 카드 전체 너비 (`w-full`)
- 데스크톱: `max-w-lg` 내에서 표시
- 버튼: 모바일에서 세로 배치 (`flex flex-col gap-2 sm:flex-row`)

## 사용 컴포넌트
- DaisyUI `card`, `input`, `btn`, `alert`, `badge`
- `components/form_field.html`
- (추후 `components/wallet_settings.html` 생성)

## 개발
- (추후 추가)
