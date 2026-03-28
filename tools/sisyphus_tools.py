"""Sisyphus (Fitness Tracker) tools for Hermes Agent."""

import os

from tools.firebase_auth import get_auth_headers
from tools.http_client import ServiceClient
from tools.registry import registry

SISYPHUS_URL = os.getenv("SISYPHUS_API_URL", "http://localhost:3003/api")

_client = ServiceClient(SISYPHUS_URL, "Sisyphus", auth_fn=get_auth_headers)


def _check():
    return bool(os.getenv("GOOGLE_REFRESH_TOKEN") or os.getenv("FIREBASE_ID_TOKEN"))


# ── Tools ────────────────────────────────────────────────────────────────────

async def get_splits(args, **kw):
    return await _client.get("/splits")

async def get_split(args, **kw):
    return await _client.get(f"/splits/{args['id']}")

async def get_today_session(args, **kw):
    return await _client.get("/sessions/today")

async def get_active_session(args, **kw):
    return await _client.get("/sessions/active")

async def get_sessions(args, **kw):
    params = {k: args[k] for k in ("splitId", "startDate", "endDate", "limit") if args.get(k)}
    return await _client.get("/sessions", params or None)

async def create_session(args, **kw):
    return await _client.post("/sessions", args)

async def get_today_daily_log(args, **kw):
    return await _client.get("/daily-logs/today")

async def upsert_daily_log(args, **kw):
    return await _client.put("/daily-logs", args)

async def get_analytics_summary(args, **kw):
    return await _client.get("/analytics/summary")

async def get_personal_records(args, **kw):
    return await _client.get("/analytics/personal-records")


# ── Registration ─────────────────────────────────────────────────────────────

registry.register(
    name="sisyphus_get_splits", toolset="sisyphus", is_async=True, emoji="🏋️",
    check_fn=_check, requires_env=["GOOGLE_REFRESH_TOKEN"],
    schema={"description": "Get all workout splits (e.g., Push, Pull, Legs) with exercises.", "parameters": {"type": "object", "properties": {}}},
    handler=get_splits,
)

registry.register(
    name="sisyphus_get_split", toolset="sisyphus", is_async=True, emoji="🏋️",
    check_fn=_check, requires_env=["GOOGLE_REFRESH_TOKEN"],
    schema={"description": "Get a specific workout split with its exercises.", "parameters": {"type": "object", "properties": {"id": {"type": "string", "description": "Split ID"}}, "required": ["id"]}},
    handler=get_split,
)

registry.register(
    name="sisyphus_get_today_session", toolset="sisyphus", is_async=True, emoji="🏋️",
    check_fn=_check, requires_env=["GOOGLE_REFRESH_TOKEN"],
    schema={"description": "Get today's workout session if one exists.", "parameters": {"type": "object", "properties": {}}},
    handler=get_today_session,
)

registry.register(
    name="sisyphus_get_active_session", toolset="sisyphus", is_async=True, emoji="🏋️",
    check_fn=_check, requires_env=["GOOGLE_REFRESH_TOKEN"],
    schema={"description": "Get the currently active (incomplete) workout session.", "parameters": {"type": "object", "properties": {}}},
    handler=get_active_session,
)

registry.register(
    name="sisyphus_get_sessions", toolset="sisyphus", is_async=True, emoji="🏋️",
    check_fn=_check, requires_env=["GOOGLE_REFRESH_TOKEN"],
    schema={"description": "Get workout session history. Filter by split or date range.", "parameters": {"type": "object", "properties": {"splitId": {"type": "string"}, "startDate": {"type": "string"}, "endDate": {"type": "string"}, "limit": {"type": "number"}}}},
    handler=get_sessions,
)

registry.register(
    name="sisyphus_create_session", toolset="sisyphus", is_async=True, emoji="🏋️",
    check_fn=_check, requires_env=["GOOGLE_REFRESH_TOKEN"],
    schema={"description": "Start a new workout session for a given split.", "parameters": {"type": "object", "properties": {"splitId": {"type": "string", "description": "Workout split ID"}, "date": {"type": "string", "description": "YYYY-MM-DD, defaults to today"}}, "required": ["splitId"]}},
    handler=create_session,
)

registry.register(
    name="sisyphus_get_today_daily_log", toolset="sisyphus", is_async=True, emoji="📊",
    check_fn=_check, requires_env=["GOOGLE_REFRESH_TOKEN"],
    schema={"description": "Get today's daily health log (weight, protein, calories, water, sleep).", "parameters": {"type": "object", "properties": {}}},
    handler=get_today_daily_log,
)

registry.register(
    name="sisyphus_upsert_daily_log", toolset="sisyphus", is_async=True, emoji="📊",
    check_fn=_check, requires_env=["GOOGLE_REFRESH_TOKEN"],
    schema={"description": "Log or update daily health metrics: weight (kg), protein (g), calories (kcal), water (ml), sleep (hours).", "parameters": {"type": "object", "properties": {"date": {"type": "string"}, "weightKg": {"type": "number"}, "proteinG": {"type": "number"}, "caloriesKcal": {"type": "number"}, "waterMl": {"type": "number"}, "sleepHours": {"type": "number"}, "notes": {"type": "string"}}}},
    handler=upsert_daily_log,
)

registry.register(
    name="sisyphus_get_analytics_summary", toolset="sisyphus", is_async=True, emoji="📊",
    check_fn=_check, requires_env=["GOOGLE_REFRESH_TOKEN"],
    schema={"description": "Get workout analytics: total workouts, streak, volume, reps, average duration.", "parameters": {"type": "object", "properties": {}}},
    handler=get_analytics_summary,
)

registry.register(
    name="sisyphus_get_personal_records", toolset="sisyphus", is_async=True, emoji="🏆",
    check_fn=_check, requires_env=["GOOGLE_REFRESH_TOKEN"],
    schema={"description": "Get personal records — best weight, volume, reps per exercise.", "parameters": {"type": "object", "properties": {}}},
    handler=get_personal_records,
)
