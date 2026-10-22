"""Add translation keys (data-i18n) to reader-facing text and collect the English source.

The language switch (static/hub-prefs.js) replaces every element that has
data-i18n / data-i18n-html with the chosen language from static/lang/*.json.
English always stays in the HTML. This script:

  1. adds keys to start-page text, the shared menu, footers and the animated
     scene captions on every page (keys already present are kept), and
  2. writes static/lang/en.json with the English text of every key, which is
     the checklist for static/lang/ms.json and static/lang/de.json.

Usage:
    python scripts/i18n_keys.py          # add missing keys + write en.json
    python scripts/i18n_keys.py --check  # fail if en.json is out of date
"""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
LESSONS = ["beginner-guide", "how-it-works", "plc-programming-methods", "industrial-situations",
           "oil-palm-industrial-environment", "oil-palm-control-stack-analysis", "phase-2-start-here",
           "phase-3-data-analytics", "phase-4-legacy-ot-recovery", "risk-assessment-certification"]

INLINE = r"(?:strong|em|a|code|br|b|span)"
SCRIPTS = ["hub-flow.js", "hub-home.js", "hub-prefs.js", "mobile-nav.js", "start.js",
           "phase3-analytics.js", "phase4-legacy.js"]
LEAF = re.compile(r"<(h1|h2|h3|p|li|th|td|small|strong|span|summary|figcaption|label|button|text|a|ol|ul|div|figure|nav|aside|article)\b([^>]*)>(.*?)</\1>", re.S)
CONTAINERS = {"ol", "ul", "div", "figure", "nav", "aside", "article"}

MENU = {"Home": "ui.nav.home", "Basics": "ui.nav.basics", "Skills": "ui.nav.skills",
        "Factory": "ui.nav.factory", "Data": "ui.nav.data", "Safety": "ui.nav.safety",
        "Simulator": "ui.nav.sim"}
STAGES = {"The basics": "stage.basics", "Real skills": "stage.skills", "A real factory": "stage.factory",
          "Data and networks": "stage.data", "Safety career": "stage.safety"}


