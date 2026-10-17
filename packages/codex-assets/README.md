# Django 도감 에셋

프로젝트 내부의 독립 설치 패키지. 데이터베이스와 HTMX 의존성이 없다.
현재 Game-icons SVG 4,180개, 분류·출처 목록, 공식 8종 팔레트를 포함한다.
직접 제작 SVG와 작품별 한국어 단어 CSV는 아직 프로젝트 자료로 관리한다.

## 설치

저장소 루트에서 `uv sync`로 로컬 패키지를 설치한다. 다른 Django 프로젝트에서는
`uv add /path/to/packages/codex-assets`로 설치할 수 있다.

`INSTALLED_APPS`에 `codex_assets.apps.CodexAssetsConfig`를 등록한다.
앱의 static과 templates는 Django가 탐색한다. 운영에서는 `collectstatic`을 사용한다.

```django
{% load static codex_assets %}
<link rel="stylesheet" href="{% static 'assets/game-icons/components.css' %}">
{% codex_asset "delapouite/brute" color="파란색" label="푸른 브루트" size=96 %}
```

`palette="solarized"`로 유사색 탐색 범위를 제한하고 `background=True`로
팔레트 배경을 표시할 수 있다. 미지정/유효하지 않은 색상은 흑백으로 표시한다.
존재하지 않는 에셋 ID는 KeyError로 드러내므로 호출 전에 유효한 ID를 선택해야 한다.
CSS는 페이지에 한 번 로드한다. HTMX로 교체되는 조각 안에서도 같은 태그를 사용한다.
엄격한 CSP에서 inline style을 금지하는 경우 별도 스타일 전달 방식이 필요하다.

```python
from codex_assets import get_asset, list_assets, nearest_color

asset = get_asset("delapouite/brute")
appearance = nearest_color("파란색")
candidates = list_assets(topic="creatures/monsters", query="brute")
```

`nearest_color`는 requestedColor/paletteId/foreground/background/distance를 반환한다.
작품별 승인·저장·수집 정책은 이 패키지가 담당하지 않는다.
저작자 정보는 `get_asset()` 결과의 author/source_url/license/license_url로 표시한다.
단어 매핑을 저장할 때 고유 ID를 사용하고 분류 경로를 식별자로 사용하지 않는다.

## 출처와 배포

코드와 아이콘의 라이선스는 별개다. 아이콘의 저작자·라이선스와 배색 변경 표시를
보존해야 한다. `src/codex_assets/static/assets/game-icons/LICENSE.txt` 및
`credits.html`, `catalog.json`에 원본 고지와 개별 정보를 포함한다.
공개 패키지 배포 시 자체 코드의 라이선스와 이름 소유권은 별도로 확정한다.

`uv build packages/codex-assets`로 wheel/sdist를 만들 수 있다.
이 패키지는 아직 PyPI에 게시하지 않았다. JavaScript 팔레트 갤러리는 개발용 탐색기로
함께 제공하며 Django 태그 렌더링에는 JavaScript가 필요 없다.
