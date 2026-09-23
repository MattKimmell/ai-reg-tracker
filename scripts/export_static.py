#!/usr/bin/env python3
"""Export tracker.db to a static SPA under docs/ for GitHub Pages.

Usage:
  python scripts/export_static.py
  make static

Writes:
  docs/index.html
  docs/assets/app.js
  docs/assets/style.css
  docs/assets/us-states.svg
  docs/data/all.json
  docs/data/briefing.json

Hash routes: #/  #/?filter=hot  #/j/CA  #/about
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import db  # noqa: E402
from app import briefing  # noqa: E402

DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"
DATA_DIR = DOCS / "data"
STATIC_SRC = Path(__file__).resolve().parent / "static_site"
APP_CSS = ROOT / "app" / "static" / "style.css"
APP_HOME_JS = ROOT / "app" / "static" / "home.js"


def scrub_public(obj):
    """Ensure public dump has no Ellavox branding in string values / legacy keys."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in ("ellavox_relevance", "ellavox_why"):
                continue
            out[k] = scrub_public(v)
        return out
    if isinstance(obj, list):
        return [scrub_public(x) for x in obj]
    if isinstance(obj, str):
        return re.sub(r"(?i)ellavox", "voice/conversation AI", obj)
    return obj


def build_payload() -> dict:
    db.ensure_db()
    jurisdictions = db.list_jurisdictions()
    details = []
    for j in jurisdictions:
        detail = db.jurisdiction_detail(j["code"])
        if not detail:
            continue
        details.append(
            {
                "jurisdiction": detail["jurisdiction"],
                "obligations": detail["obligations"],
                "sources": detail["sources"],
                "history": detail["history"],
            }
        )
    briefing_payload = briefing.build_briefing()
    payload = {
        "exported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_global_refresh": db.get_meta("last_global_refresh", "—"),
        "jurisdiction_count": len(jurisdictions),
        "stats": db.compute_stats(),
        "activity": db.activity_by_month(24),
        "briefing": briefing_payload,
        "jurisdictions": jurisdictions,
        "details": details,
    }
    return scrub_public(payload)


def write_site(payload: dict) -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for name in ("index.html", "app.js"):
        src = STATIC_SRC / name
        if not src.is_file():
            raise FileNotFoundError(f"Missing SPA template: {src}")
        dest = DOCS / name if name == "index.html" else ASSETS / name
        shutil.copy2(src, dest)

    if not APP_CSS.is_file():
        raise FileNotFoundError(f"Missing stylesheet: {APP_CSS}")
    shutil.copy2(APP_CSS, ASSETS / "style.css")

    svg_src = ROOT / "app" / "static" / "us-states.svg"
    if not svg_src.is_file():
        raise FileNotFoundError(f"Missing map SVG: {svg_src}")
    shutil.copy2(svg_src, ASSETS / "us-states.svg")

    out_json = DATA_DIR / "all.json"
    out_json.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    briefing_json = DATA_DIR / "briefing.json"
    briefing_json.write_text(
        json.dumps(payload.get("briefing") or {}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    (DOCS / ".nojekyll").write_text("", encoding="utf-8")


def main() -> int:
    if not db.DB_PATH.is_file():
        print(f"ERROR: database not found at {db.DB_PATH}", file=sys.stderr)
        print("Run: python scripts/seed_baseline.py", file=sys.stderr)
        return 1

    payload = build_payload()
    write_site(payload)

    n = payload["jurisdiction_count"]
    print(f"Exported {n} jurisdictions → {DOCS}/")
    print(f"  {DOCS / 'index.html'}")
    print(f"  {ASSETS / 'app.js'}")
    print(f"  {ASSETS / 'style.css'}")
    print(f"  {ASSETS / 'us-states.svg'}")
    print(f"  {DATA_DIR / 'all.json'}")
    print(f"  {DATA_DIR / 'briefing.json'}")
    print("Open via GitHub Pages or: python -m http.server -d docs 8080")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
