# Ellavox AI Regulation Tracker

Lightweight local web app for a quick look at **US AI regulation status** (federal + 50 states + DC), with jurisdiction detail, primary source links, and a change timeline.

**Not legal advice** — operational briefing for Ellavox product / GTM / compliance awareness.

## Stack

- FastAPI + Jinja2 (server-rendered HTML)
- SQLite (`data/tracker.db`)
- Minimal CSS (dark professional palette)

## Setup

```bash
cd /workspace/ellavox/ai-reg-tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed_baseline.py
```

## Run

```bash
cd /workspace/ellavox/ai-reg-tracker
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Open: http://127.0.0.1:8765/

Alternate:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

## Pages

| Path | Description |
|------|-------------|
| `/` | Federal card + state/DC grid; filter chips (All / Hot / In force / Ellavox-relevant) |
| `/j/{code}` | Summary, obligations, sources, history timeline (e.g. `/j/CA`) |
| `/about` | Brief disclaimer |

## API (local monthly routine)

No auth — **localhost only**. Do not expose publicly.

### `GET /api/jurisdictions`

Optional `?filter=all|hot|in_force|ellavox`.

### `GET /api/jurisdictions/{code}`

Returns jurisdiction + obligations (with sources) + jurisdiction sources + history.

### `POST /api/ingest`

Upserts jurisdiction fields; **appends** obligations, sources, and history events.

Example:

```bash
curl -s -X POST http://127.0.0.1:8765/api/ingest \
  -H 'Content-Type: application/json' \
  -d '{
    "code": "CA",
    "status_label": "in_force",
    "status_color": "in_force",
    "summary": "Updated summary…",
    "last_reviewed": "2026-10-22",
    "last_global_refresh": "2026-10-22",
    "history_events": [{
      "event_date": "2026-10-15",
      "title": "AB 1609 signed",
      "detail": "Governor signed AB 1609.",
      "source_url": "https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202520260AB1609"
    }],
    "obligations": [{
      "title": "AB 1609 — Customer service chatbots",
      "status": "in_force",
      "effective_date": "2027-01-01",
      "themes": ["disclosure", "companion_cs"],
      "ellavox_relevance": "high",
      "ellavox_why": "CS chatbot human-agent duties.",
      "summary": "Chaptered…",
      "sources": [{"label": "Chaptered bill", "url": "https://leginfo.legislature.ca.gov/"}]
    }]
  }'
```

Payload fields (all optional except `code`; `name`+`kind` required when creating a new code):

- Jurisdiction: `name`, `kind`, `status_color`, `status_label`, `summary`, `last_reviewed`, `notes`
- `obligations[]`: `title`, `status`, `effective_date`, `themes[]`, `ellavox_relevance`, `ellavox_why`, `summary`, `sources[]`
- `sources[]` (jurisdiction-level): `label`, `url`
- `history_events[]`: `event_date`, `title`, `detail`, `source_url`
- `last_global_refresh`: sets global refresh meta shown on home

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
| `quiet` | No Ellavox-material rules in focus |


## Static export (GitHub Pages)

GitHub Pages cannot run FastAPI/SQLite. Export a hash-routed SPA into `docs/`:

```bash
cd /workspace/ellavox/ai-reg-tracker
source .venv/bin/activate
make static
# or: python scripts/export_static.py
```

Output:

| Path | Role |
|------|------|
| `docs/index.html` | SPA shell |
| `docs/assets/app.js` | Hash router (`#/`, `#/?filter=hot`, `#/j/CA`, `#/about`) |
| `docs/assets/style.css` | Same dark theme as the FastAPI app |
| `docs/data/all.json` | Full dump (jurisdictions + details) |

Preview locally:

```bash
python -m http.server -d docs 8080
# open http://127.0.0.1:8080/
```

In the GitHub repo: **Settings → Pages → Source: Deploy from a branch → `/docs` folder**.

The FastAPI app remains the source of truth for local ingest/API; re-run `make static` after seeding or ingesting to refresh Pages content. Generated `docs/data/*.json` is fine to commit for a private repo so Pages has content without a CI build step.

## License / use

Internal Ellavox tooling. Local computer only.
