# CS FAQ 서버 로직

> 개발 문서

## 상태: 구현 이력 있음 (현재 동작 재검증 전)

과거 미구현 표시는 구현 커밋과 불일치해 정정했다. [구현 이력 이슈 #10](https://github.com/loading1031/2nd-if/issues/10)과 커밋 `d6e8f46`를 참고한다. 현재 기능 테스트·배포를 다시 확인한 상태는 아니다.

## 디자인
- [[design-cs-faq]] - CS FAQ 페이지 디자인

## 기획
- [[cs-faq]] - CS FAQ 페이지 기획

## 구현 위치

### 뷰
- `apps/core/views/async_views.py` → `cs_faq()` (async, login 불필요)

### URL
- `GET /cs/faq/` → name: `core:cs_faq`

### 템플릿
- `apps/core/templates/core/pages/cs_faq.html`

## 구현 내용

### 1. FAQ 뷰

```python
# apps/core/views/async_views.py
@require_http_methods(["GET"])
async def cs_faq(request):
    """FAQ 페이지 — 로그인 불필요, DB 접근 없음"""
    return render(request, 'core/pages/cs_faq.html')
```

### 2. URL 등록

```python
# apps/core/urls.py
path('cs/faq/', async_views.cs_faq, name='cs_faq'),
```

### 3. FAQ 템플릿

- `docs/cs-faq.md` 내용을 기반으로 DaisyUI collapse 아코디언 하드코딩
- 각 FAQ 항목에 `data-category` 속성 부여 (JS 카테고리 필터용)
- 검색: JS keyup 이벤트로 질문/답변 텍스트 매칭, 비매칭 항목 `hidden` 처리
- 카테고리 탭: JS click 이벤트로 `data-category` 필터링

### 4. 클라이언트 JS 로직

```
검색 입력 keyup → 
  각 collapse 요소의 텍스트 내용과 검색어 비교 →
  비매칭 항목 hidden 처리 →
  매칭 결과 0개면 "검색 결과가 없습니다" 표시

카테고리 탭 click →
  선택 탭에 tab-active 추가, 나머지 제거 →
  data-category 불일치 항목 hidden 처리 →
  "전체" 선택 시 모든 항목 표시
```

## FAQ 카테고리 매핑

| 카테고리 | data-category | `docs/cs-faq.md` 섹션 |
|---------|---------------|----------------------|
| 서비스 소개 | service | 서비스 소개 |
| 계정 | account | 계정 |
| 읽기 | reading | 읽기 |
| 창작 | writing | 창작 (분기 만들기) |
| 라이선스 | license | 라이선스 + 복사/저작권 |
| 결제/수익 | payment | 결제/수익 |
| 기술/오류 | tech | 기술/오류 |

## 선행 작업
- 없음 (독립 페이지, DB 접근 없음)
