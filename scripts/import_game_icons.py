"""Import an official Game-icons archive and build topic catalogs and an offline gallery."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "packages/codex-assets/src/codex_assets/static/assets/game-icons"
DOCS = ROOT / "docs/assets/game-icons"
SOURCE = "https://game-icons.net/archives/000000/transparent/game-icons.net.svg.zip"
# Specific topics precede broader ones for the physical file location. Other matches remain searchable.
TOPICS = [
    ("items/jewelry", "장신구·보석", "jewellery"),
    ("items/weapons", "무기·방패", "weapon arrow axe blade bomb gun shield target"),
    ("items/armor-clothing", "방어구·의복", "clothing armor boot hat mask"),
    ("items/potions-containers", "약병·액체·연금술", "bottle chemical liquid poison glass container life"),
    ("creatures/monsters", "몬스터·환수", "creature"),
    ("creatures/people", "판타지 인물", "medieval-fantasy"),
    ("creatures/animals", "동물·곤충", "animal bird claw fish insect mammal reptile shell tentacle wing"),
    ("body/anatomy", "신체·해부", "body anatomy blood bone eye hand head heart mouth skull death"),
    ("technology/transport", "교통·기계", "machine boat electronic robot vehicle"),
    ("nature/plants", "식물·약재 후보", "plant mushroom wood farm"),
    ("items/food-kitchen", "음식·주방", "food egg fruit kitchenware meat"),
    ("places/architecture", "건축·장소", "building bridge door tower statue"),
    ("items/household-tools", "생활·도구·책", "tool household office bag book lock money time string flag"),
    (
        "nature/elements-landscape",
        "자연물·현상",
        "nature sea sky space stone mineral metal fire ice lightning energy smoke light star",
    ),
    (
        "culture/games-arts",
        "놀이·음악·문화",
        "cinema circus board arimaa cluedo dice catan tarot toy sound musical-instrument video-game ball sport",
    ),
    (
        "culture/history",
        "역사·문명",
        "civilization egypt greek-roman celtic stone-age viking western world-wars ninja pirate police steampunk",
    ),
    ("culture/fiction", "특정 작품·SF", "game-of-thrones science-fiction super-mario zelda"),
    ("themes/undead", "언데드 관련물", "vampire zombie"),
    (
        "symbols/interface",
        "상징·상태·기호",
        "symbol rank map australia france mexico abstract cross gui block spike action state explosion trap",
    ),
]
LABELS = {key: label for key, label, _ in TOPICS} | {"review/untagged": "공식 태그 미확인"}
AUTHOR_ALIASES = {
    "andymeneely": "Andy Meneely",
    "aussiesim": "Simon (aussiesim)",
    "lucasms": "Lucas",
    "heavenly-dog": "HeavenlyDog",
}
CC0 = {"viscious-speed", "zeromancer"}  # Explicit exceptions in the archive's license.txt.
GENRE_TOPICS = {
    "무협": {
        "items/jewelry",
        "items/weapons",
        "items/armor-clothing",
        "items/potions-containers",
        "creatures/animals",
        "body/anatomy",
        "nature/plants",
        "places/architecture",
        "items/household-tools",
        "nature/elements-landscape",
    },
    "판타지": {
        "items/jewelry",
        "items/weapons",
        "items/armor-clothing",
        "items/potions-containers",
        "creatures/monsters",
        "creatures/people",
        "creatures/animals",
        "nature/plants",
        "places/architecture",
        "nature/elements-landscape",
    },
    "로맨스": {
        "items/jewelry",
        "items/armor-clothing",
        "items/food-kitchen",
        "items/household-tools",
        "places/architecture",
        "nature/plants",
    },
}
EXCLUDE_GENRE_TAGS = {
    "gun",
    "robot",
    "science-fiction",
    "world-wars",
    "police",
    "super-mario",
    "zelda",
    "game-of-thrones",
}


class Authors(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.cell: str | None = None
        self.row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self.row = []
        elif tag == "td":
            self.cell = ""

    def handle_data(self, data: str) -> None:
        if self.cell is not None:
            self.cell += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self.cell is not None:
            self.row.append(self.cell.strip())
            self.cell = None
        elif tag == "tr" and len(self.row) == 3:
            self.rows.append(self.row)


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = [
        "id",
        "name",
        "author",
        "author_url",
        "primary_topic",
        "topics",
        "candidate_genres",
        "tags",
        "svg_path",
        "source_url",
        "license",
        "license_url",
        "modified",
        "sha256",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: ";".join(row[key]) if isinstance(row[key], list) else row[key] for key in fields})


def build(archive: Path, tags_path: Path, about: Path) -> None:
    tags = json.loads(tags_path.read_text())
    by_icon: dict[str, set[str]] = {}
    for tag, ids in tags.items():
        for icon_id in ids:
            by_icon.setdefault(icon_id, set()).add(tag)
    parser = Authors()
    if about.suffix == ".json":
        parser.rows = json.loads(about.read_text())
    else:
        parser.feed(about.read_text())
    authors = {re.sub(r"[^a-z0-9]+", "", row[0].lower()): (row[0], row[2]) for row in parser.rows}
    STATIC.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    previous = json.loads((STATIC / "catalog.json").read_text())["icons"] if (STATIC / "catalog.json").exists() else []
    rows = []
    with ZipFile(archive) as bundle:
        license_text = bundle.read("icons/license.txt").decode()
        for exception in CC0:
            assert any(
                exception.replace("-", "") in re.sub(r"[^a-z0-9]", "", line.lower()) and "CC0" in line
                for line in license_text.splitlines()
            )
        (STATIC / "LICENSE.txt").write_text(license_text)
        for entry in sorted(bundle.namelist()):
            if not entry.endswith(".svg"):
                continue
            parts = PurePosixPath(entry).parts
            assert parts[:4] == ("icons", "000000", "transparent", "1x1") and len(parts) == 6
            author_slug, filename = parts[-2:]
            slug = filename[:-4]
            icon_id = f"{author_slug}/{slug}"
            icon_tags = by_icon.get(icon_id, set())
            topics = [key for key, _, topic_tags in TOPICS if icon_tags.intersection(topic_tags.split())] or [
                "review/untagged"
            ]
            primary = topics[0]
            author_key = AUTHOR_ALIASES.get(author_slug, author_slug)
            author_key = re.sub(r"[^a-z0-9]+", "", author_key.lower())
            assert author_key in authors, author_slug
            author, author_url = authors[author_key]
            license_id = "CC0-1.0" if author_slug in CC0 else "CC-BY-3.0"
            license_url = (
                "https://creativecommons.org/publicdomain/zero/1.0/"
                if author_slug in CC0
                else "https://creativecommons.org/licenses/by/3.0/"
            )
            content = bundle.read(entry)
            node = ET.fromstring(content)
            assert node.tag == "{http://www.w3.org/2000/svg}svg"
            assert not any(
                child.tag.rsplit("}", 1)[-1] in {"script", "image", "foreignObject"} for child in node.iter()
            ), icon_id
            relative = f"{primary}/{author_slug}/{filename}"
            dest = STATIC / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
            genres = [
                genre
                for genre, allowed in GENRE_TOPICS.items()
                if allowed.intersection(topics) and not icon_tags.intersection(EXCLUDE_GENRE_TAGS)
            ]
            if (
                "heart" in icon_tags
                and "로맨스" not in genres
                and not icon_tags.intersection({"blood", "skull", "death"})
            ):
                genres.append("로맨스")
            rows.append(
                dict(
                    id=icon_id,
                    name=slug.replace("-", " ").title(),
                    author=author,
                    author_url=author_url,
                    primary_topic=primary,
                    topics=topics,
                    candidate_genres=genres,
                    tags=sorted(icon_tags),
                    relative_path=relative,
                    svg_path=f"/static/assets/game-icons/{relative}",
                    source_url=f"https://game-icons.net/1x1/{icon_id}.html",
                    license=license_id,
                    license_url=license_url,
                    modified=False,
                    sha256=hashlib.sha256(content).hexdigest(),
                    original_archive_path=entry,
                )
            )
    expected_paths = {row["relative_path"] for row in rows}
    for old in previous:
        if old["relative_path"] not in expected_paths:
            old_file = STATIC / old["relative_path"]
            if old_file.exists():
                if hashlib.sha256(old_file.read_bytes()).hexdigest() != old["sha256"]:
                    raise ValueError(f"Preserve edited import file: {old_file}")
                old_file.unlink()
    rows.sort(key=lambda row: (row["primary_topic"], row["name"], row["id"]))
    provenance = {
        "source": SOURCE,
        "downloaded_at": datetime.now(UTC).isoformat(),
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "tags_source": "https://game-icons.net/tags.html",
        "authors_source": "https://game-icons.net/about.html",
        "icon_count": len(rows),
        "tag_page_count": len(tags),
        "classification": "official tags mapped to project topics; genre entries are candidates, not approved word mappings",
    }
    payload = {"provenance": provenance, "topics": LABELS, "icons": rows}
    (STATIC / "catalog.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    (DOCS / "upstream-tags.json").write_text(json.dumps(tags, ensure_ascii=False, indent=2) + "\n")
    (DOCS / "upstream-authors.json").write_text(json.dumps(parser.rows, ensure_ascii=False, indent=2) + "\n")
    (DOCS / "provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n")
    write_csv(DOCS / "catalog.csv", rows)
    for topic in LABELS:
        subset = [row for row in rows if topic in row["topics"]]
        if subset:
            write_csv(DOCS / "topics" / (topic + ".csv"), subset)
    for genre, slug in [("무협", "wuxia"), ("판타지", "fantasy"), ("로맨스", "romance")]:
        write_csv(DOCS / "genres" / (slug + ".csv"), [row for row in rows if genre in row["candidate_genres"]])
    credits = [
        "# Game-icons 출처와 저작자",
        "",
        "공식 묶음의 SVG를 수정 없이 보관했다. 서비스에 사용하는 아이콘의 원작자, 원본 링크, 라이선스, 변경 사실을 표시한다. 원본 라이선스는 `packages/codex-assets/src/codex_assets/static/assets/game-icons/LICENSE.txt`에 보관한다.",
        "",
        "| 저작자 | 아이콘 수 | 라이선스 |",
        "|---|---:|---|",
    ]
    credits_html = []
    for author in sorted({row["author"] for row in rows}):
        entries = [row for row in rows if row["author"] == author]
        first = entries[0]
        linked = f"[{author}]({first['author_url']})" if first["author_url"] else author
        credits.append(f"| {linked} | {len(entries)} | [{first['license']}]({first['license_url']}) |")
        credits_html.append(
            "<tr><td>"
            + (
                f'<a href="{html.escape(first["author_url"], quote=True)}">{html.escape(author)}</a>'
                if first["author_url"]
                else html.escape(author)
            )
            + f'</td><td>{len(entries)}</td><td><a href="{first["license_url"]}">{first["license"]}</a></td></tr>'
        )
    (DOCS / "ATTRIBUTION.md").write_text("\n".join(credits) + "\n")
    (STATIC / "credits.html").write_text(
        '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Game-icons 출처</title><style>body{font:16px/1.7 system-ui;max-width:850px;margin:50px auto;padding:0 24px;color:#242424}td,th{text-align:left;padding:8px 24px 8px 0;border-bottom:1px solid #ddd}a{color:#333}</style><h1>Game-icons 출처</h1><p>Icons made by the authors below. Available on <a href="https://game-icons.net/">game-icons.net</a>. Downloaded SVGs are unmodified.</p><p>Each icon’s source and license are linked in the <a href="gallery.html">gallery</a> and <a href="catalog.json">catalog</a>. <a href="LICENSE.txt">Original license notice</a>.</p><table><tr><th>저작자</th><th>개수</th><th>라이선스</th></tr>'
        + "".join(credits_html)
        + "</table></html>"
    )
    summary = [
        "# Game-icons 주제별 목록",
        "",
        f"공식 검정/투명 배경 묶음에서 SVG **{len(rows):,}개**를 받았다. SVG 바이트를 수정하지 않았으며 원본 저작자·출처·라이선스·SHA-256을 보관한다.",
        "",
        "[갤러리](../../../packages/codex-assets/src/codex_assets/static/assets/game-icons/gallery.html) · [전체 CSV](catalog.csv) · [저작자 표시](ATTRIBUTION.md) · [다운로드 기록](provenance.json)",
        "",
        "## 분류 방식",
        "",
        "- 파일 위치는 `packages/codex-assets/src/codex_assets/static/assets/game-icons/<대표 주제>/<저작자>/<아이콘>.svg`다.",
        "- 공식 태그를 기준으로 여러 주제에 연결하되, 실제 SVG 파일은 대표 주제에 한 번만 보관한다.",
        "- 분류가 겹치므로 주제별 개수를 더하면 전체 아이콘 수보다 커진다.",
        "- 장르 목록은 탐색 후보이며 한국어 단어와의 최종 매핑이 아니다. 기존 300개 단어의 매핑은 보존했다.",
        "- 파일을 받았다는 사실과 도감 사용에 적합하다는 판단은 구분한다. 아직 개별 도상 4,180개를 모두 시각 검토한 것은 아니다.",
        "",
        "## 주제별 개수",
        "",
        "| 분류 | 대표 폴더의 파일 수 | 전체 참조 수 |",
        "|---|---:|---:|",
    ]
    for topic, label in LABELS.items():
        count = sum(topic in row["topics"] for row in rows)
        if count:
            summary.append(
                f"| [{label}](topics/{topic}.csv) | {sum(row['primary_topic'] == topic for row in rows)} | {count} |"
            )
    summary.extend(["", "## 장르 후보", "", "| 장르 | 후보 수 |", "|---|---:|"])
    for genre, slug in [("무협", "wuxia"), ("판타지", "fantasy"), ("로맨스", "romance")]:
        summary.append(f"| [{genre}](genres/{slug}.csv) | {sum(genre in row['candidate_genres'] for row in rows)} |")
    summary.extend(
        [
            "",
            "## 다시 생성",
            "",
            "`python3 scripts/import_game_icons.py --archive <공식 ZIP> --tags <태그 JSON> --about docs/assets/game-icons/upstream-authors.json`",
            "",
            "공식 태그 스냅샷은 `upstream-tags.json`, 저작자 스냅샷은 `upstream-authors.json`에 보관한다. 장르 분류는 스크립트의 `GENRE_TOPICS`에서 조정한다. 라이선스가 CC0라고 명시된 두 저작자는 해당 예외를 유지하고 나머지는 CC BY 3.0으로 기록했다.",
        ]
    )
    (DOCS / "README.md").write_text("\n".join(summary) + "\n")
    build_gallery(payload)
    print(
        json.dumps(
            {
                "icons": len(rows),
                "without_tags": sum(not row["tags"] for row in rows),
                "licenses": dict(Counter(row["license"] for row in rows)),
                "primary_topics": dict(Counter(row["primary_topic"] for row in rows)),
                "genre_candidates": {
                    genre: sum(genre in row["candidate_genres"] for row in rows) for genre in GENRE_TOPICS
                },
            },
            ensure_ascii=False,
        )
    )


def build_gallery(payload: dict) -> None:
    template = (ROOT / "scripts/templates/game-icons-gallery.html").read_text()
    # Source names are plain text in the gallery; escape closing script sequences as well.
    embedded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    (STATIC / "gallery.html").write_text(
        template.replace("__CATALOG_JSON__", embedded).replace(
            "__PALETTES_JSON__", (STATIC / "palettes.json").read_text()
        )
    )


if __name__ == "__main__":
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--archive", type=Path, required=True)
    args.add_argument("--tags", type=Path, required=True)
    args.add_argument("--about", type=Path, required=True)
    options = args.parse_args()
    build(options.archive, options.tags, options.about)
