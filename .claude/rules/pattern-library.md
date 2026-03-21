# 컴포넌트 & 패턴 라이브러리 컨벤션

> [← 메인으로 돌아가기](CLAUDE.md)

## 핵심 원칙: Single Source of Truth

모든 UI 컴포넌트는 `templates/components/`에 **한 번만** 정의하고, 프로덕션 템플릿과 패턴 라이브러리 모두 `{% include %}`로 참조한다.

```
templates/components/form_field.html   ← 진짜 소스
    ├── apps/users/templates/pages/login.html     ← {% include "components/form_field.html" with ... %}
    ├── apps/users/templates/pages/signup.html     ← {% include "components/form_field.html" with ... %}
    └── templates/patterns/components/form_field/  ← {% include "components/form_field.html" with ... %}
```

## 디렉토리 구조

```
templates/
├── components/                          ← 재사용 가능한 컴포넌트 (Single Source of Truth)
│   ├── form_field.html
│   ├── alert.html
│   └── navbar.html
│
├── patterns/                            ← 패턴 라이브러리 (django-pattern-library)
│   ├── base.html                        ← 컴포넌트 래퍼 (fragment용)
│   ├── base_page.html                   ← 페이지 래퍼 (full page용)
│   ├── components/                      ← 컴포넌트 전시
│   │   └── {component_name}/
│   │       ├── {component_name}.html    ← components/를 include해서 변형 전시
│   │       └── {component_name}.yaml    ← name 필드 필수
│   └── pages/                           ← 페이지 전시
│       └── {page_name}/
│           ├── {page_name}.html         ← components/를 include해서 페이지 구성
│           ├── {page_name}.yaml
│           ├── {page_name}_error.html   ← 에러 상태 변형 (선택)
│           └── {page_name}_error.yaml
│
├── base.html                            ← {% include "components/navbar.html" %}
└── ...

apps/{app_name}/templates/               ← 프로덕션 템플릿
└── pages/
    └── {page}.html                      ← {% include "components/..." with ... %}
```

## 새 컴포넌트 추가 절차

### 1. 컴포넌트 생성

`templates/components/{name}.html`에 재사용 가능한 컴포넌트를 만든다.

```html
{# 파일 상단에 사용법 주석 필수 #}
{# 사용법: {% include "components/alert.html" with alert_type="alert-error" message="에러" %}
   필수: message
   선택: alert_type, extra_class
#}
{% if message %}
<div class="alert {{ alert_type|default:'' }} {{ extra_class }}" role="alert">
    <span>{{ message }}</span>
</div>
{% endif %}
```

**규칙:**
- 파라미터는 `with`로 전달 — 컨텍스트 변수에 의존하지 않음
- 필수/선택 파라미터를 주석에 명시
- `|default:''` 등으로 선택 파라미터 처리
- `{% url %}` 태그 사용 가능 (프로덕션에서는 정상 동작)

### 2. 패턴 라이브러리에 전시 추가

`templates/patterns/components/{name}/` 디렉토리를 만들고:

**{name}.html** — 모든 변형을 전시:
```html
<div class="space-y-4">
    <div>
        <p class="text-sm text-gray-500 mb-2 font-mono">alert-info</p>
        {% include "components/alert.html" with alert_type="alert-info" message="Info message." %}
    </div>
    <div>
        <p class="text-sm text-gray-500 mb-2 font-mono">alert-error</p>
        {% include "components/alert.html" with alert_type="alert-error" message="Error message." %}
    </div>
</div>
```

**{name}.yaml** — 최소한 name 필드:
```yaml
name: Alert
```

### 3. 프로덕션 템플릿에서 사용

```html
{% include "components/alert.html" with alert_type="alert-error" message=error_message %}
```

## 페이지 패턴 추가 절차

페이지 패턴은 `patterns/base_page.html`을 extends하고, `{% url %}` 대신 `#`을 사용한다.

```html
{% extends "patterns/base_page.html" %}

{% block nav %}
{# navbar 컴포넌트가 {% url %}을 사용하므로 패턴에서는 직접 마크업 #}
<nav class="bg-white shadow-sm">...</nav>
{% endblock %}

{% block content %}
<main>
    {# 컴포넌트는 동일하게 include #}
    {% include "components/form_field.html" with label="이메일" type="email" name="email" %}
</main>
{% endblock %}
```

**상태 변형**: 같은 페이지의 다른 상태(에러, 성공 등)는 별도 파일로 만든다.
- `login.html` + `login.yaml` — 기본 상태
- `login_error.html` + `login_error.yaml` — 에러 상태

## 패턴 라이브러리에서 {% url %} 처리

`{% url %}` 태그는 패턴 라이브러리에서 동작하지 않을 수 있다.

- **components/에서**: `{% url %}` 자유롭게 사용 (프로덕션 코드이므로)
- **patterns/에서**: URL이 필요한 곳은 `#`으로 대체하거나, 직접 마크업으로 작성

## 패턴 라이브러리 접속

- **URL**: `http://localhost:8000/pattern-library/`
- **dev 환경에서만** 활성화 (`pattern_library`가 dev INSTALLED_APPS에 있음)
- CSS 변경 후 `tailwindcss` 빌드 필요

## 주석 규칙 (중요)

Django 템플릿 주석 `{# #}`은 **반드시 한 줄 단위**로 작성한다.
여러 줄 주석 안에 `{% %}` 태그가 있으면 Django 파서가 실제 태그로 파싱하여 무한 재귀 등 치명적 오류가 발생한다.

```html
{# Good: 한 줄씩 분리 #}
{# 재사용 가능한 알림 컴포넌트 #}
{# 사용법: include "components/alert.html" with alert_type="alert-error" message="에러" #}
{# 필수: message / 선택: alert_type, extra_class #}

{# Bad: 여러 줄 주석 + 태그 포함 → 무한 재귀 발생 #}
{# 사용법: {% include "components/alert.html" with ... %}
   필수: message
#}
```

**규칙:**
- `{# #}` 주석은 한 줄에 열고 닫기
- 주석 안에 `{% %}` 태그 절대 금지 (파서가 실제 태그로 인식함)
- 사용법 설명 시 `{% %}` 대신 `include "..."` 등 평문으로 작성

## 주의사항

1. **컴포넌트 수정 = components/ 파일만 수정** — 패턴 라이브러리와 프로덕션에 자동 반영
2. **마크업 복붙 금지** — 항상 `{% include "components/..." %}`로 참조
3. **패턴 전시 템플릿에 변형 라벨 표시** — `<p class="text-sm text-gray-500 mb-2 font-mono">` 사용
4. **새 컴포넌트 = 패턴도 함께 추가** — 컴포넌트만 만들고 패턴 전시를 빠뜨리지 않기
