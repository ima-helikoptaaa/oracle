"""Sisyphus (Fitness Tracker) tools for Hermes Agent."""

import json
import os
import httpx

from tools.registry import registry
from tools.firebase_auth import get_auth_headers

SISYPHUS_URL = os.getenv("SISYPHUS_API_URL", "http://localhost:3003/api")


async def _get(path: str, params: dict | None = None) -> str:
    try:
        headers = await get_auth_headers()
        async with httpx.AsyncClient(base_url=SISYPHUS_URL, timeout=15, headers=headers) as c:
            r = await c.get(path, params=params)
            r.raise_for_status()
            return json.dumps(r.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def _post(path: str, body: dict | None = None) -> str:
    try:
        headers = await get_auth_headers()
        async with httpx.AsyncClient(base_url=SISYPHUS_URL, timeout=15, headers=headers) as c:
            r = await c.post(path, json=body or {})
            r.raise_for_status()
            return json.dumps(r.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def _put(path: str, body: dict | None = None) -> str:
    try:
        headers = await get_auth_headers()
        async with httpx.AsyncClient(base_url=SISYPHUS_URL, timeout=15, headers=headers) as c:
            r = await c.put(path, json=body or {})
            r.raise_for_status()
            return json.dumps(r.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def _patch(path: str, body: dict | None = None) -> str:
    try:
        headers = await get_auth_headers()
        async with httpx.AsyncClient(base_url=SISYPHUS_URL, timeout=15, headers=headers) as c:
            r = await c.patch(path, json=body or {})
            r.raise_for_status()
            return json.dumps(r.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Tools ────────────────────────────────────────────────────────────────────

async def get_splits(args, **kw):
    return await _get("/splits")

async def get_split(args, **kw):
    return await _get(f"/splits/{args['id']}")

async def get_today_session(args, **kw):
    return await _get("/sessions/today")

async def get_active_session(args, **kw):
    return await _get("/sessions/active")

async def get_sessions(args, **kw):
    params = {k: args[k] for k in ("splitId", "startDate", "endDate", "limit") if args.get(k)}
    return await _get("/sessions", params or None)

async def create_session(args, **kw):
    return await _post("/sessions", args)

async def get_today_daily_log(args, **kw):
    return await _get("/daily-logs/today")

async def upsert_daily_log(args, **kw):
    return await _put("/daily-logs", args)

async def get_analytics_summary(args, **kw):
    return await _get("/analytics/summary")

async def get_personal_records(args, **kw):
    return await _get("/analytics/personal-records")


# ── Registration ─────────────────────────────────────────────────────────────

registry.register(
    name="sisyphus_get_splits", toolset="sisyphus", is_async=True, emoji="🏋️",
    schema={"name": "sisyphus_get_splits", "description": "Get all workout splits (e.g., Push, Pull, Legs) with exercises.", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: get_splits(args, **kw),
)

registry.register(
    name="sisyphus_get_split", toolset="sisyphus", is_async=True, emoji="🏋️",
    schema={"name": "sisyphus_get_split", "description": "Get a specific workout split with its exercises.", "parameters": {"type": "object", "properties": {"id": {"type": "string", "description": "Split ID"}}, "required": ["id"]}},
    handler=lambda args, **kw: get_split(args, **kw),
)

registry.register(
    name="sisyphus_get_today_session", toolset="sisyphus", is_async=True, emoji="🏋️",
    schema={"name": "sisyphus_get_today_session", "description": "Get today's workout session if one exists.", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: get_today_session(args, **kw),
)

registry.register(
    name="sisyphus_get_active_session", toolset="sisyphus", is_async=True, emoji="🏋️",
    schema={"name": "sisyphus_get_active_session", "description": "Get the currently active (incomplete) workout session.", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: get_active_session(args, **kw),
)

registry.register(
    name="sisyphus_get_sessions", toolset="sisyphus", is_async=True, emoji="🏋️",
    schema={"name": "sisyphus_get_sessions", "description": "Get workout session history. Filter by split or date range.", "parameters": {"type": "object", "properties": {"splitId": {"type": "string"}, "startDate": {"type": "string"}, "endDate": {"type": "string"}, "limit": {"type": "number"}}}},
    handler=lambda args, **kw: get_sessions(args, **kw),
)

registry.register(
    name="sisyphus_create_session", toolset="sisyphus", is_async=True, emoji="🏋️",
    schema={"name": "sisyphus_create_session", "description": "Start a new workout session for a given split.", "parameters": {"type": "object", "properties": {"splitId": {"type": "string", "description": "Workout split ID"}, "date": {"type": "string", "description": "YYYY-MM-DD, defaults to today"}}, "required": ["splitId"]}},
    handler=lambda args, **kw: create_session(args, **kw),
)

registry.register(
    name="sisyphus_get_today_daily_log", toolset="sisyphus", is_async=True, emoji="📊",
    schema={"name": "sisyphus_get_today_daily_log", "description": "Get today's daily health log (weight, protein, calories, water, sleep).", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: get_today_daily_log(args, **kw),
)

registry.register(
    name="sisyphus_upsert_daily_log", toolset="sisyphus", is_async=True, emoji="📊",
    schema={"name": "sisyphus_upsert_daily_log", "description": "Log or update daily health metrics: weight (kg), protein (g), calories (kcal), water (ml), sleep (hours).", "parameters": {"type": "object", "properties": {"date": {"type": "string"}, "weightKg": {"type": "number"}, "proteinG": {"type": "number"}, "caloriesKcal": {"type": "number"}, "waterMl": {"type": "number"}, "sleepHours": {"type": "number"}, "notes": {"type": "string"}}}},
    handler=lambda args, **kw: upsert_daily_log(args, **kw),
)

registry.register(
    name="sisyphus_get_analytics_summary", toolset="sisyphus", is_async=True, emoji="📊",
    schema={"name": "sisyphus_get_analytics_summary", "description": "Get workout analytics: total workouts, streak, volume, reps, average duration.", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: get_analytics_summary(args, **kw),
)

registry.register(
    name="sisyphus_get_personal_records", toolset="sisyphus", is_async=True, emoji="🏆",
    schema={"name": "sisyphus_get_personal_records", "description": "Get personal records — best weight, volume, reps per exercise.", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: get_personal_records(args, **kw),
)
