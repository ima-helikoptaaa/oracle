"""Exodus (Job Tracker) tools for Hermes Agent."""

import os

from tools.http_client import ServiceClient
from tools.registry import registry

EXODUS_URL = os.getenv("EXODUS_API_URL", "http://localhost:3001/api")

_client = ServiceClient(EXODUS_URL, "Exodus")


def _check():
    return bool(EXODUS_URL)


# ── Tools ────────────────────────────────────────────────────────────────────

async def get_applications(args, **kw):
    params = {k: args[k] for k in ("stage", "search", "sortBy", "sortOrder", "tagIds") if args.get(k)}
    return await _client.get("/applications", params or None)


async def get_application(args, **kw):
    return await _client.get(f"/applications/{args['id']}")


async def create_application(args, **kw):
    return await _client.post("/applications", args)


async def update_application_stage(args, **kw):
    return await _client.patch(f"/applications/{args['id']}/stage", {"stage": args["stage"]})


async def get_upcoming_interviews(args, **kw):
    return await _client.get("/interviews/upcoming", {"days": args.get("days", 7)})


async def create_interview(args, **kw):
    return await _client.post("/interviews", args)


async def get_dashboard(args, **kw):
    return await _client.get("/dashboard/stats")


async def get_follow_ups(args, **kw):
    return await _client.get("/dashboard/follow-ups")


# ── Registration ─────────────────────────────────────────────────────────────

registry.register(
    name="exodus_get_applications",
    toolset="exodus", is_async=True, emoji="💼",
    check_fn=_check, requires_env=["EXODUS_API_URL"],
    schema={
        "description": "Get job applications from Exodus. Filter by pipeline stage (WISHLIST, APPLIED, INTRODUCTORY_CALL, ROUND_1-5, OFFER, REJECTED, WITHDRAWN), search text, or sort.",
        "parameters": {
            "type": "object",
            "properties": {
                "stage": {"type": "string", "description": "Pipeline stage filter"},
                "search": {"type": "string", "description": "Search by company or role"},
                "sortBy": {"type": "string", "description": "Sort: updatedAt, appliedDate, createdAt"},
            },
        },
    },
    handler=get_applications,
)

registry.register(
    name="exodus_get_application",
    toolset="exodus", is_async=True, emoji="💼",
    check_fn=_check, requires_env=["EXODUS_API_URL"],
    schema={
        "description": "Get detailed info about a specific job application including interviews, contacts, notes, and tags.",
        "parameters": {
            "type": "object",
            "properties": {"id": {"type": "string", "description": "Application ID"}},
            "required": ["id"],
        },
    },
    handler=get_application,
)

registry.register(
    name="exodus_create_application",
    toolset="exodus", is_async=True, emoji="💼",
    check_fn=_check, requires_env=["EXODUS_API_URL"],
    schema={
        "description": "Create a new job application in Exodus.",
        "parameters": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "description": "Job role/title"},
                "companyName": {"type": "string", "description": "Company name"},
                "jobUrl": {"type": "string", "description": "Job posting URL"},
                "stage": {"type": "string", "description": "Pipeline stage (default: WISHLIST)"},
                "priority": {"type": "number", "description": "Priority 0-3"},
                "location": {"type": "string"},
                "isRemote": {"type": "boolean"},
                "salaryMin": {"type": "number"},
                "salaryMax": {"type": "number"},
            },
            "required": ["role"],
        },
    },
    handler=create_application,
)

registry.register(
    name="exodus_update_application_stage",
    toolset="exodus", is_async=True, emoji="💼",
    check_fn=_check, requires_env=["EXODUS_API_URL"],
    schema={
        "description": "Move a job application to a different pipeline stage.",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Application ID"},
                "stage": {"type": "string", "description": "New pipeline stage"},
            },
            "required": ["id", "stage"],
        },
    },
    handler=update_application_stage,
)

registry.register(
    name="exodus_get_upcoming_interviews",
    toolset="exodus", is_async=True, emoji="💼",
    check_fn=_check, requires_env=["EXODUS_API_URL"],
    schema={
        "description": "Get upcoming interviews across all job applications for the next N days.",
        "parameters": {
            "type": "object",
            "properties": {"days": {"type": "number", "description": "Days ahead to look (default: 7)"}},
        },
    },
    handler=get_upcoming_interviews,
)

registry.register(
    name="exodus_create_interview",
    toolset="exodus", is_async=True, emoji="💼",
    check_fn=_check, requires_env=["EXODUS_API_URL"],
    schema={
        "description": "Schedule a new interview round for a job application.",
        "parameters": {
            "type": "object",
            "properties": {
                "applicationId": {"type": "string", "description": "Application ID"},
                "roundNumber": {"type": "number", "description": "Round number"},
                "type": {"type": "string", "description": "Type: DSA, LLD, HLD, SYSTEM_DESIGN, BEHAVIORAL, INTRO_CALL, HR, TAKE_HOME, CODING_CHALLENGE, OTHER"},
                "scheduledAt": {"type": "string", "description": "ISO datetime"},
                "durationMin": {"type": "number", "description": "Duration in minutes"},
                "interviewerName": {"type": "string"},
                "meetingLink": {"type": "string"},
                "prepNotes": {"type": "string"},
            },
            "required": ["applicationId", "roundNumber", "type"],
        },
    },
    handler=create_interview,
)

registry.register(
    name="exodus_get_dashboard",
    toolset="exodus", is_async=True, emoji="💼",
    check_fn=_check, requires_env=["EXODUS_API_URL"],
    schema={
        "description": "Get Exodus dashboard: total applications, by stage, response rate, offers.",
        "parameters": {"type": "object", "properties": {}},
    },
    handler=get_dashboard,
)

registry.register(
    name="exodus_get_follow_ups",
    toolset="exodus", is_async=True, emoji="💼",
    check_fn=_check, requires_env=["EXODUS_API_URL"],
    schema={
        "description": "Get job applications that are due for follow-up.",
        "parameters": {"type": "object", "properties": {}},
    },
    handler=get_follow_ups,
)
