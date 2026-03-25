"""Exodus (Job Tracker) tools for Hermes Agent."""

import json
import os
import httpx

from tools.registry import registry

EXODUS_URL = os.getenv("EXODUS_API_URL", "http://localhost:3001/api")


async def _get(path: str, params: dict | None = None) -> str:
    try:
        async with httpx.AsyncClient(base_url=EXODUS_URL, timeout=15) as c:
            r = await c.get(path, params=params)
            r.raise_for_status()
            return json.dumps(r.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def _post(path: str, body: dict | None = None) -> str:
    try:
        async with httpx.AsyncClient(base_url=EXODUS_URL, timeout=15) as c:
            r = await c.post(path, json=body or {})
            r.raise_for_status()
            return json.dumps(r.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def _patch(path: str, body: dict | None = None) -> str:
    try:
        async with httpx.AsyncClient(base_url=EXODUS_URL, timeout=15) as c:
            r = await c.patch(path, json=body or {})
            r.raise_for_status()
            return json.dumps(r.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Tools ────────────────────────────────────────────────────────────────────

async def get_applications(args, **kw):
    params = {}
    for k in ("stage", "search", "sortBy", "sortOrder", "tagIds"):
        if args.get(k):
            params[k] = args[k]
    return await _get("/applications", params or None)


async def get_application(args, **kw):
    return await _get(f"/applications/{args['id']}")


async def create_application(args, **kw):
    return await _post("/applications", args)


async def update_application_stage(args, **kw):
    return await _patch(f"/applications/{args['id']}/stage", {"stage": args["stage"]})


async def get_upcoming_interviews(args, **kw):
    params = {"days": args.get("days", 7)}
    return await _get("/interviews/upcoming", params)


async def create_interview(args, **kw):
    return await _post("/interviews", args)


async def get_dashboard(args, **kw):
    return await _get("/dashboard/stats")


async def get_follow_ups(args, **kw):
    return await _get("/dashboard/follow-ups")


# ── Registration ─────────────────────────────────────────────────────────────

registry.register(
    name="exodus_get_applications",
    toolset="exodus",
    schema={
        "name": "exodus_get_applications",
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
    handler=lambda args, **kw: get_applications(args, **kw),
    is_async=True,
    emoji="💼",
)

registry.register(
    name="exodus_get_application",
    toolset="exodus",
    schema={
        "name": "exodus_get_application",
        "description": "Get detailed info about a specific job application including interviews, contacts, notes, and tags.",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Application ID"},
            },
            "required": ["id"],
        },
    },
    handler=lambda args, **kw: get_application(args, **kw),
    is_async=True,
    emoji="💼",
)

registry.register(
    name="exodus_create_application",
    toolset="exodus",
    schema={
        "name": "exodus_create_application",
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
    handler=lambda args, **kw: create_application(args, **kw),
    is_async=True,
    emoji="💼",
)

registry.register(
    name="exodus_update_application_stage",
    toolset="exodus",
    schema={
        "name": "exodus_update_application_stage",
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
    handler=lambda args, **kw: update_application_stage(args, **kw),
    is_async=True,
    emoji="💼",
)

registry.register(
    name="exodus_get_upcoming_interviews",
    toolset="exodus",
    schema={
        "name": "exodus_get_upcoming_interviews",
        "description": "Get upcoming interviews across all job applications for the next N days.",
        "parameters": {
            "type": "object",
            "properties": {
                "days": {"type": "number", "description": "Days ahead to look (default: 7)"},
            },
        },
    },
    handler=lambda args, **kw: get_upcoming_interviews(args, **kw),
    is_async=True,
    emoji="💼",
)

registry.register(
    name="exodus_create_interview",
    toolset="exodus",
    schema={
        "name": "exodus_create_interview",
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
    handler=lambda args, **kw: create_interview(args, **kw),
    is_async=True,
    emoji="💼",
)

registry.register(
    name="exodus_get_dashboard",
    toolset="exodus",
    schema={
        "name": "exodus_get_dashboard",
        "description": "Get Exodus dashboard: total applications, by stage, response rate, offers.",
        "parameters": {"type": "object", "properties": {}},
    },
    handler=lambda args, **kw: get_dashboard(args, **kw),
    is_async=True,
    emoji="💼",
)

registry.register(
    name="exodus_get_follow_ups",
    toolset="exodus",
    schema={
        "name": "exodus_get_follow_ups",
        "description": "Get job applications that are due for follow-up.",
        "parameters": {"type": "object", "properties": {}},
    },
    handler=lambda args, **kw: get_follow_ups(args, **kw),
    is_async=True,
    emoji="💼",
)
