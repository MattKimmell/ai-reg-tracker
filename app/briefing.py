"""Curated operator briefing for voice & conversation AI operators.

In-force rows get a short blurb. Coming-soon / pending rows are state + date only.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from app import db

AS_OF = date(2026, 9, 23)

BUCKET_META = {
    "in_force": {"label": "In force", "css": "status-in-force"},
    "coming_soon": {"label": "Coming soon", "css": "status-pending"},
    "pending": {"label": "Pending", "css": "status-hot"},
}


def _human_date(iso: str | None, fallback: str = "pending") -> str:
    if not iso:
        return fallback
    try:
        d = datetime.strptime(iso, "%Y-%m-%d").date()
    except ValueError:
        return iso
    return f"{d.strftime('%b')} {d.day}, {d.year}"


CURATED: list[dict[str, Any]] = [
    {
        "id": "fed-tcpa",
        "jurisdiction_code": "US-FED",
        "jurisdiction_label": "Federal",
        "topic": "Phone calls",
        "bucket": "in_force",
        "blurb": (
            "If you call cell phones with an AI voice, treat it like a robocall. "
            "You generally need written consent first. At the start of the call, "
            "say who is calling and give a real callback number. Caller ID does "
            "not need to say the call is AI."
        ),
        "obligation_match": "TCPA",
        "sort": 10,
    },
    {
        "id": "fed-ftc",
        "jurisdiction_code": "US-FED",
        "jurisdiction_label": "Federal",
        "topic": "Honesty about the bot",
        "bucket": "in_force",
        "blurb": (
            "Don't pretend the bot is a person, and don't oversell what the AI can do. "
            "That is already an FTC issue."
        ),
        "obligation_match": "FTC Act",
        "sort": 20,
    },
    {
        "id": "me-chatbot",
        "jurisdiction_code": "ME",
        "jurisdiction_label": "Maine",
        "topic": "Chatbot disclosure",
        "bucket": "in_force",
        "blurb": (
            "If a chatbot talks to Maine customers and could pass as a person, tell them "
            "it is AI. Text and voice both count."
        ),
        "obligation_match": "Required disclosure of AI chatbot",
        "sort": 30,
    },
    {
        "id": "ca-bot-act",
        "jurisdiction_code": "CA",
        "jurisdiction_label": "California",
        "topic": "Bot Act",
        "bucket": "in_force",
        "blurb": (
            "If a bot is trying to sell something online (or influence a vote), say it is a bot."
        ),
        "obligation_match": "California Bot Act",
        "sort": 40,
    },
    {
        "id": "ca-feha",
        "jurisdiction_code": "CA",
        "jurisdiction_label": "California",
        "topic": "Hiring AI",
        "bucket": "in_force",
        "blurb": (
            "If you or a customer use AI in hiring for California workers, employment AI "
            "rules already apply."
        ),
        "obligation_match": "FEHA automated-decision",
        "sort": 50,
    },
    {
        "id": "tx-traiga",
        "jurisdiction_code": "TX",
        "jurisdiction_label": "Texas",
        "topic": "Statewide AI law",
        "bucket": "in_force",
        "blurb": (
            "Texas already has a statewide AI law. Some uses are banned, and the attorney "
            "general can go after companies that develop or offer AI in the state."
        ),
        "obligation_match": "TRAIGA",
        "sort": 60,
    },
    {
        "id": "ut-disclosure",
        "jurisdiction_code": "UT",
        "jurisdiction_label": "Utah",
        "topic": "Say it is AI if asked",
        "bucket": "in_force",
        "blurb": (
            "If a Utah customer asks whether they are talking to AI, tell them. "
            "Some regulated jobs need you to say it up front."
        ),
        "obligation_match": "Utah AI Policy Act",
        "sort": 70,
    },
    {
        "id": "ct-wave1",
        "jurisdiction_code": "CT",
        "jurisdiction_label": "Connecticut",
        "topic": "",
        "bucket": "coming_soon",
        "blurb": "",
        "obligation_match": "first-wave AI / AEDT",
        "sort": 80,
    },
    {
        "id": "ct-wave2",
        "jurisdiction_code": "CT",
        "jurisdiction_label": "Connecticut",
        "topic": "",
        "bucket": "coming_soon",
        "blurb": "",
        "obligation_match": "AEDT interaction",
        "sort": 90,
    },
    {
        "id": "ca-admt",
        "jurisdiction_code": "CA",
        "jurisdiction_label": "California",
        "topic": "",
        "bucket": "coming_soon",
        "blurb": "",
        "obligation_match": "CCPA / CPRA ADMT",
        "sort": 100,
    },
    {
        "id": "co-admt",
        "jurisdiction_code": "CO",
        "jurisdiction_label": "Colorado",
        "topic": "",
        "bucket": "coming_soon",
        "blurb": "",
        "obligation_match": "SB 26-189",
        "sort": 110,
    },
    {
        "id": "ca-ab1609",
        "jurisdiction_code": "CA",
        "jurisdiction_label": "California",
        "topic": "",
        "bucket": "pending",
        "blurb": "",
        "obligation_match": "AB 1609",
        "date_fallback": "pending (governor)",
        "sort": 120,
    },
]


def _obligation_index() -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    db.ensure_db()
    for j in db.list_jurisdictions():
        detail = db.jurisdiction_detail(j["code"])
        if not detail:
            continue
        out[j["code"]] = detail.get("obligations") or []
    return out


def _match_obligation(
    obligations: list[dict[str, Any]], needle: str | None
) -> dict[str, Any] | None:
    if not needle:
        return None
    n = needle.lower()
    for o in obligations:
        title = (o.get("title") or "").lower()
        if n in title:
            return o
    return None


def _row_to_item(row: dict[str, Any], obl: dict[str, Any] | None) -> dict[str, Any]:
    bucket = row["bucket"]
    meta = BUCKET_META.get(bucket, BUCKET_META["coming_soon"])
    effective = (obl or {}).get("effective_date") or None
    fallback = row.get("date_fallback") or "pending"
    return {
        "id": row["id"],
        "jurisdiction_code": row["jurisdiction_code"],
        "jurisdiction_label": row["jurisdiction_label"],
        "topic": row.get("topic") or "",
        "bucket": bucket,
        "bucket_label": meta["label"],
        "bucket_css": meta["css"],
        "blurb": row.get("blurb") or "",
        "effective_date": effective,
        "date_display": _human_date(effective, fallback),
        "obligation_status": (obl or {}).get("status") or None,
        "sort": row["sort"],
    }


def build_briefing(as_of: date | None = None) -> dict[str, Any]:
    as_of = as_of or AS_OF
    by_code = _obligation_index()
    items: list[dict[str, Any]] = []
    for row in sorted(CURATED, key=lambda r: r["sort"]):
        obl = _match_obligation(
            by_code.get(row["jurisdiction_code"], []), row.get("obligation_match")
        )
        items.append(_row_to_item(row, obl))

    in_force = [i for i in items if i["bucket"] == "in_force"]
    coming_soon = [i for i in items if i["bucket"] == "coming_soon"]
    pending = [i for i in items if i["bucket"] == "pending"]

    return {
        "title": "What to know right now",
        "subtitle": "",
        "as_of": as_of.isoformat(),
        "disclaimer": "Not legal advice.",
        "in_force": in_force,
        "coming_soon": coming_soon,
        "pending": pending,
        "upcoming": coming_soon + pending,
        "items": items,
    }
