"""Todoist (Task Manager) tools for Hermes Agent."""

import os

from tools.http_client import ServiceClient
from tools.registry import registry

TODOIST_TOKEN = os.getenv("TODOIST_API_TOKEN", "")
TODOIST_URL = "https://api.todoist.com/rest/v2"


def _todoist_headers():
    return {"Authorization": f"Bearer {TODOIST_TOKEN}", "Content-Type": "application/json"}


_client = ServiceClient(TODOIST_URL, "Todoist", auth_fn=_todoist_headers)


def _check():
    return bool(TODOIST_TOKEN)


# ── Tools ────────────────────────────────────────────────────────────────────

async def get_projects(args, **kw):
    return await _client.get("/projects")

async def get_tasks(args, **kw):
    params = {k: args[k] for k in ("project_id", "section_id", "label", "filter") if args.get(k)}
    return await _client.get("/tasks", params or None)

async def create_task(args, **kw):
    return await _client.post("/tasks", args)

async def update_task(args, **kw):
    task_id = args["id"]
    body = {k: v for k, v in args.items() if k != "id"}
    return await _client.post(f"/tasks/{task_id}", body)

async def complete_task(args, **kw):
    return await _client.post(f"/tasks/{args['id']}/close")

async def get_sections(args, **kw):
    return await _client.get("/sections", {"project_id": args["project_id"]})

async def create_project(args, **kw):
    return await _client.post("/projects", args)

async def get_labels(args, **kw):
    return await _client.get("/labels")


# ── Registration ─────────────────────────────────────────────────────────────

registry.register(
    name="todoist_get_projects", toolset="todoist", is_async=True, emoji="📁",
    check_fn=_check, requires_env=["TODOIST_API_TOKEN"],
    schema={"description": "Get all Todoist projects.", "parameters": {"type": "object", "properties": {}}},
    handler=get_projects,
)

registry.register(
    name="todoist_get_tasks", toolset="todoist", is_async=True, emoji="✅",
    check_fn=_check, requires_env=["TODOIST_API_TOKEN"],
    schema={"description": "Get Todoist tasks. Filter by project, section, label, or filter query ('today', 'overdue', 'p1').", "parameters": {"type": "object", "properties": {"project_id": {"type": "string"}, "section_id": {"type": "string"}, "label": {"type": "string"}, "filter": {"type": "string", "description": "Todoist filter: 'today', 'overdue', 'p1'"}}}},
    handler=get_tasks,
)

registry.register(
    name="todoist_create_task", toolset="todoist", is_async=True, emoji="➕",
    check_fn=_check, requires_env=["TODOIST_API_TOKEN"],
    schema={"description": "Create a Todoist task. Use due_datetime + duration for calendar view scheduling.", "parameters": {"type": "object", "properties": {"content": {"type": "string", "description": "Task title"}, "description": {"type": "string"}, "project_id": {"type": "string"}, "section_id": {"type": "string"}, "priority": {"type": "number", "description": "1 (normal) to 4 (urgent)"}, "due_string": {"type": "string", "description": "Natural language: 'today', 'tomorrow 2pm'"}, "due_date": {"type": "string", "description": "YYYY-MM-DD"}, "due_datetime": {"type": "string", "description": "YYYY-MM-DDTHH:MM:SS for calendar view"}, "duration": {"type": "number", "description": "Duration amount"}, "duration_unit": {"type": "string", "description": "'minute' or 'day'"}, "labels": {"type": "array", "items": {"type": "string"}}}, "required": ["content"]}},
    handler=create_task,
)

registry.register(
    name="todoist_update_task", toolset="todoist", is_async=True, emoji="✏️",
    check_fn=_check, requires_env=["TODOIST_API_TOKEN"],
    schema={"description": "Update an existing Todoist task (content, due date, priority, duration).", "parameters": {"type": "object", "properties": {"id": {"type": "string", "description": "Task ID"}, "content": {"type": "string"}, "description": {"type": "string"}, "priority": {"type": "number"}, "due_string": {"type": "string"}, "due_date": {"type": "string"}, "due_datetime": {"type": "string"}, "duration": {"type": "number"}, "duration_unit": {"type": "string"}, "labels": {"type": "array", "items": {"type": "string"}}}, "required": ["id"]}},
    handler=update_task,
)

registry.register(
    name="todoist_complete_task", toolset="todoist", is_async=True, emoji="✅",
    check_fn=_check, requires_env=["TODOIST_API_TOKEN"],
    schema={"description": "Mark a Todoist task as complete.", "parameters": {"type": "object", "properties": {"id": {"type": "string", "description": "Task ID"}}, "required": ["id"]}},
    handler=complete_task,
)

registry.register(
    name="todoist_get_sections", toolset="todoist", is_async=True, emoji="📁",
    check_fn=_check, requires_env=["TODOIST_API_TOKEN"],
    schema={"description": "Get sections within a Todoist project.", "parameters": {"type": "object", "properties": {"project_id": {"type": "string"}}, "required": ["project_id"]}},
    handler=get_sections,
)

registry.register(
    name="todoist_create_project", toolset="todoist", is_async=True, emoji="📁",
    check_fn=_check, requires_env=["TODOIST_API_TOKEN"],
    schema={"description": "Create a new Todoist project.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "parent_id": {"type": "string"}, "color": {"type": "string"}, "favorite": {"type": "boolean"}}, "required": ["name"]}},
    handler=create_project,
)

registry.register(
    name="todoist_get_labels", toolset="todoist", is_async=True, emoji="🏷️",
    check_fn=_check, requires_env=["TODOIST_API_TOKEN"],
    schema={"description": "Get all Todoist labels.", "parameters": {"type": "object", "properties": {}}},
    handler=get_labels,
)
