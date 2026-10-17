"""Render the local design using shared Django components and installed UI packages."""

import argparse
import re
import runpy
import subprocess
import sys
import tempfile
from pathlib import Path

import django
from django.conf import settings
from django.template import Context, Engine


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--tailwind-runtime", type=Path)
    parser.add_argument(
        "--reuse-ui-css",
        action="store_true",
        help="Reuse server/static/css/output.css; not a fresh CSS build.",
    )
    args = parser.parse_args()
    design_dir = Path(__file__).resolve().parent
    repo_root = design_dir.parent
    sys.path.insert(0, str(repo_root / "packages/codex-assets/src"))
    runtime_root = (args.runtime_root or repo_root).resolve()
    if not settings.configured:
        settings.configure(
            USE_I18N=False,
            INSTALLED_APPS=["django.contrib.staticfiles", "codex_assets"],
            STATIC_URL="/static/",
        )
    django.setup()
    engine = Engine(
        dirs=[
            str(repo_root / "server/templates"),
            str(repo_root / "packages/codex-assets/src/codex_assets/templates"),
        ],
        libraries={"codex_assets": "codex_assets.templatetags.codex_assets"},
    )
    template = engine.from_string((design_dir / "prototype.template.html").read_text())
    output = design_dir / "prototype.html"
    rendered = template.render(
        Context(
            {
                "preview_episodes": [
                    {"value": str(i), "label": label}
                    for i, label in enumerate(["1화 · 유리 온실", "2화 · 오래된 열쇠", "3화 · 밤의 손님"], 1)
                ]
            },
            use_l10n=False,
        )
    )
    rendered = rendered.replace(
        "/static/assets/game-icons/",
        "../packages/codex-assets/src/codex_assets/static/assets/game-icons/",
    )
    rendered = "\n".join(line.rstrip() for line in rendered.splitlines()) + "\n"
    output.write_text(rendered)
    guide_data = design_dir / "pages.json"
    if guide_data.exists():
        runpy.run_path(str(design_dir / "guide.py"), run_name="__main__")
    css_source = repo_root / "server/static/css/input.css"
    css_output = repo_root / "server/static/css/output.css"
    css = css_source.read_text().replace('"daisyui"', f'"{runtime_root / "node_modules/daisyui/index.js"}"')
    # Temporary input still resolves every @source relative to the canonical file.
    css = re.sub(r'(@source )"([^"]+)"', lambda match: f'{match[1]}"{(css_source.parent / match[2]).resolve()}"', css)
    tailwind_cli = runtime_root / "server/tailwindcss"
    if args.tailwind_runtime:
        tailwind_root = args.tailwind_runtime.resolve() / "node_modules"
        tailwind_cli = tailwind_root / ".bin/tailwindcss"
        css = css.replace('"tailwindcss"', f'"{tailwind_root / "tailwindcss/index.css"}"')
    if args.reuse_ui_css:
        if not css_output.exists():
            parser.error("--reuse-ui-css requires server/static/css/output.css")
        print("Tailwind CSS was not rebuilt; reusing server/static/css/output.css.")
    else:
        with tempfile.TemporaryDirectory(prefix="author-tools-") as scratch:
            css_input = Path(scratch) / "input.css"
            css_input.write_text(css)
            subprocess.run(
                [str(tailwind_cli), "-i", str(css_input), "-o", str(css_output), "--minify"],
                check=True,
            )
    subprocess.run(
        [
            str(runtime_root / "node_modules/.bin/esbuild"),
            str(design_dir / "prototype.ts"),
            "--bundle",
            "--format=iife",
            "--target=es2020",
            f"--outfile={design_dir / 'prototype.js'}",
        ],
        check=True,
    )
    if guide_data.exists():
        subprocess.run(
            [
                str(runtime_root / "node_modules/.bin/esbuild"),
                str(design_dir / "app.ts"),
                "--bundle",
                "--format=iife",
                "--target=es2020",
                f"--outfile={design_dir / 'app.js'}",
            ],
            check=True,
        )
    subprocess.run(
        [
            str(runtime_root / "node_modules/.bin/esbuild"),
            str(repo_root / "server/static/js/pattern-library.ts"),
            "--bundle",
            "--format=iife",
            "--target=es2020",
            f"--outfile={repo_root / 'server/static/js/pattern-library.js'}",
        ],
        check=True,
    )
    # Keep the preview files usable when opened directly, without a server or CDN.
    styles = css_output.read_text()
    asset_styles = (
        repo_root / "packages/codex-assets/src/codex_assets/static/assets/game-icons/components.css"
    ).read_text()
    styles = styles + asset_styles
    for html_name, script_name in [("index.html", "app.js"), ("prototype.html", "prototype.js")]:
        html_file = design_dir / html_name
        html = html_file.read_text()
        script = (design_dir / script_name).read_text().replace("</script", "<\\/script")
        html = html.replace(
            '<link rel="stylesheet" href="../server/static/css/output.css">', f"<style>{styles}</style>"
        )
        html = html.replace(f'<script src="{script_name}" defer></script>', "")
        html = html.replace("</body>", f"<script>{script}</script></body>")
        html = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"
        html_file.write_text(html)
    print(f"Built: {design_dir / 'index.html'} and {output}")


if __name__ == "__main__":
    main()
