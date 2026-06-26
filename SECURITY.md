# Security Policy

## Intended Use

Salbotics PLC Learning Hub is an educational local simulator. It is designed for learning PLC, HMI, SCADA, communications, and analytics concepts on a personal computer.

The default launcher binds the server to `127.0.0.1`, so the app is intended to be used from the same computer only.

## Not Intended For

- Public internet hosting of the live FastAPI simulator.
- Real machinery control.
- Certified safety functions.
- Production SCADA, historian, MES, or ERP use.
- Storing real plant credentials, customer data, production recipes, or private network details.

## Safe Public Demo Guidance

For public demos, portfolios, and recruiter review:

- Prefer screenshots, static pages, or GitHub Pages content.
- Keep live `/api/inputs`, `/api/commands`, and `/api/analytics/reset` endpoints local.
- Do not run the app with `--host 0.0.0.0` unless you add authentication, firewall rules, and a security review.
- Do not connect this Phase 1-3 code directly to a real PLC, VFD, serial port, Modbus network, MQTT broker, or OPC UA server.

## Reporting A Vulnerability

Please open a private report or contact Salbotics Solutions before public disclosure if you find a vulnerability that could affect learners or public users.

Include:

- A short description of the issue.
- Steps to reproduce.
- Affected file or endpoint.
- Whether the issue affects local-only use, public static pages, or a possible hosted deployment.

## Dependency Checks

Before public releases, run:

```powershell
.\.venv\Scripts\python.exe -m pip install pip-audit
.\.venv\Scripts\python.exe -m pip_audit -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
cd frontend
npm audit --audit-level=moderate
```

Also run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```
