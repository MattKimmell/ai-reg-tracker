#!/usr/bin/env python3
"""Seed baseline US AI Reg Tracker data (as of 2026-09-22)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import db  # noqa: E402

BASELINE_DATE = "2026-09-22"

STATES = [
    ("AL", "Alabama"),
    ("AK", "Alaska"),
    ("AZ", "Arizona"),
    ("AR", "Arkansas"),
    ("CA", "California"),
    ("CO", "Colorado"),
    ("CT", "Connecticut"),
    ("DE", "Delaware"),
    ("DC", "District of Columbia"),
    ("FL", "Florida"),
    ("GA", "Georgia"),
    ("HI", "Hawaii"),
    ("ID", "Idaho"),
    ("IL", "Illinois"),
    ("IN", "Indiana"),
    ("IA", "Iowa"),
    ("KS", "Kansas"),
    ("KY", "Kentucky"),
    ("LA", "Louisiana"),
    ("ME", "Maine"),
    ("MD", "Maryland"),
    ("MA", "Massachusetts"),
    ("MI", "Michigan"),
    ("MN", "Minnesota"),
    ("MS", "Mississippi"),
    ("MO", "Missouri"),
    ("MT", "Montana"),
    ("NE", "Nebraska"),
    ("NV", "Nevada"),
    ("NH", "New Hampshire"),
    ("NJ", "New Jersey"),
    ("NM", "New Mexico"),
    ("NY", "New York"),
    ("NC", "North Carolina"),
    ("ND", "North Dakota"),
    ("OH", "Ohio"),
    ("OK", "Oklahoma"),
    ("OR", "Oregon"),
    ("PA", "Pennsylvania"),
    ("RI", "Rhode Island"),
    ("SC", "South Carolina"),
    ("SD", "South Dakota"),
    ("TN", "Tennessee"),
    ("TX", "Texas"),
    ("UT", "Utah"),
    ("VT", "Vermont"),
    ("VA", "Virginia"),
    ("WA", "Washington"),
    ("WV", "West Virginia"),
    ("WI", "Wisconsin"),
    ("WY", "Wyoming"),
]

# Priority overrides: code -> jurisdiction fields + obligations
PRIORITY: dict[str, dict] = {
    "US-FED": {
        "name": "United States (Federal)",
        "kind": "federal",
        "status_label": "watch",
        "status_color": "watch",
        "summary": (
            "No comprehensive federal AI statute. Sector rules (TCPA synthetic voice, "
            "FTC §5) remain the primary constraints for voice/conversation AI operators. EO 14365 advances a "
            "preemption narrative but does not repeal state AI laws."
        ),
        "notes": (
            "Monitor FCC TCPA voice-AI consent, FTC deceptive-claims enforcement, "
            "and any congressional preemption vehicle. State disclosure/ADMT laws "
            "remain operative unless Congress acts."
        ),
        "obligations": [
            {
                "title": "TCPA — artificial / prerecorded voice (incl. AI synthetic voice)",
                "status": "in_force",
                "effective_date": None,
                "themes": ["voice_tcpa", "disclosure"],
                "voice_cs_relevance": "high",
                "voice_cs_why": (
                    "Phone AI and voice agents use synthetic speech; FCC confirms AI-generated "
                    "voices are artificial/prerecorded under TCPA — prior express "
                    "consent and caller-ID rules apply."
                ),
                "summary": (
                    "FCC Declaratory Ruling (FCC 24-17) confirms that AI technologies "
                    "generating human voices are 'artificial or prerecorded' under the "
                    "TCPA. Autodialed/prerecorded calls to cell phones generally require "
                    "prior express written consent (marketing) or prior express consent "
                    "(informational), plus identification requirements."
                ),
                "sources": [
                    {
                        "label": "FCC 24-17 Declaratory Ruling (PDF)",
                        "url": "https://docs.fcc.gov/public/attachments/FCC-24-17A1.pdf",
                    },
                    {
                        "label": "FCC statement — TCPA applies to AI voices",
                        "url": "https://docs.fcc.gov/public/attachments/FCC-24-17A1.pdf",
                    },
                ],
            },
            {
                "title": "FTC Act §5 — unfair or deceptive acts (claims & disclosure)",
                "status": "in_force",
                "effective_date": None,
                "themes": ["disclosure", "governance", "other"],
                "voice_cs_relevance": "high",
                "voice_cs_why": (
                    "Marketing and product claims about AI capabilities, human vs bot "
                    "identity, and call outcomes must not mislead customers or end consumers."
                ),
                "summary": (
                    "Section 5 prohibits unfair or deceptive acts or practices in commerce. "
                    "Applies to AI-related advertising, capability claims, and failure to "
                    "disclose material facts about automated interactions."
                ),
                "sources": [
                    {
                        "label": "FTC — Mission / Section 5 overview",
                        "url": "https://www.ftc.gov/news-events/news/press-releases/2025/09/ftc-launches-inquiry-ai-chatbots-acting-companions",
                    },
                    {
                        "label": "15 U.S.C. §45 (Cornell LII)",
                        "url": "https://www.law.cornell.edu/uscode/text/15/45",
                    },
                ],
            },
            {
                "title": "EO 14365 — Ensuring a National Policy Framework for AI",
                "status": "in_force",
                "effective_date": "2025-12-11",
                "themes": ["governance"],
                "voice_cs_relevance": "medium",
                "voice_cs_why": (
                    "Signals federal interest in preempting or challenging state AI laws; "
                    "does not itself wipe out state disclosure/ADMT obligations voice/conversation AI operators face today."
                ),
                "summary": (
                    "Executive Order 14365 (Dec 2025) directs agencies to evaluate 'onerous' "
                    "state AI laws, consider litigation/funding levers, and recommend a "
                    "uniform federal framework. It pushes a preemption narrative but does "
                    "not repeal existing state statutes."
                ),
                "sources": [
                    {
                        "label": "Federal Register — EO 14365",
                        "url": "https://www.federalregister.gov/documents/2025/12/16/2025-23092/ensuring-a-national-policy-framework-for-artificial-intelligence",
                    },
                    {
                        "label": "Congress.gov — federal legislation search",
                        "url": "https://www.law.cornell.edu/uscode/text/47/227",
                    },
                ],
            },
        ],
        "sources": [
            {
                "label": "NCSL Artificial Intelligence legislation database",
                "url": "https://www.ncsl.org/financial-services/artificial-intelligence-legislation-database",
            },
        ],
    },
    "ME": {
        "name": "Maine",
        "kind": "state",
        "status_label": "in_force",
        "status_color": "in_force",
        "summary": (
            "Enacted chatbot disclosure law (PL 2025, c. 294): clear and conspicuous "
            "notice required when AI chatbots engage consumers in trade/commerce in a "
            "way that may mislead them into believing they are talking to a human. "
            "High relevance for customer-service bots and phone AI."
        ),
        "notes": "Codified at 10 M.R.S. §1500-DD (realloc. from §1500-Y). UTPA enforcement.",
        "obligations": [
            {
                "title": "Required disclosure of AI chatbot use in trade/commerce (10 M.R.S. §1500-DD)",
                "status": "in_force",
                "effective_date": "2025-09-24",
                "themes": ["disclosure", "companion_cs"],
                "voice_cs_relevance": "high",
                "voice_cs_why": (
                    "Directly covers textual or aural AI chatbots used with Maine consumers; "
                    "Customer-service and voice bots must disclose when a reasonable consumer "
                    "could think they are talking to a human."
                ),
                "summary": (
                    "LD 1727 / Public Law 2025 ch. 294 (approved June 12, 2025; generally "
                    "effective September 24, 2025). A person may not use an AI chatbot "
                    "or other computer technology to engage in trade and commerce with a "
                    "consumer in a manner that may mislead a reasonable consumer into "
                    "believing they are engaging with a human, unless notified clearly and "
                    "conspicuously. Violation = Maine Unfair Trade Practices Act."
                ),
                "sources": [
                    {
                        "label": "Statute — 10 M.R.S. §1500-DD",
                        "url": "https://www.mainelegislature.org/legis/statutes/10/title10sec1500-DD.html",
                    },
                    {
                        "label": "LD 1727 bill status (legislature)",
                        "url": "https://legislature.maine.gov/legis/bills/display_ps.asp?ld=1727",
                    },
                ],
            },
        ],
    },
    "CA": {
        "name": "California",
        "kind": "state",
        "status_label": "enacted_pending",
        "status_color": "enacted_pending",
        "summary": (
            "Dense AI stack: existing Bot Act disclosure, FEHA ADS employment rules, "
            "CCPA ADMT regs (compliance runway into 2027), and AB 1609 (customer-service "
            "chatbots) enrolled and presented to the Governor 2026-09-14 — outcome pending "
            "as of baseline."
        ),
        "notes": (
            "AB 1609 was on the Governor's desk as of 2026-09-22; do not assume chaptered "
            "until confirmed. CCPA ADMT significant-decision duties generally phase by 2027."
        ),
        "obligations": [
            {
                "title": "California Bot Act — deceptive bot disclosure (B&P §§17940–17941)",
                "status": "in_force",
                "effective_date": "2019-07-01",
                "themes": ["disclosure"],
                "voice_cs_relevance": "high",
                "voice_cs_why": (
                    "Requires disclosure when bots communicate online with intent to "
                    "incentivize a purchase or influence a vote; relevant to CS/sales bots."
                ),
                "summary": (
                    "Prohibits use of a bot to communicate or interact with another person "
                    "online with intent to mislead about artificial identity in order to "
                    "incentivize a purchase or influence a vote, unless the bot discloses "
                    "it is a bot."
                ),
                "sources": [
                    {
                        "label": "Cal. Bus. & Prof. Code §17941 (Justia)",
                        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=BPC&sectionNum=17941",
                    },
                    {
                        "label": "NCSL AI legislation database (landing)",
                        "url": "https://www.ncsl.org/financial-services/artificial-intelligence-legislation-database",
                    },
                ],
            },
            {
                "title": "CCPA / CPRA ADMT regulations (significant decisions)",
                "status": "enacted_pending",
                "effective_date": "2027-01-01",
                "themes": ["admt_employment", "admt_housing", "governance", "disclosure"],
                "voice_cs_relevance": "medium",
                "voice_cs_why": (
                    "If operators or their customers use ADMT for significant decisions about CA "
                    "consumers, notice/opt-out/access duties apply; more relevant for "
                    "customer ADMT than core voice/conversation CS products."
                ),
                "summary": (
                    "CPPA ADMT regulations (adopted 2025; general effective date 2026-01-01) "
                    "require pre-use notices, opt-outs, and access rights when ADMT "
                    "substantially replaces human decisionmaking for significant decisions. "
                    "Existing uses generally must comply by 2027-01-01."
                ),
                "sources": [
                    {
                        "label": "California Privacy Protection Agency",
                        "url": "https://cppa.ca.gov/regulations/ccpa_updates.html",
                    },
                ],
            },
            {
                "title": "AB 1609 — Customer service chatbots (pending Governor)",
                "status": "proposed",
                "effective_date": None,
                "themes": ["disclosure", "companion_cs"],
                "voice_cs_relevance": "high",
                "voice_cs_why": (
                    "Would impose human-agent access and related CS chatbot duties on large "
                    "private businesses — directly in the customer-service / phone AI lane if enacted."
                ),
                "summary": (
                    "AB 1609 (2025–2026) would add B&P Ch. 22.6.1 on customer-service "
                    "chatbots for large private businesses. Enrolled and presented to the "
                    "Governor 2026-09-14. As of baseline 2026-09-22, final outcome "
                    "(signed/vetoed) not confirmed — treat as pending, not in force."
                ),
                "sources": [
                    {
                        "label": "AB 1609 bill status (LegInfo)",
                        "url": "https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202520260AB1609",
                    },
                    {
                        "label": "AB 1609 bill text (LegInfo)",
                        "url": "https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202520260AB1609",
                    },
                ],
            },
            {
                "title": "FEHA automated-decision systems (employment)",
                "status": "in_force",
                "effective_date": "2025-10-01",
                "themes": ["admt_employment"],
                "voice_cs_relevance": "low",
                "voice_cs_why": (
                    "Employment ADS rules matter if operators or customers use AI in hiring; "
                    "not core to phone/CS voice products."
                ),
                "summary": (
                    "Civil Rights Council FEHA regulations address automated-decision "
                    "systems in employment, including discrimination theories even when a "
                    "human remains involved. Operative Oct 2025 (Register 2025, No. 26)."
                ),
                "sources": [
                    {
                        "label": "CA Civil Rights Department",
                        "url": "https://calcivilrights.ca.gov/2025/06/30/civil-rights-council-secures-approval-for-regulations-to-protect-against-employment-discrimination-related-to-artificial-intelligence/",
                    },
                ],
            },
        ],
    },
    "TX": {
        "name": "Texas",
        "kind": "state",
        "status_label": "in_force",
        "status_color": "in_force",
        "summary": (
            "TRAIGA (HB 149) — Texas Responsible AI Governance Act — effective "
            "2026-01-01. Broad governance and prohibited-use framework with AG "
            "enforcement; medium-high relevance for voice/conversation AI operators deploying in Texas."
        ),
        "notes": "Exclusive AG enforcement; cure period; sandbox and AI Council created.",
        "obligations": [
            {
                "title": "TRAIGA — Texas Responsible AI Governance Act (HB 149)",
                "status": "in_force",
                "effective_date": "2026-01-01",
                "themes": ["governance", "disclosure"],
                "voice_cs_relevance": "medium",
                "voice_cs_why": (
                    "Applies to developing/deploying/offering AI in Texas; prohibited "
                    "manipulative uses and government disclosure rules. Moderate product "
                    "impact; watch AG guidance and federal-preemption overlay."
                ),
                "summary": (
                    "HB 149 signed 2025-06-22 (effective 2026-01-01). Creates Business & "
                    "Commerce Code Ch. 552 AI protections (prohibited manipulation, social "
                    "scoring limits, discrimination, etc.), a regulatory sandbox, and the "
                    "Texas AI Council. Civil penalties; no private right of action for most "
                    "provisions."
                ),
                "sources": [
                    {
                        "label": "HB 149 enrolled text (Texas Legislature)",
                        "url": "https://capitol.texas.gov/tlodocs/89R/billtext/html/HB00149F.htm",
                    },
                    {
                        "label": "HB 149 bill history",
                        "url": "https://capitol.texas.gov/BillLookup/history.aspx?Bill=HB149&LegSess=89R",
                    },
                ],
            },
        ],
    },
    "IL": {
        "name": "Illinois",
        "kind": "state",
        "status_label": "watch",
        "status_color": "watch",
        "summary": (
            "Employment-focused AI rules (video interview notice; broader AI employment "
            "notice/anti-bias themes). Medium relevance — voice/conversation CS operators are not primarily a "
            "hiring-tool vendor, but customers may ask."
        ),
        "notes": "Track IDHR guidance; detailed proposed notice regs were in flux mid-2026.",
        "obligations": [
            {
                "title": "Artificial Intelligence Video Interview Act + employment AI notice themes",
                "status": "in_force",
                "effective_date": "2020-01-01",
                "themes": ["admt_employment", "disclosure"],
                "voice_cs_relevance": "medium",
                "voice_cs_why": (
                    "Customers evaluating AI for hiring workflows may ask CS/voice vendors about IL "
                    "notice/consent obligations; not core to voice CS workers."
                ),
                "summary": (
                    "Illinois requires notice/consent when AI analyzes video interviews, "
                    "and has expanded employment-AI notice and anti-discrimination themes "
                    "(including HB 3773-era discussions). Prefer live ILGA statute text "
                    "over secondary summaries when advising customers."
                ),
                "sources": [
                    {
                        "label": "AI Video Interview Act (ILCS via ILGA)",
                        "url": "https://ilga.gov/legislation/ilcs/ilcs3.asp?ActID=4015&ChapterID=68",
                    },
                    {
                        "label": "ILGA legislation search (landing)",
                        "url": "https://ilga.gov/legislation/",
                    },
                ],
            },
        ],
    },
    "NY": {
        "name": "New York",
        "kind": "state",
        "status_label": "watch",
        "status_color": "watch",
        "summary": (
            "NYC Local Law 144 (AEDT hiring bias audits) is the main in-force local rule. "
            "State-level AI bills remain a watch item. Low–medium for core voice/CS products; "
            "higher if customers use AEDT in NYC hiring."
        ),
        "notes": "NYC LL144 is local (NYC); tracked under NY state card for discoverability.",
        "obligations": [
            {
                "title": "NYC Local Law 144 — Automated Employment Decision Tools",
                "status": "in_force",
                "effective_date": "2023-07-05",
                "themes": ["admt_employment"],
                "voice_cs_relevance": "low",
                "voice_cs_why": (
                    "Hiring-tool bias audits and candidate notice — peripheral to "
                    "voice/CS product; watch if product expands into HR workflows."
                ),
                "summary": (
                    "Requires independent bias audits, public summaries, and candidate "
                    "notice before using covered automated employment decision tools in NYC."
                ),
                "sources": [
                    {
                        "label": "NYC DCWP — AEDT / Local Law 144",
                        "url": "https://www.nyc.gov/site/dca/about/automated-employment-decision-tools.page",
                    },
                ],
            },
        ],
    },
    "UT": {
        "name": "Utah",
        "kind": "state",
        "status_label": "in_force",
        "status_color": "in_force",
        "summary": (
            "Utah AI Policy Act framework: generative AI disclosure on clear consumer "
            "request; heightened/proactive disclosure for regulated occupations in "
            "high-risk interactions. Medium relevance for customer-service bots and phone AI."
        ),
        "notes": "Subsequent amendments (e.g. SB 226 / SB 332 era) refine disclosure and chatbot rules — confirm current code when advising.",
        "obligations": [
            {
                "title": "Utah AI Policy Act — generative AI disclosure on request",
                "status": "in_force",
                "effective_date": "2024-05-01",
                "themes": ["disclosure", "companion_cs"],
                "voice_cs_relevance": "medium",
                "voice_cs_why": (
                    "CS and voice bots serving Utah consumers should honor clear requests "
                    "to disclose generative AI use; regulated-occupation rules may require "
                    "prominent disclosure in sensitive contexts."
                ),
                "summary": (
                    "SB 149 (2024) and follow-on amendments require businesses to disclose "
                    "generative AI use upon clear and unambiguous consumer request, with "
                    "stronger duties for certain regulated occupations and high-risk "
                    "interactions (including mental-health chatbot themes in later bills)."
                ),
                "sources": [
                    {
                        "label": "Utah SB 149 (2024) bill text",
                        "url": "https://le.utah.gov/~2024/bills/sbillint/SB0149.htm",
                    },
                    {
                        "label": "Utah Legislature bill search (landing)",
                        "url": "https://le.utah.gov/",
                    },
                ],
            },
        ],
    },
    "CT": {
        "name": "Connecticut",
        "kind": "state",
        "status_label": "proposed_hot",
        "status_color": "proposed_hot",
        "summary": (
            "Public Act 26-15 (Online Safety / AI Responsibility & Transparency) — "
            "broad AI statute with phased effective dates. First wave Oct 1 2026; core "
            "AEDT interaction/pre-decision disclosures Oct 1 2027. High watch for voice/conversation AI."
        ),
        "notes": (
            "Split effective dates (verified against PA 26-15 text): Oct 1 2026 first-wave "
            "framework / anti-discrimination; Jan 1 2027 AI companion safeguards; "
            "Oct 1 2027 AEDT interaction & pre-decision disclosures for tools deployed on/"
            "after that date. Confirm companion/CS-bot scope against PA text."
        ),
        "obligations": [
            {
                "title": "PA 26-15 — first-wave AI / AEDT framework (anti-discrimination & scaffolding)",
                "status": "enacted_pending",
                "effective_date": "2026-10-01",
                "themes": ["disclosure", "admt_employment", "governance"],
                "voice_cs_relevance": "high",
                "voice_cs_why": (
                    "First wave includes AEDT statutory framework and the rule that AI use "
                    "is not a defense to discrimination; relevant watch for CS/voice vendors "
                    "serving CT employers and for companion/online-safety themes in the Act."
                ),
                "summary": (
                    "Substitute SB 5 / Public Act 26-15. Effective Oct 1 2026: AEDT definitions "
                    "and related employment framework provisions, including that use of "
                    "automated employment-related decision technology is not a defense to "
                    "discrimination claims (and related WARN/AI-layoff disclosure themes). "
                    "Core interaction/pre-decision disclosure duties for AEDTs deployed on/"
                    "after Oct 1 2027 are tracked as a separate obligation."
                ),
                "sources": [
                    {
                        "label": "PA 26-15 official PDF (CGA)",
                        "url": "https://www.cga.ct.gov/2026/ACT/PA/PDF/2026PA-00015-R00SB-00005-PA.PDF",
                    },
                    {
                        "label": "Connecticut General Assembly",
                        "url": "https://www.cga.ct.gov/",
                    },
                ],
            },
            {
                "title": "PA 26-15 — AEDT interaction & pre-decision disclosures",
                "status": "enacted_pending",
                "effective_date": "2027-10-01",
                "themes": ["disclosure", "admt_employment"],
                "voice_cs_relevance": "medium",
                "voice_cs_why": (
                    "Plain-language interaction disclosure and written pre-decision notice "
                    "apply to AEDTs deployed on/after Oct 1 2027 — material for hiring-tool "
                    "customers; secondary for pure CS voice bots."
                ),
                "summary": (
                    "For automated employment-related decision technology deployed on or after "
                    "October 1, 2027: deployers must disclose interactions in plain language "
                    "(unless obvious) and provide written pre-decision notice covering purpose, "
                    "trade name, personal-data categories/sources, and contact information. "
                    "Developer information-sharing duties support these deployer obligations."
                ),
                "sources": [
                    {
                        "label": "PA 26-15 official PDF (CGA)",
                        "url": "https://www.cga.ct.gov/2026/ACT/PA/PDF/2026PA-00015-R00SB-00005-PA.PDF",
                    },
                ],
            },
        ],
    },
    "CO": {
        "name": "Colorado",
        "kind": "state",
        "status_label": "enacted_pending",
        "status_color": "enacted_pending",
        "summary": (
            "SB 26-189 ADMT framework effective Jan 1 2027 for consequential decisions "
            "including residential lease/purchase. High for AppFolio/PM vertical. "
            "Customer-service bots may fall outside covered ADMT when used under an "
            "acceptable-use pattern that does not materially influence lease decisions."
        ),
        "notes": (
            "SB 24-205 AI Act was repealed/replaced by SB 26-189 ADMT structure. Confirm "
            "AUP/exclusion language with counsel for CS bots that do not score/rank tenants."
        ),
        "obligations": [
            {
                "title": "SB 26-189 — ADMT in consequential decisions (incl. residential lease)",
                "status": "enacted_pending",
                "effective_date": "2027-01-01",
                "themes": ["admt_housing", "governance", "disclosure"],
                "voice_cs_relevance": "high",
                "voice_cs_why": (
                    "AppFolio/property-management customers face ADMT duties for lease "
                    "screening. Pure CS bots that do not materially influence lease "
                    "decisions may be out of scope — document AUP and use cases carefully."
                ),
                "summary": (
                    "SB 26-189 (signed May 2026) defines covered ADMT used to materially "
                    "influence consequential decisions, including lease/purchase of "
                    "residential real estate. Developer documentation + deployer notice and "
                    "post-adverse-outcome disclosures generally apply starting 2027-01-01. "
                    "AG rules for post-adverse disclosures due by that date."
                ),
                "sources": [
                    {
                        "label": "SB26-189 bill page (Colorado General Assembly)",
                        "url": "https://www.leg.colorado.gov/bills/sb26-189",
                    },
                    {
                        "label": "CO Division of Real Estate — SB26-189 summary",
                        "url": "https://www.leg.colorado.gov/bills/sb26-189",
                    },
                ],
            },
        ],
    },
}


def quiet_summary(name: str) -> str:
    return (
        f"{name}: no material AI service, disclosure, or ADMT rules currently "
        f"in focus. Monitor NCSL and local session activity; escalate if chatbot/"
        f"voice disclosure or housing ADMT bills advance."
    )


def insert_jurisdiction(conn, code, name, kind, status_label, summary, notes=""):
    cur = conn.execute(
        "INSERT INTO jurisdictions "
        "(code, name, kind, status_color, status_label, summary, last_reviewed, notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (code, name, kind, status_label, status_label, summary, BASELINE_DATE, notes),
    )
    return cur.lastrowid


def insert_obligation(conn, jid, obl):
    cur = conn.execute(
        "INSERT INTO obligations "
        "(jurisdiction_id, title, status, effective_date, themes, "
        "voice_cs_relevance, voice_cs_why, summary) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            jid,
            obl["title"],
            obl["status"],
            obl.get("effective_date"),
            json.dumps(obl.get("themes") or []),
            obl.get("voice_cs_relevance", "none"),
            obl.get("voice_cs_why", ""),
            obl.get("summary", ""),
        ),
    )
    oid = cur.lastrowid
    for src in obl.get("sources") or []:
        conn.execute(
            "INSERT INTO sources (obligation_id, label, url) VALUES (?, ?, ?)",
            (oid, src["label"], src["url"]),
        )
    return oid


def insert_history(
    conn,
    jid,
    event_date,
    title,
    detail="",
    source_url=None,
    event_kind="milestone",
):
    """Insert history. Use event_kind='seed_meta' for non-chart housekeeping only."""
    conn.execute(
        "INSERT INTO history_events "
        "(jurisdiction_id, event_date, title, detail, source_url, event_kind, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, datetime('now'))",
        (jid, event_date, title, detail, source_url, event_kind),
    )


# Verified milestones only (primary sources). Never invent dates.
# These feed the activity chart together with obligation effective_dates.
VERIFIED_MILESTONES = [
    {
        "code": "US-FED",
        "event_date": "2024-02-08",
        "title": "FCC 24-17 Declaratory Ruling released (AI voices under TCPA)",
        "detail": (
            "FCC Declaratory Ruling FCC 24-17 (adopted Feb 2, 2024; released Feb 8, 2024) "
            "confirms AI-generated human voices are artificial/prerecorded under the TCPA."
        ),
        "source_url": "https://docs.fcc.gov/public/attachments/FCC-24-17A1.pdf",
    },
    {
        "code": "US-FED",
        "event_date": "2025-12-11",
        "title": "EO 14365 signed",
        "detail": "Executive Order 14365 signed December 11, 2025.",
        "source_url": (
            "https://www.federalregister.gov/documents/2025/12/16/2025-23092/"
            "ensuring-a-national-policy-framework-for-artificial-intelligence"
        ),
    },
    {
        "code": "US-FED",
        "event_date": "2025-12-16",
        "title": "EO 14365 published in Federal Register",
        "detail": "EO 14365 published December 16, 2025 (90 FR 58499).",
        "source_url": (
            "https://www.federalregister.gov/documents/2025/12/16/2025-23092/"
            "ensuring-a-national-policy-framework-for-artificial-intelligence"
        ),
    },
    {
        "code": "CA",
        "event_date": "2019-07-01",
        "title": "California Bot Act operative",
        "detail": (
            "B&P §§17940–17943 (SB 1001) operative July 1, 2019 "
            "(effective Jan 1, 2019; operative July 1, 2019 per §17943)."
        ),
        "source_url": (
            "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml"
            "?lawCode=BPC&sectionNum=17941"
        ),
    },
    {
        "code": "CA",
        "event_date": "2025-10-01",
        "title": "FEHA automated-decision systems regulations operative",
        "detail": (
            "Civil Rights Council FEHA ADS amendments operative October 1, 2025 "
            "(Register 2025, No. 26)."
        ),
        "source_url": (
            "https://calcivilrights.ca.gov/2025/06/30/civil-rights-council-secures-approval-"
            "for-regulations-to-protect-against-employment-discrimination-related-to-"
            "artificial-intelligence/"
        ),
    },
    {
        "code": "CA",
        "event_date": "2027-01-01",
        "title": "CCPA ADMT compliance deadline for existing uses",
        "detail": (
            "CPPA ADMT regulations: general effective date Jan 1, 2026; existing ADMT uses "
            "for significant decisions generally must comply by Jan 1, 2027."
        ),
        "source_url": "https://cppa.ca.gov/regulations/ccpa_updates.html",
    },
    {
        "code": "NY",
        "event_date": "2023-01-01",
        "title": "NYC Local Law 144 statutory effective date",
        "detail": "LL144 took effect January 1, 2023; DCWP delayed enforcement to July 5, 2023.",
        "source_url": "https://www.nyc.gov/site/dca/about/automated-employment-decision-tools.page",
    },
    {
        "code": "NY",
        "event_date": "2023-07-05",
        "title": "NYC LL144 enforcement begins",
        "detail": "NYC DCWP began enforcing Local Law 144 AEDT rules on July 5, 2023.",
        "source_url": "https://www.nyc.gov/site/dca/about/automated-employment-decision-tools.page",
    },
    {
        "code": "UT",
        "event_date": "2024-03-13",
        "title": "Utah SB 149 signed (AI Policy Act)",
        "detail": "Governor signed SB 149 on March 13, 2024; Act effective May 1, 2024.",
        "source_url": "https://le.utah.gov/~2024/bills/sbillint/SB0149.htm",
    },
    {
        "code": "UT",
        "event_date": "2024-05-01",
        "title": "Utah AI Policy Act effective",
        "detail": "SB 149 §13: This bill takes effect on May 1, 2024.",
        "source_url": "https://le.utah.gov/~2024/bills/sbillint/SB0149.htm",
    },
    {
        "code": "ME",
        "event_date": "2025-06-12",
        "title": "Maine PL 2025, c. 294 approved",
        "detail": (
            "LD 1727 / Public Law 2025, c. 294 approved June 12, 2025. Nonemergency First "
            "Special Session laws generally effective September 24, 2025."
        ),
        "source_url": "https://www.maine.gov/pfr/consumercredit/laws_rules/new/pl294.pdf",
    },
    {
        "code": "ME",
        "event_date": "2025-09-24",
        "title": "Maine AI chatbot disclosure effective",
        "detail": (
            "10 M.R.S. §1500-DD generally effective September 24, 2025 (First Special Session "
            "2025 nonemergency general effective date)."
        ),
        "source_url": "https://www.mainelegislature.org/legis/statutes/10/title10sec1500-DD.html",
    },
    {
        "code": "TX",
        "event_date": "2025-06-22",
        "title": "Texas TRAIGA (HB 149) signed",
        "detail": "HB 149 signed June 22, 2025; effective January 1, 2026.",
        "source_url": "https://capitol.texas.gov/BillLookup/history.aspx?Bill=HB149&LegSess=89R",
    },
    {
        "code": "TX",
        "event_date": "2026-01-01",
        "title": "Texas TRAIGA effective",
        "detail": "Texas Responsible AI Governance Act (HB 149) effective January 1, 2026.",
        "source_url": "https://capitol.texas.gov/tlodocs/89R/billtext/html/HB00149F.htm",
    },
    {
        "code": "CT",
        "event_date": "2026-10-01",
        "title": "PA 26-15 first-wave provisions effective",
        "detail": (
            "Oct 1, 2026: AEDT framework scaffolding and anti-discrimination amendments "
            "(among other first-wave provisions)."
        ),
        "source_url": "https://www.cga.ct.gov/2026/ACT/PA/PDF/2026PA-00015-R00SB-00005-PA.PDF",
    },
    {
        "code": "CT",
        "event_date": "2027-01-01",
        "title": "PA 26-15 AI companion safeguards effective",
        "detail": "AI companion safeguard sections take effect January 1, 2027.",
        "source_url": "https://www.cga.ct.gov/2026/ACT/PA/PDF/2026PA-00015-R00SB-00005-PA.PDF",
    },
    {
        "code": "CT",
        "event_date": "2027-10-01",
        "title": "PA 26-15 AEDT interaction/pre-decision disclosures apply",
        "detail": (
            "Interaction disclosure and written pre-decision notice apply to AEDTs deployed "
            "on or after October 1, 2027."
        ),
        "source_url": "https://www.cga.ct.gov/2026/ACT/PA/PDF/2026PA-00015-R00SB-00005-PA.PDF",
    },
    {
        "code": "CO",
        "event_date": "2027-01-01",
        "title": "Colorado SB26-189 ADMT effective",
        "detail": (
            "SB26-189 ADMT framework generally effective January 1, 2027 for consequential "
            "decisions including residential lease/purchase."
        ),
        "source_url": "https://www.leg.colorado.gov/bills/sb26-189",
    },
    {
        "code": "IL",
        "event_date": "2020-01-01",
        "title": "Illinois AI Video Interview Act effective",
        "detail": (
            "Public Act 101-0260 (Artificial Intelligence Video Interview Act) effective "
            "January 1, 2020."
        ),
        "source_url": "https://www.ilga.gov/Legislation/publicacts/view/101-0260",
    },
]


def main() -> None:
    if db.DB_PATH.exists():
        db.DB_PATH.unlink()
    db.ensure_db()

    code_to_jid: dict[str, int] = {}
    count = 0
    with db.connect() as conn:
        fed = PRIORITY["US-FED"]
        jid = insert_jurisdiction(
            conn,
            "US-FED",
            fed["name"],
            fed["kind"],
            fed["status_label"],
            fed["summary"],
            fed.get("notes", ""),
        )
        code_to_jid["US-FED"] = jid
        for obl in fed["obligations"]:
            insert_obligation(conn, jid, obl)
        for src in fed.get("sources") or []:
            conn.execute(
                "INSERT INTO sources (jurisdiction_id, label, url) VALUES (?, ?, ?)",
                (jid, src["label"], src["url"]),
            )
        count += 1

        for code, name in STATES:
            if code in PRIORITY and code != "US-FED":
                p = PRIORITY[code]
                jid = insert_jurisdiction(
                    conn,
                    code,
                    p.get("name", name),
                    p.get("kind", "state"),
                    p["status_label"],
                    p["summary"],
                    p.get("notes", ""),
                )
                for obl in p.get("obligations") or []:
                    insert_obligation(conn, jid, obl)
                for src in p.get("sources") or []:
                    conn.execute(
                        "INSERT INTO sources (jurisdiction_id, label, url) VALUES (?, ?, ?)",
                        (jid, src["label"], src["url"]),
                    )
            else:
                jid = insert_jurisdiction(
                    conn,
                    code,
                    name,
                    "state",
                    "quiet",
                    quiet_summary(name),
                    "No material AI service/disclosure/ADMT rules for voice/conversation operators in focus yet.",
                )
            code_to_jid[code] = jid
            count += 1

        # Verified legislative/regulatory milestones only — never per-jurisdiction
        # "baseline snapshot" rows (those previously caused a fake Sep 2026 spike).
        for ev in VERIFIED_MILESTONES:
            jid = code_to_jid.get(ev["code"])
            if not jid:
                raise SystemExit(f"Missing jurisdiction for milestone: {ev['code']}")
            insert_history(
                conn,
                jid,
                ev["event_date"],
                ev["title"],
                ev["detail"],
                ev.get("source_url"),
                event_kind="milestone",
            )

        conn.execute(
            "INSERT INTO meta(key, value) VALUES ('last_global_refresh', ?)",
            (BASELINE_DATE,),
        )
        conn.execute(
            "INSERT INTO meta(key, value) VALUES ('seed_version', ?)",
            ("baseline-2026-09-22-v2-no-chart-noise",),
        )

    print(f"Seeded {count} jurisdictions into {db.DB_PATH}")
    with db.connect() as conn:
        n_obl = conn.execute("SELECT COUNT(*) AS c FROM obligations").fetchone()["c"]
        n_src = conn.execute("SELECT COUNT(*) AS c FROM sources").fetchone()["c"]
        n_hist = conn.execute("SELECT COUNT(*) AS c FROM history_events").fetchone()["c"]
        n_seedish = conn.execute(
            "SELECT COUNT(*) AS c FROM history_events WHERE event_kind = 'seed_meta' "
            "OR lower(title) LIKE '%baseline snapshot%'"
        ).fetchone()["c"]
    print(f"  obligations={n_obl} sources={n_src} history_events={n_hist} seedish_history={n_seedish}")


if __name__ == "__main__":
    main()
