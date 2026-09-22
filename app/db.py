"""SQLite helpers for the US AI Reg Tracker."""
from __future__ import annotations

import json
import sqlite3
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "tracker.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS jurisdictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('federal', 'state', 'local')),
    status_color TEXT NOT NULL DEFAULT 'quiet',
    status_label TEXT NOT NULL DEFAULT 'quiet',
    summary TEXT NOT NULL DEFAULT '',
    last_reviewed TEXT,
    notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS obligations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jurisdiction_id INTEGER NOT NULL REFERENCES jurisdictions(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'proposed',
    effective_date TEXT,
    themes TEXT NOT NULL DEFAULT '[]',
    voice_cs_relevance TEXT NOT NULL DEFAULT 'none',
    voice_cs_why TEXT DEFAULT '',
    summary TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id) ON DELETE CASCADE,
    obligation_id INTEGER REFERENCES obligations(id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    url TEXT NOT NULL,
    CHECK (jurisdiction_id IS NOT NULL OR obligation_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS history_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jurisdiction_id INTEGER NOT NULL REFERENCES jurisdictions(id) ON DELETE CASCADE,
    event_date TEXT NOT NULL,
    title TEXT NOT NULL,
    detail TEXT DEFAULT '',
    source_url TEXT,
    event_kind TEXT NOT NULL DEFAULT 'milestone',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def ensure_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.executescript(SCHEMA)
        _migrate_legacy_columns(conn)
        _migrate_history_event_kind(conn)


def _migrate_legacy_columns(conn: sqlite3.Connection) -> None:
    """Rename ellavox_* columns to voice_cs_* if an older DB is present."""
    cols = {
        r["name"]
        for r in conn.execute("PRAGMA table_info(obligations)").fetchall()
    }
    if "ellavox_relevance" in cols and "voice_cs_relevance" not in cols:
        conn.execute(
            "ALTER TABLE obligations RENAME COLUMN ellavox_relevance TO voice_cs_relevance"
        )
    if "ellavox_why" in cols and "voice_cs_why" not in cols:
        conn.execute(
            "ALTER TABLE obligations RENAME COLUMN ellavox_why TO voice_cs_why"
        )
    # Re-check after possible renames
    cols = {
        r["name"]
        for r in conn.execute("PRAGMA table_info(obligations)").fetchall()
    }
    if "voice_cs_relevance" not in cols:
        conn.execute(
            "ALTER TABLE obligations ADD COLUMN voice_cs_relevance "
            "TEXT NOT NULL DEFAULT 'none'"
        )
    if "voice_cs_why" not in cols:
        conn.execute(
            "ALTER TABLE obligations ADD COLUMN voice_cs_why TEXT DEFAULT ''"
        )



def _migrate_history_event_kind(conn: sqlite3.Connection) -> None:
    """Add event_kind so seed/audit rows can be excluded from activity charts."""
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(history_events)").fetchall()}
    if "event_kind" not in cols:
        conn.execute(
            "ALTER TABLE history_events ADD COLUMN event_kind "
            "TEXT NOT NULL DEFAULT 'milestone'"
        )


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


def parse_themes(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def get_meta(key: str, default: str | None = None) -> str | None:
    with connect() as conn:
        row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default


def set_meta(key: str, value: str) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO meta(key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )


def list_jurisdictions(
    status: str | None = None,
    voice_only: bool = False,
) -> list[dict[str, Any]]:
    q = "SELECT * FROM jurisdictions"
    clauses: list[str] = []
    params: list[Any] = []

    if status and status != "all":
        if status == "hot":
            clauses.append("status_label IN ('proposed_hot', 'enacted_pending')")
        elif status == "in_force":
            clauses.append("status_label = 'in_force'")
        else:
            clauses.append("status_label = ?")
            params.append(status)

    if voice_only:
        clauses.append(
            "id IN (SELECT DISTINCT jurisdiction_id FROM obligations "
            "WHERE voice_cs_relevance IN ('high', 'medium'))"
        )

    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY CASE kind WHEN 'federal' THEN 0 WHEN 'state' THEN 1 ELSE 2 END, name"

    with connect() as conn:
        rows = conn.execute(q, params).fetchall()
        return [dict(r) for r in rows]


def get_jurisdiction_by_code(code: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM jurisdictions WHERE code = ?", (code.upper(),)
        ).fetchone()
        return row_to_dict(row)


def get_obligations(jurisdiction_id: int) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM obligations WHERE jurisdiction_id = ? ORDER BY id",
            (jurisdiction_id,),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["themes"] = parse_themes(d.get("themes"))
            out.append(d)
        return out


def get_sources(
    jurisdiction_id: int | None = None,
    obligation_id: int | None = None,
) -> list[dict[str, Any]]:
    with connect() as conn:
        if obligation_id is not None:
            rows = conn.execute(
                "SELECT * FROM sources WHERE obligation_id = ? ORDER BY id",
                (obligation_id,),
            ).fetchall()
        elif jurisdiction_id is not None:
            rows = conn.execute(
                "SELECT * FROM sources WHERE jurisdiction_id = ? "
                "OR obligation_id IN (SELECT id FROM obligations WHERE jurisdiction_id = ?) "
                "ORDER BY id",
                (jurisdiction_id, jurisdiction_id),
            ).fetchall()
        else:
            rows = []
        return [dict(r) for r in rows]


def get_history(jurisdiction_id: int) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM history_events WHERE jurisdiction_id = ? "
            "ORDER BY event_date DESC, id DESC",
            (jurisdiction_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def list_all_history_events() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT h.*, j.code AS jurisdiction_code, j.name AS jurisdiction_name "
            "FROM history_events h "
            "JOIN jurisdictions j ON j.id = h.jurisdiction_id "
            "ORDER BY h.event_date ASC, h.id ASC"
        ).fetchall()
        return [dict(r) for r in rows]


def compute_stats() -> dict[str, int]:
    """Top-level counts for home stats cards."""
    with connect() as conn:
        by_label = {
            r["status_label"]: r["c"]
            for r in conn.execute(
                "SELECT status_label, COUNT(*) AS c FROM jurisdictions GROUP BY status_label"
            )
        }
        voice_high = conn.execute(
            "SELECT COUNT(*) AS c FROM obligations WHERE voice_cs_relevance = 'high'"
        ).fetchone()["c"]
        voice_juris = conn.execute(
            "SELECT COUNT(DISTINCT jurisdiction_id) AS c FROM obligations "
            "WHERE voice_cs_relevance IN ('high', 'medium')"
        ).fetchone()["c"]
    return {
        "in_force": by_label.get("in_force", 0),
        "enacted_pending": by_label.get("enacted_pending", 0),
        "proposed_hot": by_label.get("proposed_hot", 0),
        "watch": by_label.get("watch", 0),
        "quiet": by_label.get("quiet", 0),
        "voice_high": voice_high,
        "voice_jurisdictions": voice_juris,
        "total": sum(by_label.values()),
    }


_SEED_HISTORY_TITLE_MARKERS = (
    "baseline snapshot",
    "baseline seeded",
    "seed housekeeping",
    "tracker audit",
)


def _is_seed_history(title: str | None, event_kind: str | None) -> bool:
    """True for housekeeping/seed rows that must not drive the activity chart."""
    kind = (event_kind or "milestone").strip().lower()
    if kind in {"seed_meta", "seed", "audit", "housekeeping"}:
        return True
    t = (title or "").strip().lower()
    return any(m in t for m in _SEED_HISTORY_TITLE_MARKERS)


def activity_by_month(months: int = 24) -> list[dict[str, Any]]:
    """Milestones & effective dates by YYYY-MM (excludes seed/audit history).

    Counts:
      (a) history_events with real legislative/regulatory dates (event_kind
          milestone/enacted/enforcement/etc., not seed_meta), and
      (b) obligation effective_date values.
    Seed/baseline housekeeping rows are never counted.
    """
    counter: Counter[str] = Counter()
    with connect() as conn:
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(history_events)")}
        if "event_kind" in cols:
            hist_sql = "SELECT event_date, title, event_kind FROM history_events"
        else:
            hist_sql = "SELECT event_date, title, NULL AS event_kind FROM history_events"
        for row in conn.execute(hist_sql):
            if _is_seed_history(row["title"], row["event_kind"]):
                continue
            d = (row["event_date"] or "")[:7]
            if len(d) == 7 and d[4] == "-":
                counter[d] += 1
        for row in conn.execute(
            "SELECT effective_date FROM obligations WHERE effective_date IS NOT NULL"
        ):
            d = (row["effective_date"] or "")[:7]
            if len(d) == 7 and d[4] == "-":
                counter[d] += 1

    if not counter:
        return []

    # Build contiguous month range covering last `months` ending at max key or today
    keys = sorted(counter.keys())
    end = keys[-1]
    y, m = int(end[:4]), int(end[5:7])
    series: list[dict[str, Any]] = []
    for _ in range(months):
        series.append({"month": f"{y:04d}-{m:02d}", "count": counter.get(f"{y:04d}-{m:02d}", 0)})
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    series.reverse()
    # Trim leading zeros
    while series and series[0]["count"] == 0:
        series.pop(0)
    return series


def jurisdiction_detail(code: str) -> dict[str, Any] | None:
    j = get_jurisdiction_by_code(code)
    if not j:
        return None
    obligations = get_obligations(j["id"])
    for obl in obligations:
        obl["sources"] = get_sources(obligation_id=obl["id"])
    return {
        "jurisdiction": j,
        "obligations": obligations,
        "sources": get_sources(jurisdiction_id=j["id"]),
        "history": get_history(j["id"]),
    }


def _obl_voice_fields(obl: dict[str, Any]) -> tuple[str, str]:
    """Accept new or legacy ingest keys."""
    rel = obl.get("voice_cs_relevance")
    if rel is None:
        rel = obl.get("ellavox_relevance", "none")
    why = obl.get("voice_cs_why")
    if why is None:
        why = obl.get("ellavox_why", "")
    return rel or "none", why or ""


def upsert_from_ingest(payload: dict[str, Any]) -> dict[str, Any]:
    """Upsert jurisdiction + related rows from a monthly ingest payload."""
    ensure_db()
    code = payload["code"].upper()
    with connect() as conn:
        existing = conn.execute(
            "SELECT id FROM jurisdictions WHERE code = ?", (code,)
        ).fetchone()

        fields = {
            "name": payload.get("name"),
            "kind": payload.get("kind"),
            "status_color": payload.get("status_color") or payload.get("status_label"),
            "status_label": payload.get("status_label"),
            "summary": payload.get("summary"),
            "last_reviewed": payload.get("last_reviewed"),
            "notes": payload.get("notes"),
        }

        if existing:
            jid = existing["id"]
            sets = []
            vals: list[Any] = []
            for k, v in fields.items():
                if v is not None:
                    sets.append(f"{k} = ?")
                    vals.append(v)
            if sets:
                vals.append(jid)
                conn.execute(
                    f"UPDATE jurisdictions SET {', '.join(sets)} WHERE id = ?",
                    vals,
                )
        else:
            if not fields["name"] or not fields["kind"]:
                raise ValueError("name and kind required when creating a jurisdiction")
            cur = conn.execute(
                "INSERT INTO jurisdictions "
                "(code, name, kind, status_color, status_label, summary, last_reviewed, notes) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    code,
                    fields["name"],
                    fields["kind"],
                    fields["status_color"] or "quiet",
                    fields["status_label"] or "quiet",
                    fields["summary"] or "",
                    fields["last_reviewed"],
                    fields["notes"] or "",
                ),
            )
            jid = cur.lastrowid

        created_obligations = 0
        for obl in payload.get("obligations") or []:
            themes = obl.get("themes") or []
            if isinstance(themes, list):
                themes_json = json.dumps(themes)
            else:
                themes_json = str(themes)
            rel, why = _obl_voice_fields(obl)
            cur = conn.execute(
                "INSERT INTO obligations "
                "(jurisdiction_id, title, status, effective_date, themes, "
                "voice_cs_relevance, voice_cs_why, summary) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    jid,
                    obl["title"],
                    obl.get("status", "proposed"),
                    obl.get("effective_date"),
                    themes_json,
                    rel,
                    why,
                    obl.get("summary", ""),
                ),
            )
            oid = cur.lastrowid
            created_obligations += 1
            for src in obl.get("sources") or []:
                conn.execute(
                    "INSERT INTO sources (obligation_id, label, url) VALUES (?, ?, ?)",
                    (oid, src["label"], src["url"]),
                )

        for src in payload.get("sources") or []:
            conn.execute(
                "INSERT INTO sources (jurisdiction_id, label, url) VALUES (?, ?, ?)",
                (jid, src["label"], src["url"]),
            )

        created_events = 0
        for ev in payload.get("history_events") or []:
            conn.execute(
                "INSERT INTO history_events "
                "(jurisdiction_id, event_date, title, detail, source_url, event_kind) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    jid,
                    ev["event_date"],
                    ev["title"],
                    ev.get("detail", ""),
                    ev.get("source_url"),
                    ev.get("event_kind") or "milestone",
                ),
            )
            created_events += 1

        if payload.get("last_global_refresh"):
            conn.execute(
                "INSERT INTO meta(key, value) VALUES ('last_global_refresh', ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (payload["last_global_refresh"],),
            )

        return {
            "code": code,
            "jurisdiction_id": jid,
            "obligations_added": created_obligations,
            "history_events_added": created_events,
        }
