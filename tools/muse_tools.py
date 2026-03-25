"""Muse (Content Engine) tools for Hermes Agent."""

import json
import os
import httpx

from tools.registry import registry

MUSE_URL = os.getenv("MUSE_API_URL", "http://localhost:3002/api")


async def _get(path: str, params: dict | None = None) -> str:
    try:
        async with httpx.AsyncClient(base_url=MUSE_URL, timeout=15) as c:
            r = await c.get(path, params=params)
            r.raise_for_status()
            return json.dumps(r.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def _post(path: str, body: dict | None = None) -> str:
    try:
        async with httpx.AsyncClient(base_url=MUSE_URL, timeout=30) as c:
            r = await c.post(path, json=body or {})
            r.raise_for_status()
            return json.dumps(r.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def _patch(path: str, body: dict | None = None) -> str:
    try:
        async with httpx.AsyncClient(base_url=MUSE_URL, timeout=15) as c:
            r = await c.patch(path, json=body or {})
            r.raise_for_status()
            return json.dumps(r.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Tools ────────────────────────────────────────────────────────────────────

async def get_digests(args, **kw):
    params = {}
    if args.get("limit"):
        params["limit"] = args["limit"]
    return await _get("/digests", params or None)

async def get_digest(args, **kw):
    return await _get(f"/digests/{args['id']}")

async def generate_digest(args, **kw):
    return await _post("/digests/generate")

async def get_ideas(args, **kw):
    params = {k: args[k] for k in ("format", "platform", "digestId") if args.get(k)}
    return await _get("/ideas", params or None)

async def get_content_kanban(args, **kw):
    return await _get("/content/kanban")

async def get_content_calendar(args, **kw):
    return await _get("/content/calendar", {"startDate": args["startDate"], "endDate": args["endDate"]})

async def create_content(args, **kw):
    return await _post("/content", args)

async def update_content_status(args, **kw):
    return await _patch(f"/content/{args['id']}/status", {"status": args["status"]})

async def schedule_content(args, **kw):
    body = {"scheduledDate": args["scheduledDate"]}
    if args.get("scheduledTime"):
        body["scheduledTime"] = args["scheduledTime"]
    return await _patch(f"/content/{args['id']}/schedule", body)

async def promote_idea(args, **kw):
    return await _post(f"/content/promote/{args['ideaId']}")

async def get_analytics(args, **kw):
    params = {k: args[k] for k in ("startDate", "endDate") if args.get(k)}
    return await _get("/analytics/dashboard", params or None)

async def get_reminders(args, **kw):
    params = {k: args[k] for k in ("status", "type") if args.get(k)}
    return await _get("/notifications/reminders", params or None)

async def trigger_discovery(args, **kw):
    return await _post("/schedule/trigger/discovery")


# ── Registration ─────────────────────────────────────────────────────────────

registry.register(
    name="muse_get_digests", toolset="muse", is_async=True, emoji="📰",
    schema={"name": "muse_get_digests", "description": "Get recent AI/ML content digests with curated articles, summaries, and relevance scores.", "parameters": {"type": "object", "properties": {"limit": {"type": "number", "description": "Number of digests to return"}}}},
    handler=lambda args, **kw: get_digests(args, **kw),
)

registry.register(
    name="muse_get_digest", toolset="muse", is_async=True, emoji="📰",
    schema={"name": "muse_get_digest", "description": "Get a specific digest with all items including AI summaries, topic tags, and why-it-matters.", "parameters": {"type": "object", "properties": {"id": {"type": "string", "description": "Digest ID"}}, "required": ["id"]}},
    handler=lambda args, **kw: get_digest(args, **kw),
)

registry.register(
    name="muse_generate_digest", toolset="muse", is_async=True, emoji="📰",
    schema={"name": "muse_generate_digest", "description": "Trigger generation of a new digest from recent articles. Fetches, filters, and ranks using AI.", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: generate_digest(args, **kw),
)

registry.register(
    name="muse_get_ideas", toolset="muse", is_async=True, emoji="💡",
    schema={"name": "muse_get_ideas", "description": "Get AI-generated content ideas. Filter by format (BLOG_POST, YOUTUBE_VIDEO, LINKEDIN_POST, TWITTER_POST, MEME) or platform.", "parameters": {"type": "object", "properties": {"format": {"type": "string"}, "platform": {"type": "string"}, "digestId": {"type": "string"}}}},
    handler=lambda args, **kw: get_ideas(args, **kw),
)

registry.register(
    name="muse_get_content_kanban", toolset="muse", is_async=True, emoji="📋",
    schema={"name": "muse_get_content_kanban", "description": "Get content kanban board: pieces grouped by status (IDEA, RESEARCHING, CREATING, READY, POSTED).", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: get_content_kanban(args, **kw),
)

registry.register(
    name="muse_get_content_calendar", toolset="muse", is_async=True, emoji="📅",
    schema={"name": "muse_get_content_calendar", "description": "Get scheduled content pieces for a date range.", "parameters": {"type": "object", "properties": {"startDate": {"type": "string", "description": "YYYY-MM-DD"}, "endDate": {"type": "string", "description": "YYYY-MM-DD"}}, "required": ["startDate", "endDate"]}},
    handler=lambda args, **kw: get_content_calendar(args, **kw),
)

registry.register(
    name="muse_create_content", toolset="muse", is_async=True, emoji="✍️",
    schema={"name": "muse_create_content", "description": "Create a new content piece in Muse.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}, "format": {"type": "string", "description": "BLOG_POST, YOUTUBE_VIDEO, LINKEDIN_POST, TWITTER_POST, MEME"}, "platform": {"type": "string"}, "body": {"type": "string"}, "notes": {"type": "string"}}, "required": ["title", "format"]}},
    handler=lambda args, **kw: create_content(args, **kw),
)

registry.register(
    name="muse_update_content_status", toolset="muse", is_async=True, emoji="📋",
    schema={"name": "muse_update_content_status", "description": "Move content through workflow: IDEA -> RESEARCHING -> CREATING -> READY -> POSTED.", "parameters": {"type": "object", "properties": {"id": {"type": "string"}, "status": {"type": "string"}}, "required": ["id", "status"]}},
    handler=lambda args, **kw: update_content_status(args, **kw),
)

registry.register(
    name="muse_schedule_content", toolset="muse", is_async=True, emoji="📅",
    schema={"name": "muse_schedule_content", "description": "Schedule a content piece for a specific date and optional time.", "parameters": {"type": "object", "properties": {"id": {"type": "string"}, "scheduledDate": {"type": "string", "description": "YYYY-MM-DD"}, "scheduledTime": {"type": "string", "description": "HH:MM"}}, "required": ["id", "scheduledDate"]}},
    handler=lambda args, **kw: schedule_content(args, **kw),
)

registry.register(
    name="muse_promote_idea", toolset="muse", is_async=True, emoji="🚀",
    schema={"name": "muse_promote_idea", "description": "Convert a content idea into a content piece for production.", "parameters": {"type": "object", "properties": {"ideaId": {"type": "string"}}, "required": ["ideaId"]}},
    handler=lambda args, **kw: promote_idea(args, **kw),
)

registry.register(
    name="muse_get_analytics", toolset="muse", is_async=True, emoji="📊",
    schema={"name": "muse_get_analytics", "description": "Get Muse content analytics dashboard with performance metrics.", "parameters": {"type": "object", "properties": {"startDate": {"type": "string"}, "endDate": {"type": "string"}}}},
    handler=lambda args, **kw: get_analytics(args, **kw),
)

registry.register(
    name="muse_get_reminders", toolset="muse", is_async=True, emoji="🔔",
    schema={"name": "muse_get_reminders", "description": "Get pending reminders from Muse.", "parameters": {"type": "object", "properties": {"status": {"type": "string", "description": "PENDING, SENT, DISMISSED, ACTED"}, "type": {"type": "string", "description": "POST_CONTENT, BRAND_MEME, ENGAGEMENT, CUSTOM"}}}},
    handler=lambda args, **kw: get_reminders(args, **kw),
)

registry.register(
    name="muse_trigger_discovery", toolset="muse", is_async=True, emoji="🔍",
    schema={"name": "muse_trigger_discovery", "description": "Manually trigger content discovery — fetch articles from all enabled sources.", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: trigger_discovery(args, **kw),
)
