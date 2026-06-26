# Security And Safety Boundary

Salbotics PLC Learning Hub is an educational local simulator.

## Safe Default

- The launcher binds to `127.0.0.1`.
- This means the app is intended for the same computer only.
- The live FastAPI simulator is not meant to be a public internet control panel.

## Do Not Use This As

- Certified safety software.
- Real traffic-control software.
- Real machinery control software.
- Boiler, pressure, or process protection.
- Production SCADA, historian, MES, or ERP.

## Public Demo Guidance

For LinkedIn, recruiter review, portfolio pages, and GitHub Pages:

- Prefer screenshots and static pages.
- Do not expose live `/api/inputs`, `/api/commands`, or `/api/analytics/reset`.
- Do not run with `--host 0.0.0.0` unless authentication, firewall rules, and engineering review are added.
- Do not add real plant credentials, private IP addresses, customer data, or production recipes.
- Do not use Phase 4 material to bypass software licenses, defeat vendor protections, or command real machinery.

## Security Checks Used

Recent public-prep checks:

- `pytest`
- `pip-audit`
- `pip check`
- `npm audit --audit-level=moderate`
- simple secret-pattern scan

No known dependency vulnerabilities were found after the latest dependency update.
