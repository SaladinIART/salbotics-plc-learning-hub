"""Record sample data for the Phase 3 and Phase 4 dashboards on the public website.

The public site has no trainer server behind it, so its dashboards would be
empty. This script runs the trainer's own API in-process (no network, no
background tasks) and saves one snapshot per dashboard as static JSON. On the
website, phase3-analytics.js and phase4-legacy.js draw these snapshots with
their normal chart code and label them as sample data.

Usage:
    python scripts/build_dashboard_samples.py
"""

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from main import create_app  # noqa: E402

ANALYTICS_URLS = [
    "/api/analytics/summary",
    "/api/analytics/events?limit=12",
    "/api/analytics/trends?metric=oer_percent&minutes=60",
    "/api/analytics/trends?metric=press_current_a&minutes=60",
    "/api/analytics/trends?metric=tank_level_percent&minutes=60",
]
LEGACY_URLS = [
    "/api/legacy/summary",
    "/api/legacy/registers",
    "/api/legacy/events?limit=10",
]


def scrub(value, tmp):
    """Replace this machine's temporary database paths with a neutral label."""
    if isinstance(value, dict):
        return {k: scrub(v, tmp) for k, v in value.items()}
    if isinstance(value, list):
        return [scrub(v, tmp) for v in value]
    if isinstance(value, str) and tmp in value:
        return "sample recorded from the local trainer"
    return value


def record(client, urls, tmp):
    data = {}
    for url in urls:
        response = client.get(url)
        response.raise_for_status()
        data[url] = scrub(response.json(), tmp)
    return data


def main():
    with tempfile.TemporaryDirectory() as tmp:
        app = create_app(start_background=False,
                         analytics_db_path=Path(tmp) / "analytics.sqlite3",
                         legacy_db_path=Path(tmp) / "legacy.sqlite3")
        with TestClient(app) as client:
            outputs = {
                "sample-analytics.json": record(client, ANALYTICS_URLS, tmp),
                "sample-legacy.json": record(client, LEGACY_URLS, tmp),
            }
    for name, data in outputs.items():
        path = ROOT / "static" / name
        path.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
