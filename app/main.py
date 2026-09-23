"""US AI Reg Tracker — FastAPI app."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app import db
from app import briefing

APP_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="US AI Reg Tracker",
    description="Operational briefing for US AI regulation status (federal + states + DC).",
    version="0.2.0",
)

app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

STATUS_META = {
    "in_force": {"label": "In force", "css": "status-in-force"},
    "enacted_pending": {"label": "Enacted / pending", "css": "status-pending"},
    "proposed_hot": {"label": "Proposed (hot)", "css": "status-hot"},
    "quiet": {"label": "Quiet", "css": "status-quiet"},
    "watch": {"label": "Watch", "css": "status-watch"},
}

RELEVANCE_META = {
    "high": {"label": "High", "css": "rel-high"},
    "medium": {"label": "Medium", "css": "rel-medium"},
    "low": {"label": "Low", "css": "rel-low"},
    "none": {"label": "None", "css": "rel-none"},
}



@app.on_event("startup")
def startup() -> None:
    db.ensure_db()


def _enrich_jurisdiction(j: dict[str, Any]) -> dict[str, Any]:
    out = dict(j)
    key = j.get("status_label") or "quiet"
    meta = STATUS_META.get(key, STATUS_META["quiet"])
    out["status_display"] = meta["label"]
    out["status_css"] = meta["css"]
    return out


def _parse_filter(filter: str) -> tuple[str | None, bool]:
    voice_only = filter in ("voice", "voice_cs")
    status = None
    if filter == "hot":
        status = "hot"
    elif filter == "in_force":
        status = "in_force"
    return status, voice_only


# --- HTML pages ---


@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    filter: str = Query("all", alias="filter"),
):
    status, voice_only = _parse_filter(filter)

    all_jurisdictions = [_enrich_jurisdiction(j) for j in db.list_jurisdictions()]
    jurisdictions = [_enrich_jurisdiction(j) for j in db.list_jurisdictions(
        status=status,
        voice_only=voice_only,
    )]
    federal = [j for j in jurisdictions if j["kind"] == "federal"]
    states = [j for j in jurisdictions if j["kind"] in ("state", "local")]
    refresh = db.get_meta("last_global_refresh", "—")
    stats = db.compute_stats()
    activity = db.activity_by_month(24)
    briefing_payload = briefing.build_briefing()

    # Map status payload for client-side SVG coloring (code → {name, status_css, status_display})
    map_status = {}
    for j in all_jurisdictions:
        if j["kind"] in ("state", "local"):
            map_status[j["code"]] = {
                "name": j["name"],
                "status_css": j["status_css"],
                "status_display": j["status_display"],
            }

    # Search index for client-side search (all jurisdictions + obligations)
    search_index = []
    for j in all_jurisdictions:
        detail = db.jurisdiction_detail(j["code"])
        obl_bits = []
        if detail:
            for o in detail["obligations"]:
                obl_bits.append(o.get("title") or "")
                obl_bits.extend(o.get("themes") or [])
                obl_bits.append(o.get("summary") or "")
                obl_bits.append(o.get("voice_cs_why") or "")
        search_index.append({
            "code": j["code"],
            "name": j["name"],
            "kind": j["kind"],
            "status_label": j["status_label"],
            "text": " ".join([j["code"], j["name"], j.get("summary") or "", *obl_bits]).lower(),
        })

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "federal": federal,
            "states": states,
            "filter": filter,
            "last_refresh": refresh,
            "status_meta": STATUS_META,
            "total_count": len(jurisdictions),
            "stats": stats,
            "activity_json": json.dumps(activity),
            "search_index_json": json.dumps(search_index),
            "map_status_json": json.dumps(map_status),
            "briefing": briefing_payload,
        },
    )


@app.get("/j/{code}", response_class=HTMLResponse)
def jurisdiction_page(request: Request, code: str):
    detail = db.jurisdiction_detail(code)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Jurisdiction {code} not found")

    j = _enrich_jurisdiction(detail["jurisdiction"])
    obligations = []
    for obl in detail["obligations"]:
        o = dict(obl)
        rel = o.get("voice_cs_relevance") or "none"
        o["rel_display"] = RELEVANCE_META.get(rel, RELEVANCE_META["none"])["label"]
        o["rel_css"] = RELEVANCE_META.get(rel, RELEVANCE_META["none"])["css"]
        obligations.append(o)

    return templates.TemplateResponse(
        "jurisdiction.html",
        {
            "request": request,
            "j": j,
            "obligations": obligations,
            "sources": detail["sources"],
            "history": detail["history"],
            "status_meta": STATUS_META,
        },
    )


@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "last_refresh": db.get_meta("last_global_refresh", "—"),
        },
    )


# --- JSON API ---


@app.get("/api/jurisdictions")
def api_list_jurisdictions(
    filter: str | None = Query(None),
):
    f = filter or "all"
    status, voice_only = _parse_filter(f)
    if f not in ("all", "hot", "in_force", "voice", "voice_cs") and f:
        status = f
        voice_only = False

    return {
        "last_global_refresh": db.get_meta("last_global_refresh"),
        "stats": db.compute_stats(),
        "jurisdictions": db.list_jurisdictions(status=status, voice_only=voice_only),
    }


@app.get("/api/stats")
def api_stats():
    return {
        "last_global_refresh": db.get_meta("last_global_refresh"),
        "stats": db.compute_stats(),
        "activity": db.activity_by_month(24),
    }


@app.get("/api/jurisdictions/{code}")
def api_jurisdiction(code: str):
    detail = db.jurisdiction_detail(code)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Jurisdiction {code} not found")
    return detail


class SourceIn(BaseModel):
    label: str
    url: str


class ObligationIn(BaseModel):
    title: str
    status: str = "proposed"
    effective_date: str | None = None
    themes: list[str] = Field(default_factory=list)
    voice_cs_relevance: str | None = None
    voice_cs_why: str | None = None
    # Legacy aliases accepted on ingest
    ellavox_relevance: str | None = None
    ellavox_why: str | None = None
    summary: str = ""
    sources: list[SourceIn] = Field(default_factory=list)


class HistoryIn(BaseModel):
    event_date: str
    title: str
    detail: str = ""
    source_url: str | None = None


class IngestPayload(BaseModel):
    code: str
    name: str | None = None
    kind: str | None = None
    status_color: str | None = None
    status_label: str | None = None
    summary: str | None = None
    last_reviewed: str | None = None
    notes: str | None = None
    obligations: list[ObligationIn] = Field(default_factory=list)
    sources: list[SourceIn] = Field(default_factory=list)
    history_events: list[HistoryIn] = Field(default_factory=list)
    last_global_refresh: str | None = None


@app.post("/api/ingest")
def api_ingest(payload: IngestPayload):
    """Upsert jurisdiction summary/status; append obligations, sources, history.

    No auth — local-only tiny app. Do not expose outside localhost.
    """
    try:
        result = db.upsert_from_ingest(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, **result}
