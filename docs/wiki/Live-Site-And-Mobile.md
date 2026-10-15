# Live Site And Mobile

## Live Site

- URL: https://salbotics.uk/salbotics-plc-learning-hub/
- Content: a read-only copy of the learning pages; the Beginner guide is the landing page.
- Not published: the live PLC/HMI simulator panel and its `/api` controls. Run the trainer locally
  for those (see [Windows Download And Launch](Windows-Download-And-Launch.md)).

## How Publishing Works

1. `scripts/build_pages_site.py` copies `static/` into a new folder, rewrites `/static/...` links
   so they work under `/salbotics-plc-learning-hub/`, makes the Beginner guide `index.html`, and
   fails if any link is broken.
2. `.github/workflows/pages.yml` runs that build on every pull request (check only) and deploys to
   GitHub Pages from `main`.
3. The repository's Pages source must be **GitHub Actions** (Settings -> Pages).

Preview locally:

```powershell
python scripts/build_pages_site.py --output site-preview
python -m http.server 8080 --directory site-preview
```

## On Phones

On screens under about 760 px (desktop is unchanged):

- **MENU button** replaces the full link bar.
- **Calmer text** on guide pages: normal case, larger body text, lighter weights.
- **Stacked diagrams** on the Beginner guide so labels stay readable.
- **Collapsible sections** with a **Jump to section** menu on the longest pages (Oil Palm,
  Industrial Situations, Phase 2, PLC Methods).
- **Swipe sideways** hints on wide ladder diagrams and tables; the hint disappears after you swipe.

Without JavaScript the pages still work; the links and sections simply stay open.

## Troubleshooting

- **Page not found at the live URL:** check that the latest run in the Actions tab succeeded and
  that Pages source is GitHub Actions.
- **Old layout on a phone:** refresh the page; the browser may have cached old files.
