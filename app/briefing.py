"""Curated operator briefing for voice & conversation AI operators.

Plain-English rows for the home-page panel. Dates and obligation status are
cross-checked against tracker.db when available; blurbs stay curated so monthly
exports stay accurate without inventing effective dates.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from app import db

# Reference "now" for framing imminent dates in this seed era.
AS_OF = date(2026, 9, 23)

BUCKET_META = {
    "in_force": {"label": "In force", "css": "status-in-force"},
    "coming_soon": {"label": "Coming soon", "css": "status-pending"},
    "watch": {"label": "Watch", "css": "status-watch"},
    "pending": {"label": "Pending", "css": "status-hot"},
}

# Curated rows. `obligation_match` is a substring of obligation title used to
# pull live effective_date / status from the DB when present.
CURATED: list[dict[str, Any]] = [
    {
        "id": "fed-tcpa",
        "jurisdiction_code": "US-FED",
        "jurisdiction_label": "Federal",
        "topic": "Phone calls",
        "bucket": "in_force",
        "blurb": (
            "If you call cell phones with an AI voice, treat it like a robocall. "
            "You generally need written consent first, and the caller ID has to be honest."
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
            "That is already an FTC issue, not a future one."
        ),
        "obligation_match": "FTC Act",
        "sort": 20,
    },
    {
        "id": "fed-eo",
        "jurisdiction_code": "US-FED",
        "jurisdiction_label": "Federal",
        "topic": "Federal vs. states",
        "bucket": "watch",
        "blurb": (
            "Washington is talking about overriding state AI laws. That talk has not "
            "wiped out the state rules below — keep following them."
        ),
        "obligation_match": "EO 14365",
        "sort": 30,
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
        "sort": 40,
    },
    {
        "id": "ca-bot-act",
        "jurisdiction_code": "CA",
        "jurisdiction_label": "California",
        "topic": "Bot Act",
        "bucket": "in_force",
        "blurb": (
            "If a bot is trying to sell something online (or influence a vote), say it is a bot. "
            "Don't let people think they are talking to a person."
        ),
        "obligation_match": "California Bot Act",
        "sort": 50,
    },
    {
        "id": "ca-feha",
        "jurisdiction_code": "CA",
        "jurisdiction_label": "California",
        "topic": "Hiring AI",
        "bucket": "in_force",
        "blurb": (
            "If you or a customer use AI in hiring for California workers, employment AI "
            "rules already apply. Less relevant for day-to-day customer-service bots."
        ),
        "obligation_match": "FEHA automated-decision",
        "sort": 60,
    },
    {
        "id": "ca-admt",
        "jurisdiction_code": "CA",
        "jurisdiction_label": "California",
        "topic": "Automated decisions",
        "bucket": "coming_soon",
        "blurb": (
            "By 2027, if AI is making significant decisions about people — not just chatting — "
            "they get notice, a way to opt out, and a right to see what happened. "
            "Check whether any customer workflow is actually deciding, not just helping."
        ),
        "obligation_match": "CCPA / CPRA ADMT",
        "sort": 70,
    },
    {
        "id": "ca-ab1609",
        "jurisdiction_code": "CA",
        "jurisdiction_label": "California",
        "topic": "CS chatbot bill",
        "bucket": "pending",
        "blurb": (
            "A customer-service chatbot bill for larger companies is sitting with the "
            "governor (sent Sept 14). Not law yet — watch whether it is signed or vetoed."
        ),
        "obligation_match": "AB 1609",
        "sort": 80,
    },
    {
        "id": "ct-wave1",
        "jurisdiction_code": "CT",
        "jurisdiction_label": "Connecticut",
        "topic": "Decision tools (Oct 1)",
        "bucket": "coming_soon",
        "blurb": (
            "In a week, Connecticut starts treating automated decision tools more seriously. "
            "Using AI is not a shield if the outcome discriminates."
        ),
        "obligation_match": "first-wave AI / AEDT",
        "sort": 90,
    },
    {
        "id": "ct-wave2",
        "jurisdiction_code": "CT",
        "jurisdiction_label": "Connecticut",
        "topic": "Tell people it is AI",
        "bucket": "coming_soon",
        "blurb": (
            "A year later, new automated decision tools will need to tell people they are "
            "talking to AI and give written notice before a decision. More of a hiring-tool "
            "issue than a pure customer-service voice bot issue."
        ),
        "obligation_match": "AEDT interaction",
        "sort": 100,
    },
    {
        "id": "co-admt",
        "jurisdiction_code": "CO",
        "jurisdiction_label": "Colorado",
        "topic": "Leases and big decisions",
        "bucket": "coming_soon",
        "blurb": (
            "In 2027, automated decisions that matter — including whether someone gets a "
            "lease — come with extra duties. Important if bots help with property leasing."
        ),
        "obligation_match": "SB 26-189",
        "sort": 110,
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
        "sort": 120,
    },
    {
        "id": "ut-disclosure",
        "jurisdiction_code": "UT",
        "jurisdiction_label": "Utah",
        "topic": "AI Policy Act",
        "bucket": "in_force",
        "blurb": (
            "If a Utah customer asks whether they are talking to AI, tell them. "
            "Some regulated jobs need you to say it up front."
        ),
        "obligation_match": "Utah AI Policy Act",
        "sort": 130,
    },
    {
        "id": "il-employment",
        "jurisdiction_code": "IL",
        "jurisdiction_label": "Illinois",
        "topic": "Employment AI",
        "bucket": "watch",
        "blurb": (
            "If anyone uses AI on video interviews of Illinois candidates, they need notice "
            "and consent. Not a day-to-day customer-service bot rule."
        ),
        "obligation_match": "Artificial Intelligence Video Interview",
        "sort": 140,
    },
    {
        "id": "nyc-ll144",
        "jurisdiction_code": "NY",
        "jurisdiction_label": "NYC / NY",
        "topic": "Local Law 144",
        "bucket": "watch",
        "blurb": (
            "If AI is used to hire in New York City, it needs a bias audit and the candidate "
            "has to be told. Hiring-adjacent, not a customer-service bot rule."
        ),
        "obligation_match": "NYC Local Law 144",
        "sort": 150,
    },
]


def _obligation_index() -> dict[str, list[dict[str, Any]]]:
    """Map jurisdiction code → obligations (for live date/status cross-check)."""
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


def build_briefing(as_of: date | None = None) -> dict[str, Any]:
    """Build exportable briefing payload with curated blurbs + live dates."""
    as_of = as_of or AS_OF
    by_code = _obligation_index()
    items: list[dict[str, Any]] = []

    for row in sorted(CURATED, key=lambda r: r["sort"]):
        bucket = row["bucket"]
        meta = BUCKET_META.get(bucket, BUCKET_META["watch"])
        obl = _match_obligation(
            by_code.get(row["jurisdiction_code"], []), row.get("obligation_match")
        )
        effective = (obl or {}).get("effective_date") or None
        obl_status = (obl or {}).get("status") or None

        items.append(
            {
                "id": row["id"],
                "jurisdiction_code": row["jurisdiction_code"],
                "jurisdiction_label": row["jurisdiction_label"],
                "topic": row["topic"],
                "bucket": bucket,
                "bucket_label": meta["label"],
                "bucket_css": meta["css"],
                "blurb": row["blurb"],
                "effective_date": effective,
                "obligation_status": obl_status,
                "sort": row["sort"],
            }
        )

    return {
        "title": "Operator briefing — what to know right now",
        "subtitle": (
            "What matters now if you run voice, SMS, or chat AI that talks to customers "
            "and gets work done."
        ),
        "as_of": as_of.isoformat(),
        "disclaimer": "Operational briefing · Not legal advice · Confirm against primary sources.",
        "items": items,
    }
