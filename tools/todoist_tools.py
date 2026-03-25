"""Todoist (Task Manager) tools for Hermes Agent."""

import json
import os
import httpx

from tools.registry import registry

TODOIST_TOKEN = os.getenv("TODOIST_API_TOKEN", "")
TODOIST_URL = "https://api.todoist.com/rest/v2"


def _headers() -> dict:
    return {"Authorization": f"Bearer {TODOIST_TOKEN}", "Content-Type": "application/json"}


async def _get(path: str, params: dict | None = None) -> str:
    try:
        async with httpx.AsyncClient(base_url=TODOIST_URL, timeout=15, headers=_headers()) as c:
            r = await c.get(path, params=params)
            r.raise_for_status()
            return json.dumps(r.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def _post(path: str, body: dict | None = None) -> str:
    try:
        async with httpx.AsyncClient(base_url=TODOIST_URL, timeout=15, headers=_headers()) as c:
            r = await c.post(path, json=body or {})
            r.raise_for_status()
            return json.dumps(r.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Tools ────────────────────────────────────────────────────────────────────

async def get_projects(args, **kw):
    return await _get("/projects")

async def get_tasks(args, **kw):
    params = {k: args[k] for k in ("project_id", "section_id", "label", "filter") if args.get(k)}
    return await _get("/tasks", params or None)

async def create_task(args, **kw):
    return await _post("/tasks", args)

async def update_task(args, **kw):
    task_id = args.pop("id")
    return await _post(f"/tasks/{task_id}", args)

async def complete_task(args, **kw):
    try:
        async with httpx.AsyncClient(base_url=TODOIST_URL, timeout=15, headers=_headers()) as c:
            r = await c.post(f"/tasks/{args['id']}/close")
            r.raise_for_status()
            return json.dumps({"success": True})
    except Exception as e:
        return json.dumps({"error": str(e)})

async def get_sections(args, **kw):
    return await _get("/sections", {"project_id": args["project_id"]})

async def create_project(args, **kw):
    return await _post("/projects", args)

async def get_labels(args, **kw):
    return await _get("/labels")


# ── Registration ─────────────────────────────────────────────────────────────

def _check_todoist():
    return bool(TODOIST_TOKEN)

registry.register(
    name="todoist_get_projects", toolset="todoist", is_async=True, emoji="📁",
    check_fn=_check_todoist, requires_env=["TODOIST_API_TOKEN"],
    schema={"name": "todoist_get_projects", "description": "Get all Todoist projects.", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: get_projects(args, **kw),
)

registry.register(
    name="todoist_get_tasks", toolset="todoist", is_async=True, emoji="✅",
    check_fn=_check_todoist, requires_env=["TODOIST_API_TOKEN"],
    schema={"name": "todoist_get_tasks", "description": "Get Todoist tasks. Filter by project, section, label, or filter query ('today', 'overdue', 'p1').", "parameters": {"type": "object", "properties": {"project_id": {"type": "string"}, "section_id": {"type": "string"}, "label": {"type": "string"}, "filter": {"type": "string", "description": "Todoist filter: 'today', 'overdue', 'p1'"}}}},
    handler=lambda args, **kw: get_tasks(args, **kw),
)

registry.register(
    name="todoist_create_task", toolset="todoist", is_async=True, emoji="➕",
    check_fn=_check_todoist, requires_env=["TODOIST_API_TOKEN"],
    schema={"name": "todoist_create_task", "description": "Create a Todoist task. Use due_datetime + duration for calendar view scheduling.", "parameters": {"type": "object", "properties": {"content": {"type": "string", "description": "Task title"}, "description": {"type": "string"}, "project_id": {"type": "string"}, "section_id": {"type": "string"}, "priority": {"type": "number", "description": "1 (normal) to 4 (urgent)"}, "due_string": {"type": "string", "description": "Natural language: 'today', 'tomorrow 2pm'"}, "due_date": {"type": "string", "description": "YYYY-MM-DD"}, "due_datetime": {"type": "string", "description": "YYYY-MM-DDTHH:MM:SS for calendar view"}, "duration": {"type": "number", "description": "Duration amount"}, "duration_unit": {"type": "string", "description": "'minute' or 'day'"}, "labels": {"type": "array", "items": {"type": "string"}}}, "required": ["content"]}},
    handler=lambda args, **kw: create_task(args, **kw),
)

registry.register(
    name="todoist_update_task", toolset="todoist", is_async=True, emoji="✏️",
    check_fn=_check_todoist, requires_env=["TODOIST_API_TOKEN"],
    schema={"name": "todoist_update_task", "description": "Update an existing Todoist task (content, due date, priority, duration).", "parameters": {"type": "object", "properties": {"id": {"type": "string", "description": "Task ID"}, "content": {"type": "string"}, "description": {"type": "string"}, "priority": {"type": "number"}, "due_string": {"type": "string"}, "due_date": {"type": "string"}, "due_datetime": {"type": "string"}, "duration": {"type": "number"}, "duration_unit": {"type": "string"}, "labels": {"type": "array", "items": {"type": "string"}}}, "required": ["id"]}},
    handler=lambda args, **kw: update_task(args, **kw),
)

registry.register(
    name="todoist_complete_task", toolset="todoist", is_async=True, emoji="✅",
    check_fn=_check_todoist, requires_env=["TODOIST_API_TOKEN"],
    schema={"name": "todoist_complete_task", "description": "Mark a Todoist task as complete.", "parameters": {"type": "object", "properties": {"id": {"type": "string", "description": "Task ID"}}, "required": ["id"]}},
    handler=lambda args, **kw: complete_task(args, **kw),
)

registry.register(
    name="todoist_get_sections", toolset="todoist", is_async=True, emoji="📁",
    check_fn=_check_todoist, requires_env=["TODOIST_API_TOKEN"],
    schema={"name": "todoist_get_sections", "description": "Get sections within a Todoist project.", "parameters": {"type": "object", "properties": {"project_id": {"type": "string"}}, "required": ["project_id"]}},
    handler=lambda args, **kw: get_sections(args, **kw),
)

registry.register(
    name="todoist_create_project", toolset="todoist", is_async=True, emoji="📁",
    check_fn=_check_todoist, requires_env=["TODOIST_API_TOKEN"],
    schema={"name": "todoist_create_project", "description": "Create a new Todoist project.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "parent_id": {"type": "string"}, "color": {"type": "string"}, "favorite": {"type": "boolean"}}, "required": ["name"]}},
    handler=lambda args, **kw: create_project(args, **kw),
)

registry.register(
    name="todoist_get_labels", toolset="todoist", is_async=True, emoji="🏷️",
    check_fn=_check_todoist, requires_env=["TODOIST_API_TOKEN"],
    schema={"name": "todoist_get_labels", "description": "Get all Todoist labels.", "parameters": {"type": "object", "properties": {}}},
    handler=lambda args, **kw: get_labels(args, **kw),
)
