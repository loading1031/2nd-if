# 작품/에피소드 시스템

> 기획 문서

## 상태: 기획 중

## 개요
원작자가 작품을 생성하고, 에피소드(화) 단위로 연재하는 시스템.

## 데이터 구조

### 작품 (Work)
| 필드 | 타입 | 필수 | 비고 |
|------|------|------|------|
| title | string | O | 작품 제목 |
| description | text | X | 작품 소개 |
| author | User | O | 원작자 |
| license | License | O | [[license]] 참조 |
| created_at | datetime | O | |
| status | enum | O | 연재중, 완결, 중단 |

### 에피소드 (Episode)
| 필드 | 타입 | 필수 | 비고 |
|------|------|------|------|
| work | Work | O | 소속 작품 |
| episode_number | int | O | 화 번호 |
| title | string | O | 에피소드 제목 |
| content | EditorJS JSON | O | editor.js 컨텐츠 |
| author | User | O | 작성자 |
| created_at | datetime | O | |
| is_paid | bool | O | 유료 여부, default=False ([[revenue]] 참조) |
| price | decimal | X | 코인 가격 (is_paid=True일 때) |
| view_count | int | O | 조회수, default=0 |
| avg_rating | float | X | 별점 평균 (1~5), null=미등록 |
| rating_count | int | O | 별점 등록 수, default=0 |

> `is_branch` 여부는 Neo4j의 `BRANCHES_FROM` 관계로 판단 ([[branch]] 참조). Django 모델에 중복 저장하지 않음.

## 저장 위치
- Work, Episode 메타데이터: Django ORM (PostgreSQL)
- 에피소드 간 관계(분기 그래프): Neo4j

## 사용자 플로우
1. 원작자: 작품 생성 → 라이선스 선택 → 에피소드 작성/발행
2. 독자: 작품 목록 → 작품 선택 → 에피소드 순서대로 읽기
3. 2차 창작자: 에피소드 읽기 → 분기 생성 ([[branch]] 참조)

### 작품별 포인트 풀
| 필드 | 타입 | 필수 | 비고 |
|------|------|------|------|
| work | Work | O | 소속 작품 |
| point_pool | int | O | 현재 사용 가능한 포인트 풀, default=0 |
| updated_at | datetime | O | 마지막 풀 갱신 시점 |

> 매월 작품 통계 기반으로 포인트 풀 갱신 ([[point-system]] 참조)

## 의존성
- [[auth]] — 작성자 인증
- [[license]] — 작품 생성 시 라이선스 선택
- [[branch]] — 에피소드에서 분기 생성
- [[revenue]] — 유료 에피소드 가격 설정
- [[point-system]] — 작품별 포인트 풀

## 디자인 문서
- [[design-episode-reader]] - 에피소드 리더 페이지
- [[design-star-rating]] - 별점 평가 컴포넌트
- [[design-episode-write]] - 에피소드 작성 페이지
