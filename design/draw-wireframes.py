from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent / "wireframes"
OUT.mkdir(exist_ok=True)
INK, MUTED, LINE, BASE, PRIMARY = "#25252b", "#72727c", "#dedee5", "#f7f7fa", "#422ad5"


def wire(code, title, kind):
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="760" viewBox="0 0 1120 760">',
        '<rect width="1120" height="760" fill="white"/>',
    ]

    def rect(x, y, w, h, fill="white", stroke=LINE, r=10):
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>')

    def text(x, y, s, size=16, fill=INK, bold=False):
        svg.append(
            f'<text x="{x}" y="{y}" font-family="Apple SD Gothic Neo, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{fill}">{escape(s)}</text>'
        )

    def line(x1, y1, x2, y2):
        svg.append(
            f'<path d="M{x1} {y1}H{x2}" stroke="{LINE}"/>'
            if y1 == y2
            else f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{LINE}"/>'
        )

    def button(x, y, w, s, primary=False):
        rect(x, y, w, 32, PRIMARY if primary else "white", PRIMARY if primary else LINE, 6)
        text(x + 12, y + 21, s, 13, "white" if primary else INK, True)

    def card(x, y, w, h, name, lines):
        rect(x, y, w, h)
        text(x + 18, y + 29, name, 17, bold=True)
        for i, s in enumerate(lines):
            text(x + 18, y + 60 + i * 27, s, 14, MUTED)

    def image(x, y, w, h, label="렌더 이미지 영역"):
        rect(x, y, w, h, BASE)
        line(x + 12, y + 12, x + w - 12, y + h - 12)
        line(x + w - 12, y + 12, x + 12, y + h - 12)
        rect(x + 14, y + h / 2 - 14, w - 28, 29, BASE, BASE, 3)
        text(x + 24, y + h / 2 + 6, label, 13, MUTED)

    text(28, 36, code, 14, PRIMARY, True)
    text(93, 36, title, 24, bold=True)
    text(28, 64, "구조 와이어프레임 · 예시 콘텐츠 · 배치 제안", 13, MUTED)
    rect(28, 94, 1064, 632)
    text(50, 128, "2nd-if", 18, bold=True)
    text(230, 128, "내 설정집" if kind in ("creator", "publish") else "유리 정원", 14, MUTED)
    text(1010, 128, "독자" if kind == "reader" else ("제작자" if kind in ("creator", "publish") else "작가"), 13, MUTED)
    line(28, 148, 1092, 148)
    line(204, 148, 204, 726)
    menu = (
        ["목차", "읽은 타임라인", "독서 설정"]
        if kind == "reader"
        else (
            ["내 설정집", "항목·에셋 편집", "버전 발행", "이용 조건"]
            if kind in ("creator", "publish")
            else ["작품 관리", "독서 인사이트", "설정집과 에셋", "지표 공개 설정"]
        )
    )
    for i, s in enumerate(menu):
        if (
            (kind.startswith("insight") and i == 1)
            or (kind.startswith("book") and i == 2)
            or (kind == "sharing" and i == 3)
        ):
            rect(40, 172 + i * 46, 152, 36, BASE, BASE, 6)
        text(54, 196 + i * 46, s, 13, MUTED)
    text(228, 190, title, 21, bold=True)
    if kind == "home":
        text(228, 225, "현재 선택한 작품의 도구로 이동합니다.", 14, MUTED)
        card(
            228, 252, 398, 194, "독서 인사이트", ["회차별 읽기 · 페이지 전환 시간", "내 작품 유입 · 공용 컴포넌트 합계"]
        )
        button(248, 390, 144, "인사이트 보기", True)
        card(644, 252, 424, 194, "설정집과 에셋", ["작품에 채택한 버전 관리", "표현과 에셋 연결 · 업데이트 선택"])
        button(664, 390, 148, "설정집 관리", True)
        card(
            228,
            468,
            840,
            142,
            "권한을 구분합니다",
            ["작품 공개: 공개 / 링크 공개 / 비공개", "지표 공개: 작가만 / 초대한 계정만 / 전체 공개"],
        )
    elif kind == "insight":
        button(796, 167, 122, "전체 회차 ▾")
        button(930, 167, 138, "최근 30일 ▾")
        for i, (n, v) in enumerate(
            [("읽기 시작", "2,714"), ("완독 판정", "1,936"), ("회차 이탈률", "22.0%"), ("분기 경유 합류", "184")]
        ):
            x = 228 + i * 214
            rect(x, 221, 198, 104)
            text(x + 14, 248, n, 13, MUTED)
            text(x + 14, 290, v, 28, bold=True)
        card(
            228,
            347,
            406,
            259,
            "회차별 읽기",
            [
                "회차          판정 완료       이탈률",
                "1화           1,000회          18.2%",
                "2화             800회          22.5%",
                "3화             681회          26.9%",
            ],
        )
        card(652, 347, 416, 259, "페이지 전환 시간 · 1화", [])
        for i, (n, v, count) in enumerate([("1쪽", 42, 756), ("2쪽", 29, 742), ("3쪽", 58, 736)]):
            y = 410 + i * 56
            text(670, y, n, 13, MUTED)
            rect(707, y - 11, 182, 7, BASE, BASE, 3)
            rect(707, y - 11, v * 3, 7, PRIMARY, PRIMARY, 3)
            text(912, y, f"{v}초 · {count}건", 12, MUTED)
        text(228, 641, "판정 중 233회는 이탈률에서 제외 · 마지막 페이지의 전환 시간은 집계하지 않습니다.", 13, MUTED)
    elif kind == "insight-traffic":
        button(228, 216, 132, "내 작품 유입", True)
        button(370, 216, 144, "공용 컴포넌트")
        card(
            228,
            268,
            840,
            210,
            "내 작품으로 들어온 경로",
            [
                "경로                              클릭                  읽기 시작",
                "홈 추천                         412                    312",
                "작가 프로필                   226                    184",
                "검색 결과                      180                    123",
            ],
        )
        card(
            228, 496, 840, 116, "분기 경유 원작 합류", ["모든 분기 합계: 184  ·  분기별 내부 지표는 제공하지 않습니다."]
        )
        text(228, 647, "공용 탭: 목적지 작품별 숫자를 제거한 플랫폼 전체 합계만 표시합니다.", 13, MUTED)
    elif kind == "sharing":
        for i, (label, desc) in enumerate(
            [
                ("작가만", "기본값 · 작가 본인만 집계 지표 열람"),
                ("초대한 계정만", "초대는 작품 읽기·편집 권한을 부여하지 않습니다."),
                ("전체 공개", "누구나 이 작품의 집계 지표 열람"),
            ]
        ):
            y = 218 + i * 91
            rect(228, y, 840, 76, BASE if i == 0 else "white", PRIMARY if i == 0 else LINE)
            text(248, y + 28, "●" if i == 0 else "○", 16, PRIMARY)
            text(278, y + 28, label, 16, bold=True)
            text(278, y + 54, desc, 13, MUTED)
        card(228, 512, 840, 90, "초대한 계정만 선택하면 표시", ["이메일 입력 / 초대 계정 목록 / 초대 취소"])
        text(228, 643, "공개 범위 변경·초대 철회는 다음 조회부터 적용", 13, MUTED)
        button(952, 625, 116, "설정 저장", True)
    elif kind == "book-search":
        rect(228, 215, 644, 40)
        text(244, 241, "설정집 이름 · 제작자 검색", 14, MUTED)
        button(886, 219, 182, "이용 조건 필터 ▾")
        for i, (name, creator) in enumerate(
            [("북부의 식물 도감", "나무그늘"), ("잊힌 왕국의 문장", "mono"), ("비 오는 도시의 소품", "윤슬")]
        ):
            x = 228 + i * 286
            rect(x, 279, 268, 326)
            image(x + 16, 295, 236, 128)
            text(x + 16, 454, name, 16, bold=True)
            text(x + 16, 483, creator, 13, MUTED)
            text(x + 16, 511, "이용 조건 · 버전 확인", 13, MUTED)
            button(x + 16, 548, 236, "상세 보기")
        text(228, 644, "무료 배포 여부와 작품의 상업 이용 허용은 별도 조건입니다.", 13, MUTED)
    elif kind == "book-detail":
        card(
            228,
            220,
            506,
            164,
            "북부의 식물 도감",
            ["나무그늘 · 채택할 버전 v1.5", "무료 작품 이용 허용", "설정집 전체 이용 권한을 확인합니다."],
        )
        image(752, 220, 316, 164)
        card(
            228,
            403,
            840,
            187,
            "작품에서 사용할 항목",
            [
                "☑ 월광초     ☑ 오래된 온실     ☐ 은빛 덩굴",
                "선택한 항목의 표현 연결은 작품에서 개별 관리",
                "겹치는 용어: 경고 후 표현 매핑으로 이동",
            ],
        )
        button(847, 616, 221, "이 버전을 작품에 채택", True)
    elif kind == "book-list":
        button(940, 167, 128, "설정집 추가")
        for i, (name, v, new) in enumerate(
            [
                ("북부의 식물 도감", "v1.4", "v1.5"),
                ("잊힌 왕국의 문장", "v2.1", None),
                ("비 오는 도시의 소품", "v1.0", "v1.1"),
            ]
        ):
            y = 225 + i * 119
            rect(228, y, 840, 103)
            image(244, y + 18, 67, 67, "그림")
            text(330, y + 34, name, 17, bold=True)
            text(330, y + 62, v + " 사용 중 · 제작자 · 이용 조건", 13, MUTED)
            if new:
                button(918, y + 35, 132, new + " 업데이트")
            else:
                text(970, y + 56, "최신 버전", 13, MUTED)
        text(228, 625, "업데이트하지 않으면 현재 버전 유지 · 다른 설정집과 다른 작품은 변경하지 않습니다.", 13, MUTED)
    elif kind == "book-update":
        rect(326, 215, 650, 430)
        text(350, 252, "북부의 식물 도감 · 버전 검토", 21, bold=True)
        text(930, 251, "×", 20, MUTED)
        card(350, 279, 289, 100, "현재 v1.4", [])
        card(659, 279, 291, 100, "새 버전 v1.5", [])
        text(350, 416, "추가 3개 · 이미지 개선 2개", 16, bold=True)
        text(350, 448, "라이선스: 무료 작품 이용 허용 → 동일 조건", 14, MUTED)
        text(350, 479, "기존 표현 매핑에 영향을 주는 항목을 확인합니다.", 14, MUTED)
        text(350, 518, "이 작품의 이 설정집만 변경됩니다.", 14, MUTED)
        button(550, 580, 153, "현재 버전 유지")
        button(718, 580, 232, "이 설정집만 업데이트", True)
    elif kind == "book-map":
        rect(228, 219, 840, 69, BASE)
        text(248, 260, "그녀의 손끝에서 [은빛 잎]이 흔들렸다.  ·  1화 3쪽", 17)
        for i, (name, book) in enumerate(
            [("○ 월광초", "북부의 식물 도감 · v1.4"), ("○ 은빛 덩굴", "잊힌 왕국의 문장 · v2.1")]
        ):
            x = 228 + i * 430
            rect(x, 307, 410, 268)
            image(x + 18, 324, 374, 123)
            text(x + 18, 479, name, 18, bold=True)
            text(x + 18, 508, book, 14, MUTED)
            text(x + 18, 538, "사물 이름 · 색상 키 · 미리보기", 13, MUTED)
        text(228, 625, "미지정 충돌 표현에는 에셋을 자동 표시하지 않습니다.", 13, MUTED)
        button(884, 605, 184, "선택한 에셋 연결", True)
    elif kind == "creator":
        card(228, 218, 220, 380, "항목 목록", ["월광초", "오래된 온실", "은빛 덩굴", "＋ 항목 추가"])
        card(
            466,
            218,
            602,
            380,
            "월광초 · 새 버전 초안",
            [
                "사용자 레이블  [식물]",
                "설명               [                              ]",
                "사물 이름       [월광초]",
                "배경 이름       [해당 없음]",
                "색상 별칭       [은백색 → 표준값]",
                "흑백 기본 이미지 필수 / 색상 변형 선택",
            ],
        )
        button(800, 622, 118, "초안 저장")
        button(930, 622, 138, "발행 검토", True)
    elif kind == "publish":
        card(
            228,
            219,
            840,
            128,
            "새 버전 발행",
            ["버전 v1.5    ·    변경 설명 입력", "항목 46개 / 흑백 이미지 확인 / 색상 변형 검토"],
        )
        card(
            228,
            365,
            840,
            155,
            "이용 조건 확인",
            [
                "무료 배포와 상업 이용 허용은 별도",
                "기존 v1.4의 라이선스는 변경하지 않습니다.",
                "새 버전은 기존 작품에 자동 적용되지 않습니다.",
            ],
        )
        text(228, 574, "중복 버전 · 필수 이미지 누락 · 업로드 미완료를 먼저 확인", 14, MUTED)
        button(760, 611, 142, "초안으로 복귀")
        button(916, 611, 152, "새 버전 발행", True)
    elif kind == "reader":
        text(245, 242, "유리 정원 · 1화", 16, bold=True)
        for i, s in enumerate(
            [
                "온실의 문이 천천히 열렸다.",
                "그녀의 손끝에서 은빛 잎이",
                "흔들렸다. 비는 그친 뒤였다.",
                "읽던 본문은 같은 위치에 남는다.",
            ]
        ):
            text(245, 302 + i * 53, s, 20)
        rect(652, 219, 396, 401)
        text(674, 251, "월광초", 18, bold=True)
        text(1010, 251, "×", 18, MUTED)
        image(674, 271, 352, 233)
        text(674, 539, "북부의 식물 도감 · 작가가 연결", 13, MUTED)
        button(674, 565, 352, "닫고 읽기 계속")
        text(245, 662, "이미지 실패 시에도 본문 읽기 계속 · 별도 설정집 구매 없음", 13, MUTED)
    svg.append("</svg>")
    (OUT / f"{code}.svg").write_text("\n".join(svg).replace("▾", "선택").replace("☑", "[선택]").replace("☐", "[ ]"))


