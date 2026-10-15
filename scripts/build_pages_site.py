"""Build the public static GitHub Pages site from ./static.

Why this exists
---------------
The learning pages use absolute paths such as ``/static/styles.css`` because
the local FastAPI app serves them from the domain root. On GitHub Pages the
site lives under ``/salbotics-plc-learning-hub/``, so those paths 404 and the
styles break. This script copies ``static/`` into a NEW directory, rewrites
the paths to relative ones, makes the beginner guide the landing page, and
leaves the live simulator panel out (it needs the local /api backend).

Usage:
    python scripts/build_pages_site.py --output site

The output directory must not exist. Standard library only.
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
REPO_URL = "https://github.com/SaladinIART/salbotics-plc-learning-hub"
LANDING_SOURCE = "beginner-guide.html"
EXCLUDED = {"index.html"}  # live simulator: requires the local FastAPI backend

BACK_LINK = re.compile(r'<a class="([^"]*)" href="/">.*?</a>', re.S)
ATTR = re.compile(r'(?:href|src)="([^"]+)"')


def rewrite_html(text):
    text = BACK_LINK.sub(
        lambda m: f'<a class="{m.group(1)}" href="{REPO_URL}">RUN LOCALLY</a>',
        text)
    text = text.replace('href="/static/', 'href="').replace('src="/static/', 'src="')
    return text


def build(output):
    output = Path(output)
    if output.exists():
        raise FileExistsError(f"Output directory already exists: {output}")
    output.mkdir(parents=True)
    for src in sorted(STATIC.iterdir()):
        if not src.is_file() or src.name in EXCLUDED:
            continue
        if src.suffix == ".html":
            text = rewrite_html(src.read_text(encoding="utf-8"))
            (output / src.name).write_text(text, encoding="utf-8", newline="\n")
        else:
            shutil.copy2(src, output / src.name)
    landing = (output / LANDING_SOURCE).read_text(encoding="utf-8")
    (output / "index.html").write_text(landing, encoding="utf-8", newline="\n")
    (output / ".nojekyll").write_text("", encoding="utf-8")
    return output


def check(output):
    """Return a list of problems: absolute local paths or unresolved links."""
    problems = []
    for page in sorted(Path(output).glob("*.html")):
        for ref in ATTR.findall(page.read_text(encoding="utf-8")):
            if re.match(r"^(https?:|mailto:|#|data:)", ref):
                continue
            if ref.startswith("/"):
                problems.append(f"{page.name}: absolute path {ref}")
                continue
            target = ref.split("#", 1)[0].split("?", 1)[0]
            if target and not (Path(output) / target).is_file():
                problems.append(f"{page.name}: missing target {ref}")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args(argv)
    try:
        out = build(a.output)
    except FileExistsError as exc:
        ap.exit(2, f"{exc}\n")
    problems = check(out)
    for p in problems:
        print("PROBLEM:", p)
    pages = len(list(out.glob("*.html")))
    print(f"built {pages} pages into {out}; {len(problems)} link problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
