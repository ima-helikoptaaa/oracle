"""Progression (Habit Tracker) tools for Hermes Agent."""

import json
import os
import httpx

from tools.registry import registry

PROGRESSION_URL = os.getenv("PROGRESSION_API_URL", "http://localhost:8000/api/v1")
FIREBASE_TOKEN = os.getenv("FIREBASE_ID_TOKEN", "")


def _headers() -> dict:
    h = {}
    if FIREBASE_TOKEN:
        h["Authorization"] = f"Bearer {FIREBASE_TOKEN}"
    return h


async def _get(path: str, params: dict | None = None) -> str:
    try:
        async with httpx.AsyncClient(base_url=PROGRESSION_URL, timeout=15, headers=_headers()) as c:
            r = await c.get(path, params=params)
            r.raise_for_status()
            return json.dumps(r.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def _post(path: str, body: dict | None = None) -> str:
    try:
        async with httpx.AsyncClient(base_url=PROGRESSION_URL, timeout=15, headers=_headers()) as c:
            r = await c.post(path, json=body or {})
            r.raise_for_status()
            return json.dumps(r.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def _put(path: str, body: dict | None = None) -> str:
    try:
        async with httpx.AsyncClient(base_url=PROGRESSION_URL, timeout=15, headers=_headers()) as c:
            r = await c.put(path, json=body or {})
            r.raise_for_status()
            return json.dumps(r.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Tools ────────────────────────────────────────────────────────────────────

async def get_activities(args, **kw):
    return await _get("/activities")

async def complete_activity(args, **kw):
    return await _post(f"/activities/{args['id']}/complete", {"value": args["value"]})

async def create_activity(args, **kw):
    return await _post("/activities", args)

async def get_stats_overview(args, **kw):
    return await _get("/stats/overview")

async def get_heatmap(args, **kw):
    params = {}
    if args.get("days"):
        params["days"] = args["days"]
    return await _get("/stats/heatmap", params or None)

async def get_points(args, **kw):
    return await _get("/points")

async def get_identities(args, **kw):
    return await _get("/identities")

async def get_stacks(args, **kw):
    return await _get("/stacks")

async def check_penalties(args, **kw):
    return await _get("/activities/penalties")

async def get_activity_history(args, **kw):
    params = {}
    if args.get("days"):
        params["days"] = args["days"]
    return await _get(f"/stats/activity/{args['activityId']}/history", params or None)


# ── Registration ─────────────────────────────────────────────────────────────

registry.register(
    name="progression_get_activities", toolset="progression", is_async=True, emoji="🔥",
    schema={"name": "progression_get_activities", "description": "Get all habit activities with current Fibonacci streaks, targets, and today's completion status.", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: get_activities(args, **kw),
)

registry.register(
    name="progression_complete_activity", toolset="progression", is_async=True, emoji="✅",
    schema={"name": "progression_complete_activity", "description": "Log completion of a habit activity with a value.", "parameters": {"type": "object", "properties": {"id": {"type": "string", "description": "Activity ID"}, "value": {"type": "number", "description": "Completion value (1 for done, or amount)"}}, "required": ["id", "value"]}},
    handler=lambda args, **kw: complete_activity(args, **kw),
)

registry.register(
    name="progression_create_activity", toolset="progression", is_async=True, emoji="🔥",
    schema={"name": "progression_create_activity", "description": "Create a new habit activity.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "baseTarget": {"type": "number", "description": "Initial target value"}, "emoji": {"type": "string"}, "unit": {"type": "string"}, "stepSize": {"type": "number"}, "colorHex": {"type": "string"}, "identityId": {"type": "string"}, "cueTime": {"type": "string"}}, "required": ["name", "baseTarget"]}},
    handler=lambda args, **kw: create_activity(args, **kw),
)

registry.register(
    name="progression_get_stats_overview", toolset="progression", is_async=True, emoji="📊",
    schema={"name": "progression_get_stats_overview", "description": "Get stats: total completions, active streaks, points, weekly comparison.", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: get_stats_overview(args, **kw),
)

registry.register(
    name="progression_get_heatmap", toolset="progression", is_async=True, emoji="🟩",
    schema={"name": "progression_get_heatmap", "description": "Get activity completion heatmap for the last N days.", "parameters": {"type": "object", "properties": {"days": {"type": "number", "description": "Number of days (default: 90)"}}}},
    handler=lambda args, **kw: get_heatmap(args, **kw),
)

registry.register(
    name="progression_get_points", toolset="progression", is_async=True, emoji="💰",
    schema={"name": "progression_get_points", "description": "Get current points balance and transaction history.", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: get_points(args, **kw),
)

registry.register(
    name="progression_get_identities", toolset="progression", is_async=True, emoji="🎭",
    schema={"name": "progression_get_identities", "description": "Get user's identities (personal archetypes) that habits are linked to.", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: get_identities(args, **kw),
)

registry.register(
    name="progression_get_stacks", toolset="progression", is_async=True, emoji="📚",
    schema={"name": "progression_get_stacks", "description": "Get habit stacks — groups of activities to do together.", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: get_stacks(args, **kw),
)

registry.register(
    name="progression_check_penalties", toolset="progression", is_async=True, emoji="⚠️",
    schema={"name": "progression_check_penalties", "description": "Check and apply streak penalties for missed days.", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: check_penalties(args, **kw),
)

registry.register(
    name="progression_get_activity_history", toolset="progression", is_async=True, emoji="📈",
    schema={"name": "progression_get_activity_history", "description": "Get completion history for a specific habit activity.", "parameters": {"type": "object", "properties": {"activityId": {"type": "string", "description": "Activity ID"}, "days": {"type": "number", "description": "Days to look back (default: 30)"}}, "required": ["activityId"]}},
    handler=lambda args, **kw: get_activity_history(args, **kw),
)
