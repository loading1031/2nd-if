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
| is_branch | bool | O | 분기 여부 |

## 저장 위치
- Work, Episode 메타데이터: Django ORM (PostgreSQL)
- 에피소드 간 관계(분기 그래프): Neo4j

## 사용자 플로우
1. 원작자: 작품 생성 → 라이선스 선택 → 에피소드 작성/발행
2. 독자: 작품 목록 → 작품 선택 → 에피소드 순서대로 읽기
3. 2차 창작자: 에피소드 읽기 → 분기 생성 ([[branch]] 참조)

## 의존성
- [[auth]] — 작성자 인증
- [[license]] — 작품 생성 시 라이선스 선택
- [[branch]] — 에피소드에서 분기 생성

## 디자인 문서
- (설계 진행 후 추가)
