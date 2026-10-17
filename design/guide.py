"""Build the screen-design review document from its authored page data."""

import json
from html import escape
from pathlib import Path


def style_body(content: str) -> str:
    replacements = {
        "<h1>": '<h1 class="mb-3 text-2xl font-bold tracking-tight">',
        "<h2>": '<h2 class="mt-8 mb-3 border-b border-base-300 pb-2 text-lg font-semibold">',
        "<h3>": '<h3 class="mt-5 mb-2 text-sm font-semibold">',
        "<p>": '<p class="my-3 text-sm leading-relaxed text-base-content/70">',
        "<ul>": '<ul class="list-disc space-y-2 pl-5 text-sm leading-relaxed text-base-content/70">',
        "<table>": '<div class="my-4 overflow-x-auto rounded-box border border-base-300"><table class="table table-sm">',
        "</table>": "</table></div>",
        "<a href=": '<a class="link link-primary" href=',
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    return content


def picture(code: str, label: str) -> str:
    svg = (Path(__file__).resolve().parent / "wireframes" / f"{code}.svg").read_text()
    svg = svg.replace(
        "<svg ",
        f'<svg role="img" aria-label="{escape(label, quote=True)} 구조 와이어프레임" '
        'style="display:block;width:100%;min-width:1120px;height:auto" ',
        1,
    )
    return (
        '<figure class="my-5 overflow-hidden rounded-box border border-base-300 bg-base-100">'
        '<div style="overflow-x:auto">' + svg + "</div>"
        '<figcaption class="border-t border-base-300 px-4 py-3 text-xs leading-relaxed text-base-content/50">'
        "SVG 구조 와이어프레임 · 배치 제안 · 좁은 화면에서는 가로로 이동해 확인"
        f' · <a class="link" href="wireframes/{code}.svg" target="_blank" rel="noopener">SVG 원본 보기 ↗</a>'
        "</figcaption></figure>"
    )


def main() -> None:
    root = Path(__file__).resolve().parent
    data = json.loads((root / "pages.json").read_text())
    nav = ['<li><a href="#overview" data-guide-nav="overview">화면 · 전체 IA</a></li>']
    sections = []
    overview = data["overviewHtml"].replace(
        "와이어프레임은 표와 영역으로 구성한 구조 검토용 초안이다.",
        "와이어프레임은 SVG로 그린 구조 검토용 초안이다. 실제 Tailwind/daisyUI 렌더와 구분한다.",
    )
    overview = overview.replace("<h2>정보 구조 (IA)</h2>", "<h2>정보 구조 (IA)</h2>" + picture("IA-00", "전체 IA"))
    sections.append('<section id="overview" data-guide-page>' + style_body(overview) + "</section>")
    groups = {"A": "작품 관리", "I": "작가 인사이트", "S": "설정집 채택", "C": "설정집 제작", "R": "독자 열람"}
    previous = None
    for page in data["pages"]:
        code, title = page["id"], page["title"]
        group = code[0]
        if group != previous:
            nav.append(f'<li class="menu-title mt-3 text-xs">{groups[group]}</li>')
            previous = group
        nav.append(f'<li><a href="#{code}" data-guide-nav="{code}">{code} {escape(title)}</a></li>')
        body = page["html"].replace(page["wire"], picture(code, title))
        sections.append(f'<section id="{code}" data-guide-page hidden>{style_body(body)}</section>')
    nav.extend(
        [
            '<li class="menu-title mt-3 text-xs">컴포넌트 · 코드 기준</li>',
            '<li><a href="#components" data-guide-nav="components">컴포넌트 목록</a></li>',
            '<li><a href="#tokens" data-guide-nav="tokens">토큰</a></li>',
        ]
    )
    catalog = "http://localhost:8000/pattern-library/pattern/"
    components = """<h1>공통 컴포넌트</h1><p>전시는 Django 패턴 라이브러리에서 관리한다. 각 항목에서 실제 컴포넌트·입력 옵션·상태·원본 사용법을 확인한다. 화면 구조 승인 기준은 PR #34의 c74c536이며 IA와 흐름은 유지한다.</p><ul>"""
    component_names = {
        "author_metric_card": "지표 카드",
        "author_episode_select": "회차 선택",
        "author_episode_row": "회차 판정 행",
        "author_page_time": "페이지 전환 시간",
        "author_visibility_option": "지표 공개 범위",
        "author_invite_row": "초대 계정 행",
        "author_setting_book_row": "설정집 행·버전 버튼",
        "author_setting_update_dialog": "버전 비교·유지·적용 모달",
        "author_asset_candidate": "표현·SVG 후보 카드",
        "author_state_panel": "조회 상태 패널",
        "author_state_notice": "집계 지연·저장 결과",
        "form_field": "입력·오류·비활성 (기존 컴포넌트)",
        "alert": "공통 알림 (기존 컴포넌트)",
    }
    for name, title in component_names.items():
        components += (
            f'<li><a href="{catalog}patterns/components/{name}/{name}.html">{title}</a>'
            f' · <a href="../server/templates/components/{name}.html">공유 원본</a></li>'
        )
    components += "</ul><p>패턴 라이브러리와 기존 동작 시안은 같은 Django include와 서비스 CSS 원본을 사용한다. 예시 데이터와 모의 저장은 실제 API·권한 처리를 뜻하지 않는다. 실행 방법은 design/README.md를 참조한다.</p>"
    tokens = f"""<h1>디자인 토큰</h1><p>테마 원본은 <a href="../server/static/css/input.css">서비스 CSS 진입점</a>에서 불러오는 Tailwind CSS·daisyUI light다. 별도 토큰 값을 이 문서에 복제하지 않는다.</p>
<p><a href="{catalog}patterns/tokens/theme/theme.html">패턴 라이브러리에서 실제 토큰 값·용도 보기</a></p><p>카탈로그는 현재 렌더된 CSS 변수를 읽어 색·간격·타이포·모서리를 표시한다. SVG 팔레트는 에셋 표현 옵션으로 구분한다. SVG 와이어프레임은 승인된 구조와 배치 기준이다.</p>"""
    for name, body in [("components", components), ("tokens", tokens)]:
        sections.append(f'<section id="{name}" data-guide-page hidden>{style_body(body)}</section>')
    html = """<!doctype html><html lang="ko" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>2nd-if · #31 작가 도구 설계서</title><link rel="stylesheet" href="../server/static/css/output.css"><script src="app.js" defer></script></head>
<body class="min-h-screen bg-base-200 text-base-content antialiased"><div class="grid min-h-screen lg:grid-cols-[264px_minmax(0,1fr)]">
<aside class="border-b border-base-300 bg-base-100 lg:sticky lg:top-0 lg:h-screen lg:overflow-y-auto lg:border-r lg:border-b-0">
<div class="border-b border-base-300 p-5"><p class="text-xs font-semibold text-primary">2nd-if / DESIGN</p><h1 class="mt-2 text-lg font-bold">#31 작가 도구 설계서</h1><p class="mt-2 text-xs leading-relaxed text-base-content/50">승인된 화면 흐름 → 화면 설명 → 와이어프레임<br>PR #34 병합 · 2026-10-17</p></div>
<nav aria-label="화면 설계 문서"><ul class="menu w-full p-3">NAV</ul></nav></aside>
<main class="min-w-0"><header class="flex flex-wrap items-center justify-between gap-3 border-b border-base-300 bg-base-100 px-5 py-4 lg:px-8"><p id="guide-crumb" class="text-xs text-base-content/60">화면 / 전체 IA</p><a class="btn btn-ghost btn-xs" href="prototype.html#insights" target="_blank" rel="noopener">제품 동작 시안 ↗</a></header>
<div class="max-w-6xl mx-auto p-5 lg:p-8"><div class="alert mb-6 text-xs shadow-none">화면 IA와 흐름은 PR #34에서 승인됐습니다. 이미지·수치는 예시이며 서버 저장, 분석 집계, 실제 권한 처리는 구현 범위에 포함하지 않습니다.</div>SECTIONS</div></main></div></body></html>"""
    html = html.replace("NAV", "".join(nav)).replace("SECTIONS", "".join(sections))
    (root / "index.html").write_text(html)
    print("Built IA + 12 screen wireframes + component/token references")


if __name__ == "__main__":
    main()
