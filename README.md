# US AI Reg Tracker

Lightweight tracker for **US AI regulation status** (federal + 50 states + DC), with jurisdiction detail, primary source links, change timeline, map, search, and activity chart.

**Not legal advice** — operational briefing for awareness of rules that may affect voice/conversation AI operators, customer-service bots, and phone AI.

## Stack

- FastAPI + Jinja2 (local server-rendered HTML)
- SQLite (`data/tracker.db`)
- Static SPA export under `docs/` for GitHub Pages

## Setup

```bash
cd /workspace/ellavox/ai-reg-tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed_baseline.py
```

## Run (local)

```bash
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Open: http://127.0.0.1:8765/

## Pages

| Path | Description |
|------|-------------|
| `/` | Stats, federal card, US map, activity chart, state list; filters All / Hot / In force / Voice/conversation; search |
| `/j/{code}` | Summary, obligations, sources, history timeline (e.g. `/j/CA`) |
| `/about` | Disclaimer |

## Data model notes

Obligation relevance fields:

| Field | Values | UI label |
|-------|--------|----------|
| `voice_cs_relevance` | `high` \| `medium` \| `low` \| `none` | Voice / conversation relevant |
| `voice_cs_why` | free text | Why it matters |

Legacy ingest keys `ellavox_relevance` / `ellavox_why` are still accepted by `POST /api/ingest` and mapped to the new names.

Filter chip `?filter=voice` = jurisdictions with high/medium `voice_cs_relevance` obligations.

## API (local monthly routine)

No auth — **localhost only**. Do not expose publicly.

### `GET /api/jurisdictions`

Optional `?filter=all|hot|in_force|voice`.

### `GET /api/jurisdictions/{code}`

### `GET /api/stats`

### `POST /api/ingest`

Upserts jurisdiction fields; **appends** obligations, sources, and history events.

Example obligation fields: `voice_cs_relevance`, `voice_cs_why` (preferred).

## Re-seed

```bash
python scripts/seed_baseline.py
```

Overwrites `data/tracker.db`.

## Status labels

| Label | Meaning |
|-------|---------|
| `in_force` | Operative obligation |
| `enacted_pending` | Enacted; effective date in future or awaiting start |
| `proposed_hot` | Active hot proposal / high watch |
| `watch` | Monitor; not quiet |
| `quiet` | No material voice/conversation AI rules in focus |

## Static export (GitHub Pages)

```bash
source .venv/bin/activate
make static
# or: python scripts/export_static.py
```

Output: `docs/index.html`, `docs/assets/*`, `docs/data/all.json`.

Preview:

```bash
python -m http.server -d docs 8080
```

In GitHub: **Settings → Pages → Source: Deploy from a branch → `/docs` folder**.

Re-run `make static` after seeding or ingesting to refresh Pages content.

## License / use

Public operational briefing. Confirm primary sources before compliance decisions.
