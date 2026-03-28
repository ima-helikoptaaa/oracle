"""Muse (Content Engine) tools for Hermes Agent."""

import os

from tools.http_client import ServiceClient
from tools.registry import registry

MUSE_URL = os.getenv("MUSE_API_URL", "http://localhost:3002/api")

_client = ServiceClient(MUSE_URL, "Muse", timeout=15)


def _check():
    return bool(MUSE_URL)


# ── Tools ────────────────────────────────────────────────────────────────────

async def get_digests(args, **kw):
    params = {}
    if args.get("limit"):
        params["limit"] = args["limit"]
    return await _client.get("/digests", params or None)

async def get_digest(args, **kw):
    return await _client.get(f"/digests/{args['id']}")

async def generate_digest(args, **kw):
    return await _client.post("/digests/generate")

async def get_ideas(args, **kw):
    params = {k: args[k] for k in ("format", "platform", "digestId") if args.get(k)}
    return await _client.get("/ideas", params or None)

async def get_content_kanban(args, **kw):
    return await _client.get("/content/kanban")

async def get_content_calendar(args, **kw):
    return await _client.get("/content/calendar", {"from": args["startDate"], "to": args["endDate"]})

async def create_content(args, **kw):
    return await _client.post("/content", args)

async def update_content_status(args, **kw):
    return await _client.patch(f"/content/{args['id']}/status", {"status": args["status"]})

async def schedule_content(args, **kw):
    body = {"scheduledDate": args["scheduledDate"]}
    if args.get("scheduledTime"):
        body["scheduledTime"] = args["scheduledTime"]
    return await _client.patch(f"/content/{args['id']}/schedule", body)

async def promote_idea(args, **kw):
    return await _client.post(f"/content/promote/{args['ideaId']}")

async def get_analytics(args, **kw):
    params = {k: args[k] for k in ("startDate", "endDate") if args.get(k)}
    return await _client.get("/analytics/dashboard", params or None)

async def get_reminders(args, **kw):
    params = {k: args[k] for k in ("type", "limit") if args.get(k)}
    return await _client.get("/schedule/runs", params or None)

async def trigger_discovery(args, **kw):
    return await _client.post("/schedule/trigger/discovery")


# ── Registration ─────────────────────────────────────────────────────────────

registry.register(
    name="muse_get_digests", toolset="muse", is_async=True, emoji="📰",
    check_fn=_check, requires_env=["MUSE_API_URL"],
    schema={"description": "Get recent AI/ML content digests with curated articles, summaries, and relevance scores.", "parameters": {"type": "object", "properties": {"limit": {"type": "number", "description": "Number of digests to return"}}}},
    handler=get_digests,
)

registry.register(
    name="muse_get_digest", toolset="muse", is_async=True, emoji="📰",
    check_fn=_check, requires_env=["MUSE_API_URL"],
    schema={"description": "Get a specific digest with all items including AI summaries, topic tags, and why-it-matters.", "parameters": {"type": "object", "properties": {"id": {"type": "string", "description": "Digest ID"}}, "required": ["id"]}},
    handler=get_digest,
)

registry.register(
    name="muse_generate_digest", toolset="muse", is_async=True, emoji="📰",
    check_fn=_check, requires_env=["MUSE_API_URL"],
    schema={"description": "Trigger generation of a new digest from recent articles. Fetches, filters, and ranks using AI.", "parameters": {"type": "object", "properties": {}}},
    handler=generate_digest,
)

registry.register(
    name="muse_get_ideas", toolset="muse", is_async=True, emoji="💡",
    check_fn=_check, requires_env=["MUSE_API_URL"],
    schema={"description": "Get AI-generated content ideas. Filter by format (BLOG_POST, YOUTUBE_VIDEO, LINKEDIN_POST, TWITTER_POST, MEME) or platform.", "parameters": {"type": "object", "properties": {"format": {"type": "string"}, "platform": {"type": "string"}, "digestId": {"type": "string"}}}},
    handler=get_ideas,
)

