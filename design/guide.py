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
    components = """<h1>컴포넌트</h1><p>프로젝트 코드가 기준이다. 화면의 구성 요소를 실제 구현에 연결한다.</p>
<table><thead><tr><th>요소</th><th>코드 기준</th><th>쓰임새</th></tr></thead><tbody>
<tr><td>버튼</td><td>daisyUI btn / btn-sm / btn-outline / btn-primary</td><td>반복 행은 작은 우측 버튼, 최종 확인은 primary</td></tr>
<tr><td>카드·표·탭</td><td>card / stat / table / tabs / badge</td><td>인사이트, 설정집 목록</td></tr>
<tr><td>공개 범위·입력</td><td>radio / input / select</td><td>공개 설정, 초대, 제작자 편집</td></tr>
<tr><td>모달</td><td>modal / modal-box / modal-action</td><td>버전 검토, 에셋 선택</td></tr>
<tr><td>공유 알림·폼</td><td>components/alert.html, components/form_field.html</td><td>집계 지연, 권한 안내, 계정 초대</td></tr></tbody></table>
<h2>재사용 원칙</h2><p>공유 컴포넌트는 server/templates/components/에 정의하고 패턴 라이브러리와 제품 화면이 같은 include를 참조한다. 여기의 SVG는 구조 검토용이고 별도 제품 동작 시안은 실제 Tailwind/daisyUI 패키지로 빌드된다.</p>"""
    tokens = """<h1>토큰</h1><p>코드 기준 · daisyUI 5.5.14의 light 테마. 출처: server/static/css/input.css, node_modules/daisyui/theme/light/object.js</p>
<table><thead><tr><th>토큰</th><th>값</th><th>용도</th></tr></thead><tbody>
<tr><td>base-100</td><td>oklch(100% 0 0)</td><td>화면·카드 바탕</td></tr>
<tr><td>base-200 / base-300</td><td>oklch(98% 0 0) / oklch(95% 0 0)</td><td>주변 바탕·구분선</td></tr>
<tr><td>base-content</td><td>oklch(21% 0.006 285.885)</td><td>기본 글자</td></tr>
<tr><td>primary</td><td>oklch(45% 0.24 277.023)</td><td>주요 행동</td></tr>
<tr><td>radius-field / radius-box</td><td>0.25rem / 0.5rem</td><td>필드·박스</td></tr>
<tr><td>border</td><td>1px</td><td>기본 경계선</td></tr></tbody></table>
<p>실제 색과 컴포넌트는 코드가 기준이다. SVG 와이어프레임은 구조와 배치를 전달하며 최종 스타일의 픽셀 일치를 보증하지 않는다.</p>"""
    for name, body in [("components", components), ("tokens", tokens)]:
        sections.append(f'<section id="{name}" data-guide-page hidden>{style_body(body)}</section>')
    html = """<!doctype html><html lang="ko" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>2nd-if · #26 화면 설계서</title><link rel="stylesheet" href="ui.css"><script src="app.js" defer></script></head>
<body class="min-h-screen bg-base-200 text-base-content antialiased"><div class="grid min-h-screen lg:grid-cols-[264px_minmax(0,1fr)]">
<aside class="border-b border-base-300 bg-base-100 lg:sticky lg:top-0 lg:h-screen lg:overflow-y-auto lg:border-r lg:border-b-0">
<div class="border-b border-base-300 p-5"><p class="text-xs font-semibold text-primary">2nd-if / DESIGN</p><h1 class="mt-2 text-lg font-bold">#26 화면 설계서</h1><p class="mt-2 text-xs leading-relaxed text-base-content/50">전체 IA → 화면 설명 → 와이어프레임<br>검토 초안 · 2026-10-17</p></div>
<nav aria-label="화면 설계 문서"><ul class="menu w-full p-3">NAV</ul></nav></aside>
<main class="min-w-0"><header class="flex flex-wrap items-center justify-between gap-3 border-b border-base-300 bg-base-100 px-5 py-4 lg:px-8"><p id="guide-crumb" class="text-xs text-base-content/60">화면 / 전체 IA</p><a class="btn btn-ghost btn-xs" href="prototype.html#insights" target="_blank" rel="noopener">제품 동작 시안 ↗</a></header>
<div class="max-w-6xl mx-auto p-5 lg:p-8"><div class="alert mb-6 text-xs shadow-none">이 페이지는 화면을 검토하는 설계 문서입니다. 이미지·수치는 예시이며 최종 디자인 승인은 아직 받지 않았습니다.</div>SECTIONS</div></main></div></body></html>"""
    html = html.replace("NAV", "".join(nav)).replace("SECTIONS", "".join(sections))
    (root / "index.html").write_text(html)
    print("Built IA + 12 screen wireframes + component/token references")


if __name__ == "__main__":
    main()
