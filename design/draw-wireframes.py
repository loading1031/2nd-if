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
        button(796, 167, 122, "1화 ▾")
        button(930, 167, 138, "최근 30일 ▾")
        button(228, 218, 120, "읽기 흐름", True)
        button(358, 218, 186, "내 작품 유입 · I-02")
        button(554, 218, 178, "공용 합계 · I-02")
        button(890, 218, 178, "공개 설정 · I-03")
        for i, (n, v) in enumerate(
            [("읽기 시작", "2,714"), ("완독 판정", "1,936"), ("회차 이탈률", "22.0%"), ("분기 경유 합류", "184")]
        ):
            x = 228 + i * 214
            rect(x, 269, 198, 86)
            text(x + 14, 294, n, 13, MUTED)
            text(x + 14, 333, v, 28, bold=True)
        card(228, 374, 406, 232, "회차별 읽기", [])
        text(246, 433, "회차 선택             판정 완료 / 이탈률", 13, MUTED)
        for i, (chapter, value) in enumerate(
            [("1화", "1,000회 / 18.2%"), ("2화", "800회 / 22.5%"), ("3화", "681회 / 26.9%")]
        ):
            y = 447 + i * 46
            button(246, y, 114, chapter + " 보기 →", i == 0)
            text(384, y + 22, value, 13, MUTED)
        card(652, 374, 416, 232, "페이지 전환 시간 · 선택한 1화", [])
        for i, (n, v, count) in enumerate([("1쪽", 42, 756), ("2쪽", 29, 742), ("3쪽", 58, 736)]):
            y = 439 + i * 56
            text(670, y, n, 13, MUTED)
            rect(707, y - 11, 182, 7, BASE, BASE, 3)
            rect(707, y - 11, v * 3, 7, PRIMARY, PRIMARY, 3)
            text(912, y, f"{v}초 · {count}건", 12, MUTED)
        text(228, 641, "회차 행 선택 → 오른쪽 상세 갱신 · 유입/공개 설정 이동 시 작품·회차·기간 유지", 13, MUTED)
        text(228, 670, "판정 중 233회는 이탈률 제외 · 마지막 페이지에는 다음 전환 시간이 없습니다.", 13, MUTED)

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
            y = 218 + i * 64
            rect(228, y, 840, 54, BASE if i == 0 else "white", PRIMARY if i == 0 else LINE)
            text(248, y + 24, "●" if i == 0 else "○", 16, PRIMARY)
            text(278, y + 23, label, 15, bold=True)
            text(278, y + 44, desc, 13, MUTED)
        card(
            228,
            423,
            840,
            89,
            "초대한 계정만 선택 시 · 이메일 입력 / 초대",
            ["reader@example.com  ·  초대됨  ·  [초대 취소]"],
        )
        text(228, 553, "저장 전 · 변경 사항 있음 / 저장 중에는 중복 제출 방지", 13, MUTED)
        button(952, 532, 116, "설정 저장", True)
        rect(228, 586, 840, 118, BASE)
        text(244, 610, "보조 상태 · 입력 오류 / 저장 결과 / 권한", 14, bold=True)
        text(
            244,
            634,
            "초대 오류 예시: 이메일 형식을 확인하세요 / 이미 초대했습니다 / 본인은 초대할 수 없습니다",
            13,
            MUTED,
        )
        text(244, 658, "저장 성공: 저장됨 / 실패: 저장하지 못했습니다 [재시도] · 선택 범위·입력 유지", 13, MUTED)
        text(244, 682, "권한 없음: 변경·저장 불가 / 초대 철회: 다음 조회부터 적용", 13, MUTED)

    elif kind == "book-search":
        rect(228, 215, 644, 40)
        text(244, 241, "북부  ·  검색어 유지", 14, MUTED)
        button(886, 219, 182, "무료 이용 허용 ▾")
        button(228, 273, 208, "← 작품 설정집 · S-03")
        text(456, 295, "유리 정원 · 상세를 닫으면 검색어·필터·목록 위치 복원", 13, MUTED)
        for i, (name, creator) in enumerate(
            [("북부의 식물 도감", "나무그늘"), ("북부 왕국의 문장", "mono"), ("북부 도시의 소품", "윤슬")]
        ):
            x = 228 + i * 286
            rect(x, 325, 268, 292)
            image(x + 16, 341, 236, 101)
            text(x + 16, 471, name, 16, bold=True)
            text(x + 16, 500, creator, 13, MUTED)
            text(x + 16, 528, "이용 조건 · 버전 확인", 13, MUTED)
            button(x + 16, 560, 236, "상세 보기 → S-02")
        text(228, 654, "상세 취소 → 이 탐색 결과 · 작품 목록 복귀 후 재진입해도 탐색 조건 유지", 13, MUTED)
        text(228, 680, "무료 배포 여부와 작품의 상업 이용 허용은 별도 조건입니다.", 13, MUTED)

    elif kind == "book-detail":
        button(228, 211, 208, "← 탐색 결과 · S-01")
        text(456, 233, "검색어: 북부 · 무료 이용 필터 · 목록 위치 유지", 13, MUTED)
        card(
            228,
            259,
            506,
            122,
            "북부의 식물 도감",
            ["나무그늘 · 채택할 버전 v1.5", "무료 작품 이용 허용 · 설정집 전체 이용 권한"],
        )
        image(752, 259, 316, 122)
        card(
            228,
            399,
            840,
            123,
            "유리 정원에서 사용할 항목 · 2개 선택",
            ["☑ 월광초     ☑ 오래된 온실     ☐ 은빛 덩굴", "선택 항목과 버전을 채택 완료 후에도 유지합니다."],
        )
        button(228, 541, 208, "취소 · 탐색 결과로")
        button(826, 541, 242, "채택 후 목록으로 · S-03", True)
        rect(228, 592, 840, 112, BASE)
        text(244, 617, "채택 성공 상태: 유리 정원 · 북부의 식물 도감 v1.5 · 선택 항목 2개 유지", 13, bold=True)
        text(244, 643, "S-03에 채택 완료 표시 · 충돌은 채택을 막지 않고 별도 연결을 제안", 13, MUTED)
        button(842, 658, 208, "충돌 표현 연결 · S-05")

    elif kind == "book-list":
        button(900, 167, 168, "설정집 추가 · S-01")
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
            button(756, y + 35, 148, "표현 연결 · S-05")
            if new:
                button(918, y + 35, 132, new + " 업데이트")
            else:
                text(970, y + 56, "최신 버전", 13, MUTED)
        text(228, 625, "표현 연결: 유리 정원·선택한 설정집·고정 버전·복귀 위치를 S-05에 전달", 13, MUTED)
        text(228, 653, "채택 직후 상태: 추가된 행에 채택 완료·선택 항목 수 표시 (기존 목록과 구분)", 13, MUTED)
        text(228, 681, "현재 버전 유지 가능 · 다른 설정집과 다른 작품은 변경하지 않습니다.", 13, MUTED)

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
        text(228, 222, "유리 정원 · 진입: S-03 목록 또는 에디터 · 설정집·고정 버전 유지", 13, MUTED)
        rect(228, 240, 840, 62, BASE)
        text(248, 277, "그녀의 손끝에서 [은빛 잎]이 흔들렸다.  ·  1화 3쪽 · 이 표현만", 16)
        for i, (name, book) in enumerate(
            [("○ 월광초", "북부의 식물 도감 · v1.4"), ("○ 은빛 덩굴", "잊힌 왕국의 문장 · v2.1")]
        ):
            x = 228 + i * 430
            rect(x, 320, 410, 220)
            image(x + 18, 336, 374, 92)
            text(x + 18, 460, name, 18, bold=True)
            text(x + 18, 489, book, 14, MUTED)
            text(x + 18, 517, "사물 이름 · 색상 키 · 미리보기", 13, MUTED)
        button(228, 558, 208, "취소 · 진입 화면으로")
        button(884, 558, 184, "선택한 에셋 연결", True)
        rect(228, 608, 840, 96, BASE)
        text(244, 632, "저장 완료 상태: 연결됨 · 작품·설정집·버전·1화 3쪽·표현 위치 유지", 13, bold=True)
        text(244, 658, "목록 진입 → S-03의 해당 행 / 에디터 진입 → 같은 회차·쪽·표현으로 복귀", 13, MUTED)
        text(244, 684, "실패 시 선택 유지·재시도 / 취소 시 기존 매핑 유지", 13, MUTED)
        button(868, 665, 184, "진입 화면으로 복귀")

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
        text(245, 242, "유리 정원 · 1화 3쪽", 16, bold=True)
        text(245, 294, "온실의 문이 천천히 열렸다.", 20)
        text(245, 336, "그녀의 손끝에서", 20)
        button(245, 354, 250, "은빛 잎 · 이미지 열기", True)
        text(245, 424, "흔들렸다. 비는 그친 뒤였다.", 20)
        text(245, 472, "연결 표현을 탭 → 오른쪽 패널", 14, PRIMARY, True)
        text(245, 502, "닫기 → 같은 쪽·읽기 위치·표현으로", 14, MUTED)
        rect(652, 219, 396, 401)
        text(674, 251, "열린 오버레이 · 월광초", 18, bold=True)
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
            ("채택 완료 → 목록", "S-03 · 선택 항목 유지"),
            ("표현 연결 → 열람", "S-05 → R-01"),
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