def plain_text(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def add_attr(open_tag_attrs, attr):
    return open_tag_attrs + " " + attr


def key_leaves(region, prefix, counter):
    """Key every text leaf in `region` that has no key yet. Returns the new region.

    - text only            -> data-i18n (textContent)
    - text + inline markup -> data-i18n-html (its children are marked so they are not keyed again)
    - only child elements  -> not keyed; its children are keyed instead
    """
    def inside(m):
        """Leave this element unkeyed but key the text inside it."""
        tag, attrs, inner = m.group(1), m.group(2), m.group(3)
        return f"<{tag}{attrs}>" + LEAF.sub(repl, inner) + f"</{tag}>"

    def repl(m):
        tag, attrs, inner = m.group(1), m.group(2), m.group(3)
        if "data-i18n" in attrs or "sp-play" in attrs or "aria-hidden" in attrs or not plain_text(inner):
            return m.group(0)
        if tag in CONTAINERS or re.search(r"<(?!/?" + INLINE + r"\b)[a-z]", inner):
            return inside(m)                                       # block children: key inside
        if "data-i18n" in inner:                                   # a child already has a key
            return m.group(0)
        if re.fullmatch(r"[\s\d.·→←+&;%?!:\-–—/x×]*", plain_text(inner)):   # numbers/symbols only
            return m.group(0)
        has_children = re.search(r"<" + INLINE + r"\b", inner)
        direct_text = re.sub(r"<(" + INLINE + r")\b[^>]*>.*?</\1>|<br\s*/?>", "", inner, flags=re.S).strip()
        if has_children and not direct_text:
            return inside(m)                                       # children get their own keys
        counter[0] += 1
        if has_children:
            inner = re.sub(r"<(" + INLINE + r")\b", r"<\1 data-i18n-in", inner)
            return f'<{tag}{attrs} data-i18n-html="{prefix}.{counter[0]}">{inner}</{tag}>'
        return f'<{tag}{attrs} data-i18n="{prefix}.{counter[0]}">{inner}</{tag}>'
    previous = None
    while previous != region:            # nested leaves (e.g. <li><strong>) need more passes
        previous = region
        region = LEAF.sub(repl, region)
    return region.replace(" data-i18n-in", "")


def key_menu(text):
    for label, key in MENU.items():
        text = re.sub(rf'(<a class="(?:header-link|connection-pill guide-back)" href="[^"]*"[^>]*?)>({label})</a>',
                      lambda m: (m.group(0) if "data-i18n" in m.group(1)
                                 else f'{m.group(1)} data-i18n="{key}">{m.group(2)}</a>'), text)
    return text


def key_start(text):
    # Lesson map and stage names share keys with hub-flow.js.
    text = re.sub(
        r'<a href="/static/([a-z0-9-]+)\.html"><span class="sp-lesson-no">(\d+)</span><span><strong>(.*?)</strong><small>(.*?)</small></span></a>',
        lambda m: (f'<a href="/static/{m.group(1)}.html"><span class="sp-lesson-no">{m.group(2)}</span><span>'
                   f'<strong data-i18n="lesson.{m.group(1)}.title">{m.group(3)}</strong>'
                   f'<small data-i18n="lesson.{m.group(1)}.blurb">{m.group(4)}</small></span></a>'), text)
    for name, key in STAGES.items():
        text = text.replace(f"<h3>{name}</h3>", f'<h3 data-i18n="{key}">{name}</h3>')
    start = text.index("<body")
    head, body = text[:start], text[start:]
    used = [int(n) for n in re.findall(r'"st\.(\d+)"', text)]
    body = key_leaves(body, "st", [max([0] + used)])
    return head + body


def key_lesson(text, name):
    # Header: brand and the lesson's own name (shared with hub-flow.js).
    text = text.replace('<a class="hub-home" href="/static/start.html">Salbotics PLC Hub</a>',
                        '<a class="hub-home" href="/static/start.html" data-i18n="ui.brand">Salbotics PLC Hub</a>', 1)
    text = re.sub(r'(<div class="brand-block">\s*<strong>(?:(?!</strong>).)*</strong>\s*)<span>([^<]+)</span>',
                  lambda m: f'{m.group(1)}<span data-i18n="lesson.{name}.title">{m.group(2)}</span>', text, count=1, flags=re.S)
    # Footer.
    m = re.search(r'<footer class="product-footer">(.*?)</footer>', text, re.S)
    if m and "data-i18n" not in m.group(0):
        text = text.replace(m.group(0), f'<footer class="product-footer" data-i18n-html="ui.footer">{m.group(1)}</footer>')
    # Beginner guide: closing "Educational use" note.
    if name == "beginner-guide" and '"bg.edu.1"' not in text:
        s = text.index('aria-label="Educational use note"')
        e = text.index("</div>", s)
        text = text[:s] + key_leaves(text[s:e], "bg.edu", [0]) + text[e:]
    # How it works: the traffic-light scene shares its keys with the start page.
    if name == "how-it-works":
        start = (STATIC / "start.html").read_text(encoding="utf-8")
        keyed = re.search(r'<svg class="sp-anim sp-anim-traffic".*?</svg>', start, re.S).group(0)
        text = re.sub(r'<svg class="sp-anim sp-anim-traffic".*?</svg>', lambda m: keyed, text, count=1, flags=re.S)
        if '"hw.scene.1"' not in text:
            s = text.index("<figcaption>")
            e = text.index("</figcaption>", s)
            text = text[:s] + key_leaves(text[s:e], "hw.scene", [0]) + text[e:]
    return text


def collect():
    strings = {}
    for page in ["start"] + LESSONS:
        text = (STATIC / f"{page}.html").read_text(encoding="utf-8")
        for m in re.finditer(r'<([a-z0-9]+)\b[^>]*?data-i18n(-html)?="([^"]+)"[^>]*>(.*?)</\1>', text, re.S):
            key, inner, is_html = m.group(3), m.group(4), bool(m.group(2))
            value = re.sub(r"\s+", " ", inner).strip() if is_html else plain_text(inner)
            if key in strings and strings[key] != value:
                raise SystemExit(f"key {key} has two different English texts:\n  {strings[key]}\n  {value}")
            strings[key] = value
        for m in re.finditer(r'<[a-z0-9]+\b([^>]*?)data-i18n-attr="([^"]+)"([^>]*)>', text):
            attrs = m.group(1) + m.group(3)
            for pair in m.group(2).split(";"):
                name, key = [x.strip() for x in pair.split(":")]
                value = re.search(rf'{name}="([^"]*)"', attrs).group(1)
                strings[key] = html.unescape(value)
    # Text built by scripts: hubT("js.key", "English") / T(...) / hubText(...)
    for name in SCRIPTS:
        code = (STATIC / name).read_text(encoding="utf-8")
        code = "\n".join(line for line in code.splitlines() if not line.strip().startswith("//"))
        for m in re.finditer(r'(?:hubT|T|hubText)\("(js\.[a-z0-9.]+)",\s*"((?:[^"\\]|\\.)*)"', code):
            strings[m.group(1)] = json.loads('"' + m.group(2) + '"')
    # Added by scripts/build_pages_site.py on the public site (the local trainer says "Simulator").
    strings["ui.nav.runlocal"] = "Run locally"
    # Tap-to-explain meanings (static/hub-ui.js)
    ui = (STATIC / "hub-ui.js").read_text(encoding="utf-8")
    for term, meaning in re.findall(r'\["([^"]+)", "([^"]+)"\]', ui):
        strings["gl." + term] = meaning
    return dict(sorted(strings.items()))


def main(argv):
    if "--check" not in argv:
        for page in ["start"] + LESSONS:
            path = STATIC / f"{page}.html"
            text = key_menu(path.read_text(encoding="utf-8"))
            text = key_start(text) if page == "start" else key_lesson(text, page)
            path.write_text(text, encoding="utf-8")
    strings = collect()
    out = STATIC / "lang" / "en.json"
    content = json.dumps(strings, ensure_ascii=False, indent=1) + "\n"
    if "--check" in argv:
        if not out.exists() or out.read_text(encoding="utf-8") != content:
            print("static/lang/en.json is out of date: run python scripts/i18n_keys.py")
            return 1
        print(f"en.json up to date ({len(strings)} keys)")
        return 0
    out.parent.mkdir(exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(f"wrote static/lang/en.json ({len(strings)} keys)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
