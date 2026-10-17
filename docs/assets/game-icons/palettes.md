# 도감 팔레트와 작품 색상 매핑

## 결정

공식 홈페이지의 8개 팔레트 HEX 값을 순서 그대로 보존한다. 각 팔레트는 배경 1색과 아이콘 전경 8색이다. 원본 SVG 파일을 수정하거나 색상별 SVG를 중복 저장하지 않고 CSS 마스크로 표시한다. 이는 홈페이지 팔레트를 사용한 배색이며 작가가 제작한 별도 컬러 원본이 아니다.

## 팔레트

| 팔레트 | 배경 | 아이콘색 8개 |
|---|---|---|
| threezerotwofour | #090300 | #DB2D20 / #E8BBD0 / #FDED02 / #01A252 / #B5E4F4 / #01A0E4 / #A16A94 / #CDAB53 |
| bespin | #28211C | #CF6A4C / #CF7D34 / #F9EE98 / #54BE0D / #AFC4DB / #5EA6EA / #9B859D / #937121 |
| bright | #000000 | #FB0120 / #FC6D24 / #FDA331 / #A1C659 / #76C7B7 / #6FB3D2 / #D381C3 / #BE643C |
| default | #181818 | #AB4642 / #DC9656 / #F7CA88 / #A1B56C / #86C1B9 / #7CAFC2 / #BA8BAF / #A16946 |
| eighties | #2D2D2D | #F2777A / #F99157 / #FFCC66 / #99CC99 / #66CCCC / #6699CC / #CC99CC / #D27B53 |
| flat | #2C3E50 | #E74C3C / #E67E22 / #F1C40F / #2ECC71 / #1ABC9C / #3498DB / #9B59B6 / #BE643C |
| monokai | #272822 | #F92672 / #FD971F / #F4BF75 / #A6E22E / #A1EFE4 / #66D9EF / #AE81FF / #CC6633 |
| solarized | #002B36 | #DC322F / #CB4B16 / #B58900 / #859900 / #2AA198 / #268BD2 / #6C71C4 / #D33682 |

## 사용 흐름

- 도감 에셋 목록에서 팔레트와 색상 견본을 고르면 현재 목록, 이후 검색·페이지, 상세 보기에 같은 배색을 적용한다. 흑백 원본 옵션으로 되돌릴 수 있다.
- 팔레트 배경 또는 투명(밝은 바탕)을 선택한다. 컬러 모드에서는 기존 흑백 반전 버튼을 비활성화한다.
- 작품 색상에 파란색·blue 같은 등록된 색 이름이나 3자리/6자리 HEX를 입력하고 가까운 색 적용을 누른다.
- 전체 팔레트의 64개 전경색 슬롯 또는 선택한 팔레트 안에서 찾는다. 잘못된 입력은 안내하고 기존 배색을 유지한다.
- 색상 선택은 이 목록의 미리보기 설정이다. 새로고침 시 흑백으로 돌아간다. 작품별 저장과 실제 독자 도감 연동은 후속 구현이다.

## 이후 작품 데이터 연결

`scripts/src/game-icon-colors.ts`의 `GameIconColors.nearest(color, paletteId?)`를 사용한다. HEX와 등록된 색 이름을 받으며 실패 시 null을 반환한다. 색 이름은 사전에 정한 대표 HEX로 해석하며 자연어 문장 전체를 분석하지 않는다. 파란색/blue의 기준은 #0066CC다.

유사도는 OKLab 좌표에서 색상 계열을 중시한 거리로 계산한다: `sqrt(0.25*dL² + dC² + 9*dH²)`. 동점은 공식 팔레트 및 색상 순서를 따른다. 이는 표준 Delta E가 아닌 도감용 가중 거리다.

작품마다 `assetId`와 아래 반환값을 함께 저장할 수 있다. 같은 brute 에셋에 서로 다른 작품 색상을 연결한다. 아직 저장 API나 독자 화면에 연결하지 않았다.

```json
{
  "assetId": "delapouite/brute",
  "requestedColor": "#0066CC",
  "paletteId": "solarized",
  "foreground": "#268BD2",
  "background": "#002B36"
}
```

반환값에는 `distance`도 있다. 원본의 저작자·라이선스 정보를 유지하고 배색 변경 사실을 표시한다.

## 소스와 빌드

- [공식 스크립트](https://game-icons.net/scripts/game-icons.js?v=20201115)
- [팔레트 JSON](../../../packages/codex-assets/src/codex_assets/static/assets/game-icons/palettes.json): 공식 값과 소스 SHA256
- [TypeScript 소스](../../../scripts/src/game-icon-colors.ts)
- [목록 템플릿](../../../scripts/templates/game-icons-gallery.html)

Node 24에서 다음 명령으로 브라우저용 JavaScript를 재생성한다. 팔레트 데이터는 importer가 JSON을 HTML에 삽입하므로 별도 fetch 없이 동작한다.

```sh
node --input-type=module -e 'import {stripTypeScriptTypes} from "node:module"; import fs from "node:fs"; fs.writeFileSync("packages/codex-assets/src/codex_assets/static/assets/game-icons/palette-colors.js",stripTypeScriptTypes(fs.readFileSync("scripts/src/game-icon-colors.ts","utf8"),{mode:"transform"}));'
```
