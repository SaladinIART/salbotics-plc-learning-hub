# Static Demo Publishing Notes

Phase 1 publishes two surfaces:

1. Public static learning demo for browsing pages, screenshots, and documentation.
2. Local FastAPI simulator for interactive PLC controls.

## Static Demo Boundary

The static demo should not expose live `/api/inputs/*` or `/api/commands/*`
controls on the public web. Those endpoints are for local learning only.

Recommended public behavior:

- Host static pages, CSS, JavaScript that does not require live control writes, docs, and screenshots.
- Present the live PLC/HMI simulator as a local-run feature.
- Link to the README run instructions for anyone who wants full interaction.
- Keep safety language visible: this project is educational and not certified control software.

## Suggested GitHub Pages Target

Assumed repository:

```text
https://github.com/SaladinIART/salbotics-plc-learning-hub
```

Assumed Pages URL:

```text
https://saladiniart.github.io/salbotics-plc-learning-hub/
```

## Screenshot Assets

Committed README screenshots:

```text
docs/screenshots/dashboard.png
docs/screenshots/how-it-works.png
docs/screenshots/oil-palm.png
docs/screenshots/programming-methods.png
```

Regenerate these after major visual changes and verify desktop/mobile layout before replacing them.

## Pre-Publish Checklist

- README renders on GitHub.
- `LICENSE` and `NOTICE` are present.
- Static demo pages load without Python.
- Public pages link back to GitHub, `salbotics.uk`, and the portfolio placeholder or final portfolio URL.
- No live control endpoint is advertised as a hosted public control surface.
- `docs/PROJECT_SWOT_ANALYSIS.md` remains private/untracked unless intentionally rewritten as a public roadmap.


## Why the public URL returned 404 (fixed in this branch)

Two causes: (1) the repository had no Pages deployment, so
`salbotics.uk/salbotics-plc-learning-hub/` (served from the Pages project of this
repo) had nothing to show and fell through to the portfolio's 404 page; and
(2) the pages use absolute `/static/...` paths that break under the
`/salbotics-plc-learning-hub/` sub-path.

Fix: `scripts/build_pages_site.py` builds a relative-link copy of `static/` (the
"What is this?" overview (`start.html`) is the landing page; the live simulator panel is left out because it
needs the local backend), and `.github/workflows/pages.yml` deploys it.

One-time step that only the repository owner can do: GitHub -> repository
Settings -> Pages -> Build and deployment -> Source: **GitHub Actions**, then merge
this branch to `main` (or run the workflow manually). Local check:

```powershell
python scripts/build_pages_site.py --output site-preview
python -m http.server 8080 --directory site-preview
```
