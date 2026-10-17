"""Render the local design using shared Django components and installed UI packages."""

import argparse
import runpy
import subprocess
import tempfile
from pathlib import Path

from django.conf import settings
from django.template import Context, Engine


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--tailwind-runtime", type=Path)
    args = parser.parse_args()
    design_dir = Path(__file__).resolve().parent
    repo_root = design_dir.parent
    runtime_root = (args.runtime_root or repo_root).resolve()
    if not settings.configured:
        settings.configure(USE_I18N=False)
    engine = Engine(dirs=[str(repo_root / "server/templates")])
    template = engine.from_string((design_dir / "prototype.template.html").read_text())
    output = design_dir / "prototype.html"
    output.write_text(template.render(Context({}, use_l10n=False)))
    guide_data = design_dir / "pages.json"
    if guide_data.exists():
        runpy.run_path(str(design_dir / "guide.py"), run_name="__main__")
    css = (design_dir / "input.css").read_text()
    css = css.replace('"daisyui"', f'"{runtime_root / "node_modules/daisyui/index.js"}"').replace(
        '"./prototype.html"', f'"{output}"'
    )
    for source in ("index.html", "app.ts"):
        css = css.replace(f'"./{source}"', f'"{design_dir / source}"')
    tailwind_cli = runtime_root / "server/tailwindcss"
    if args.tailwind_runtime:
        tailwind_root = args.tailwind_runtime.resolve() / "node_modules"
        tailwind_cli = tailwind_root / ".bin/tailwindcss"
        css = css.replace('"tailwindcss"', f'"{tailwind_root / "tailwindcss/index.css"}"')
    with tempfile.TemporaryDirectory(prefix="author-tools-") as scratch:
        css_input = Path(scratch) / "input.css"
        css_input.write_text(css)
        subprocess.run(
            [str(tailwind_cli), "-i", str(css_input), "-o", str(design_dir / "ui.css"), "--minify"],
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
    # Keep the preview files usable when opened directly, without a server or CDN.
    styles = (design_dir / "ui.css").read_text()
    for html_name, script_name in [("index.html", "app.js"), ("prototype.html", "prototype.js")]:
        html_file = design_dir / html_name
        html = html_file.read_text()
        script = (design_dir / script_name).read_text().replace("</script", "<\\/script")
        html = html.replace('<link rel="stylesheet" href="ui.css">', f"<style>{styles}</style>")
        html = html.replace(f'<script src="{script_name}" defer></script>', "")
        html = html.replace("</body>", f"<script>{script}</script></body>")
        html_file.write_text(html)
    print(f"Built: {design_dir / 'index.html'} and {output}")


if __name__ == "__main__":
    main()