PAGES = [
    ("A-01", "작품 관리 진입", "home"),
    ("I-01", "독서 인사이트", "insight"),
    ("I-02", "내 작품 유입·공용 합계", "insight-traffic"),
    ("I-03", "지표 공개·초대", "sharing"),
    ("S-01", "설정집 탐색", "book-search"),
    ("S-02", "설정집 상세·채택", "book-detail"),
    ("S-03", "작품의 설정집 목록", "book-list"),
    ("S-04", "설정집 버전 검토", "book-update"),
    ("S-05", "표현·에셋 매핑", "book-map"),
    ("C-01", "설정집 항목·에셋 편집", "creator"),
    ("C-02", "설정집 버전 발행", "publish"),
    ("R-01", "독서 중 에셋 열람", "reader"),
]
for code, title, kind in PAGES:
    wire(code, title, kind)

ia = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="800" viewBox="0 0 1120 800"><defs><marker id="a" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="none" stroke="#9999a7"/></marker></defs><rect width="1120" height="800" fill="white"/>'
]


def it(x, y, s, size=16, bold=False, color=INK):
    ia.append(
        f'<text x="{x}" y="{y}" font-family="Apple SD Gothic Neo, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(s)}</text>'
    )


it(34, 43, "2nd-if · 전체 정보 구조와 주요 이동 흐름", 26, True)
it(34, 75, "화면 설계 #26 · 화면 코드는 왼쪽 문서 탭과 연결됩니다. · 배치 제안", 14, color=MUTED)
lanes = [
    (
        "1 · 작가의 관찰",
        [
            ("작품 관리", "A-01 · 현재 작품"),
            ("독서 인사이트", "I-01 · 읽기 흐름"),
            ("작품·공용 유입", "I-02 · 합계 경계"),
            ("지표 공개·초대", "I-03 · 기본 작가만"),
        ],
    ),
    (
        "2 · 설정집 채택",
        [
            ("채택 목록", "S-03 · 설정집 추가"),
            ("탐색 → 상세", "S-01 / S-02"),
            ("표현·에셋 매핑", "S-05 · 문맥별 연결"),
            ("독자 에셋 열람", "R-01 · 본문으로 복귀"),
        ],
    ),
    (
        "3 · 버전 업데이트",
        [
            ("개별 업데이트", "S-03 · v1.5 버튼"),
            ("변경·조건 검토", "S-04 · 해당 설정집"),
            ("현재 버전 유지", "또는 신규 버전 적용"),
            ("선택한 버전 고정", "다른 설정집·작품 유지"),
        ],
    ),
    (
        "4 · 제작자의 발행",
        [
            ("항목·에셋 편집", "C-01 · 새 버전 초안"),
            ("필수 이미지·키", "흑백 기본형 검토"),
            ("새 버전 발행", "C-02 · 라이선스 고정"),
            ("작가의 선택 대기", "기존 버전 자동 변경 없음"),
        ],
    ),
]
for row, (name, nodes) in enumerate(lanes):
    y = 116 + row * 148
    ia.append(f'<rect x="30" y="{y}" width="1060" height="130" rx="12" fill="{BASE}" stroke="{LINE}"/>')
    it(48, y + 36, name, 16, True)
    for col, (head, sub) in enumerate(nodes):
        x = 221 + col * 214
        ia.append(f'<rect x="{x}" y="{y + 23}" width="194" height="82" rx="9" fill="white" stroke="{LINE}"/>')
        it(x + 13, y + 55, head, 16, True)
        it(x + 13, y + 81, sub, 12, color=MUTED)
        if col < 3:
            ia.append(f'<path d="M{x + 194} {y + 65}h19" stroke="#9999a7" marker-end="url(#a)"/>')
it(34, 750, "권한 경계: 작품 열람·편집 / 설정집 재사용 라이선스 / 집계 지표 공개를 각각 판정", 15, True)
it(34, 778, "별도 범위: 작품 공식 설정·팬 설정집 #30 · 동적 리더·자동 Blender 파이프라인 #15/#18 보류", 13, color=MUTED)
ia.append("</svg>")
(OUT / "IA-00.svg").write_text("\n".join(ia))

print(f"Created {len(PAGES)} screen SVGs and IA diagram at {OUT}")
