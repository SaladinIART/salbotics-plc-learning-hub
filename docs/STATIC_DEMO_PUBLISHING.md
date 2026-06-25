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

