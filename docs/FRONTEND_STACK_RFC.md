# Frontend Stack RFC

Status: accepted for Phase 1 publishing.

Decision date: 2026-06-26.

## Decision

Use a staged migration toward **Astro + interactive SVG islands** for the public
learning hub.

Keep the existing **FastAPI + Python PLC engine** as the local interactive
simulator runtime.

Do not migrate the whole project to SvelteKit, React, or a full client-side SPA
for Phase 1.

## Why Astro Fits Phase 1

The project is now mostly a learning hub:

- Static guide pages.
- Long-form docs.
- SVG diagrams.
- Screenshots.
- A small local simulator.
- Recruiter-facing public README and static demo.

Astro fits this shape because it can generate fast static pages while still
allowing selective interactive islands later. That means the public demo can be
hosted as static content, while the Python simulator remains local and safe by
default.

## Why Not Full SvelteKit In Phase 1

SvelteKit would be a good choice for a deeply interactive training app, but it
is more migration than Phase 1 needs.

Avoiding a full SvelteKit migration now keeps focus on:

- Publishing the project.
- Improving public branding.
- Keeping the learning content readable.
- Avoiding delay before LinkedIn/GitHub sharing.
- Preserving the beginner-friendly current code path.

SvelteKit can be reconsidered later if the interactive lesson system becomes
large enough to need application-level routing, stores, and richer client state.

## What Stays In FastAPI

FastAPI remains responsible for:

- Local simulator server.
- `/api/state`.
- `/api/inputs/{name}`.
- `/api/commands/{command}`.
- Background PLC scan loop.
- Serving current static files until Astro migration matures.

The public static demo should not expose live write endpoints.

## Migration Stages

### Phase 1A - Current app polished and published

- Keep current static HTML/CSS/JS pages.
- Publish README, screenshots, license, notice, and static demo notes.
- Keep Python communications out of scope.

### Phase 1B - Astro shell spike

- Add a separate `frontend/` Astro project.
- Build one migrated guide page with shared layout, nav, footer, and SVG content.
- Prove `npm run build` creates a static export.
- Do not replace the current FastAPI-served pages yet.

### Phase 1C - Selective interactive islands

- Convert high-value diagrams into interactive SVG islands.
- Start with guide-style interactions, not live PLC-control endpoints.
- Keep local simulator controls behind FastAPI.

## Source Basis

- Astro: https://astro.build/
- Vite: https://vite.dev/
- SvelteKit: https://svelte.dev/docs/kit
- FastAPI templates/static files: https://fastapi.tiangolo.com/advanced/templates/

