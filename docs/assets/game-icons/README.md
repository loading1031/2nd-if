# Game-icons 주제별 목록

공식 검정/투명 배경 묶음에서 SVG **4,180개**를 받았다. SVG 바이트를 수정하지 않았으며 원본 저작자·출처·라이선스·SHA-256을 보관한다.

[갤러리](../../../packages/codex-assets/src/codex_assets/static/assets/game-icons/gallery.html) · [전체 CSV](catalog.csv) · [저작자 표시](ATTRIBUTION.md) · [다운로드 기록](provenance.json)

## 분류 방식

- 파일 위치는 `packages/codex-assets/src/codex_assets/static/assets/game-icons/<대표 주제>/<저작자>/<아이콘>.svg`다.
- 공식 태그를 기준으로 여러 주제에 연결하되, 실제 SVG 파일은 대표 주제에 한 번만 보관한다.
- 분류가 겹치므로 주제별 개수를 더하면 전체 아이콘 수보다 커진다.
- 장르 목록은 탐색 후보이며 한국어 단어와의 최종 매핑이 아니다. 기존 300개 단어의 매핑은 보존했다.
- 파일을 받았다는 사실과 도감 사용에 적합하다는 판단은 구분한다. 아직 개별 도상 4,180개를 모두 시각 검토한 것은 아니다.

## 주제별 개수

| 분류 | 대표 폴더의 파일 수 | 전체 참조 수 |
|---|---:|---:|
| [장신구·보석](topics/items/jewelry.csv) | 54 | 54 |
| [무기·방패](topics/items/weapons.csv) | 565 | 566 |
| [방어구·의복](topics/items/armor-clothing.csv) | 296 | 308 |
| [약병·액체·연금술](topics/items/potions-containers.csv) | 333 | 361 |
| [몬스터·환수](topics/creatures/monsters.csv) | 118 | 122 |
| [판타지 인물](topics/creatures/people.csv) | 7 | 29 |
| [동물·곤충](topics/creatures/animals.csv) | 400 | 482 |
| [신체·해부](topics/body/anatomy.csv) | 437 | 695 |
| [교통·기계](topics/technology/transport.csv) | 281 | 327 |
| [식물·약재 후보](topics/nature/plants.csv) | 169 | 274 |
| [음식·주방](topics/items/food-kitchen.csv) | 128 | 239 |
| [건축·장소](topics/places/architecture.csv) | 179 | 247 |
| [생활·도구·책](topics/items/household-tools.csv) | 271 | 479 |
| [자연물·현상](topics/nature/elements-landscape.csv) | 313 | 806 |
| [놀이·음악·문화](topics/culture/games-arts.csv) | 276 | 554 |
| [역사·문명](topics/culture/history.csv) | 16 | 534 |
| [특정 작품·SF](topics/culture/fiction.csv) | 1 | 119 |
| [언데드 관련물](topics/themes/undead.csv) | 0 | 48 |
| [상징·상태·기호](topics/symbols/interface.csv) | 334 | 1066 |
| [공식 태그 미확인](topics/review/untagged.csv) | 2 | 2 |

## 장르 후보

| 장르 | 후보 수 |
|---|---:|
| [무협](genres/wuxia.csv) | 3010 |
| [판타지](genres/fantasy.csv) | 2456 |
| [로맨스](genres/romance.csv) | 1400 |

## 다시 생성

`python3 scripts/import_game_icons.py --archive <공식 ZIP> --tags <태그 JSON> --about docs/assets/game-icons/upstream-authors.json`

공식 태그 스냅샷은 `upstream-tags.json`, 저작자 스냅샷은 `upstream-authors.json`에 보관한다. 장르 분류는 스크립트의 `GENRE_TOPICS`에서 조정한다. 라이선스가 CC0라고 명시된 두 저작자는 해당 예외를 유지하고 나머지는 CC BY 3.0으로 기록했다.
