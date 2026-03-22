# 에피소드 리더 복사 방지 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[copy-protection]] - 복사 방지 시스템

## 패턴 라이브러리
- (에피소드 리더 페이지에 통합)

## 프로덕션 템플릿
- `server/apps/stories/templates/stories/partials/episode_content.html`

## 복사 시 출처 삽입

텍스트 복사를 허용하되, 클립보드 내용 끝에 자동 추가:
```
[복사된 텍스트]

— 「작품명」 N화: 에피소드 제목
https://2nd-if.com/stories/{id}/episodes/{n}/
```

## 시각 워터마크 (유료만)

- 본문 위에 반투명 닉네임 오버레이 (opacity 3%)
- 30도 회전, 중앙 배치
- pointer-events: none (클릭 안 먹힘)
- 무료 에피소드는 적용 안 함

## 사용 컴포넌트
- `server/static/js/copy-protection.js`
- CSS `.novel-reader`, `.novel-reader-watermark`

## 개발
- (Step 1~4에서 구현)