registry.register(
    name="muse_get_content_kanban", toolset="muse", is_async=True, emoji="📋",
    check_fn=_check, requires_env=["MUSE_API_URL"],
    schema={"description": "Get content kanban board: pieces grouped by status (IDEA, RESEARCHING, CREATING, READY, POSTED).", "parameters": {"type": "object", "properties": {}}},
    handler=get_content_kanban,
)

registry.register(
    name="muse_get_content_calendar", toolset="muse", is_async=True, emoji="📅",
    check_fn=_check, requires_env=["MUSE_API_URL"],
    schema={"description": "Get scheduled content pieces for a date range.", "parameters": {"type": "object", "properties": {"startDate": {"type": "string", "description": "YYYY-MM-DD"}, "endDate": {"type": "string", "description": "YYYY-MM-DD"}}, "required": ["startDate", "endDate"]}},
    handler=get_content_calendar,
)

registry.register(
    name="muse_create_content", toolset="muse", is_async=True, emoji="✍️",
    check_fn=_check, requires_env=["MUSE_API_URL"],
    schema={"description": "Create a new content piece in Muse.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}, "format": {"type": "string", "description": "BLOG_POST, YOUTUBE_VIDEO, LINKEDIN_POST, TWITTER_POST, MEME"}, "platform": {"type": "string"}, "body": {"type": "string"}, "notes": {"type": "string"}}, "required": ["title", "format"]}},
    handler=create_content,
)

registry.register(
    name="muse_update_content_status", toolset="muse", is_async=True, emoji="📋",
    check_fn=_check, requires_env=["MUSE_API_URL"],
    schema={"description": "Move content through workflow: IDEA -> RESEARCHING -> CREATING -> READY -> POSTED.", "parameters": {"type": "object", "properties": {"id": {"type": "string"}, "status": {"type": "string"}}, "required": ["id", "status"]}},
    handler=update_content_status,
)

registry.register(
    name="muse_schedule_content", toolset="muse", is_async=True, emoji="📅",
    check_fn=_check, requires_env=["MUSE_API_URL"],
    schema={"description": "Schedule a content piece for a specific date and optional time.", "parameters": {"type": "object", "properties": {"id": {"type": "string"}, "scheduledDate": {"type": "string", "description": "YYYY-MM-DD"}, "scheduledTime": {"type": "string", "description": "HH:MM"}}, "required": ["id", "scheduledDate"]}},
    handler=schedule_content,
)

registry.register(
    name="muse_promote_idea", toolset="muse", is_async=True, emoji="🚀",
    check_fn=_check, requires_env=["MUSE_API_URL"],
    schema={"description": "Convert a content idea into a content piece for production.", "parameters": {"type": "object", "properties": {"ideaId": {"type": "string"}}, "required": ["ideaId"]}},
    handler=promote_idea,
)

registry.register(
    name="muse_get_analytics", toolset="muse", is_async=True, emoji="📊",
    check_fn=_check, requires_env=["MUSE_API_URL"],
    schema={"description": "Get Muse content analytics dashboard with performance metrics.", "parameters": {"type": "object", "properties": {"startDate": {"type": "string"}, "endDate": {"type": "string"}}}},
    handler=get_analytics,
)

registry.register(
    name="muse_get_reminders", toolset="muse", is_async=True, emoji="🔔",
    check_fn=_check, requires_env=["MUSE_API_URL"],
    schema={"description": "Get recent Muse pipeline runs (discovery, digest generation) and their status.", "parameters": {"type": "object", "properties": {"type": {"type": "string", "description": "Filter by run type: discovery, digest"}, "limit": {"type": "number", "description": "Number of runs to return"}}}},
    handler=get_reminders,
)

registry.register(
    name="muse_trigger_discovery", toolset="muse", is_async=True, emoji="🔍",
    check_fn=_check, requires_env=["MUSE_API_URL"],
    schema={"description": "Manually trigger content discovery — fetch articles from all enabled sources.", "parameters": {"type": "object", "properties": {}}},
    handler=trigger_discovery,
)
