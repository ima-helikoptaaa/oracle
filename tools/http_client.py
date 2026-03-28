"""Shared async HTTP client with connection pooling, error handling, and auth support."""

import asyncio
import json

import httpx


def _format_http_error(service_name: str, e: httpx.HTTPStatusError) -> str:
    s = e.response.status_code
    if s in (502, 503):
        return json.dumps({"error": f"{service_name} service unavailable — backend is down", "status": s})
    if s in (401, 403):
        return json.dumps({"error": f"Auth failed ({s}) — check credentials", "status": s})
    if s == 404:
        return json.dumps({"error": f"Endpoint not found: {e.request.url.path}", "status": 404})
    return json.dumps({"error": f"HTTP {s}: {e.response.text[:200]}", "status": s})


class ServiceClient:
    """Reusable async HTTP client for a backend service.

    Supports optional auth header injection and connection pooling.
    """

    def __init__(self, base_url: str, service_name: str, auth_fn=None, timeout: float = 15):
        self._base_url = base_url
        self._service_name = service_name
        self._auth_fn = auth_fn
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._lock = asyncio.Lock()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)
        return self._client

    async def _headers(self) -> dict:
        if self._auth_fn:
            result = self._auth_fn()
            if asyncio.iscoroutine(result):
                return await result
            return result
        return {}

    async def _request(self, method: str, path: str, params: dict | None = None, body: dict | None = None) -> str:
        try:
            client = await self._get_client()
            headers = await self._headers()
            r = await client.request(method, path, params=params, json=body, headers=headers)
            r.raise_for_status()
            if r.status_code == 204 or not r.content:
                return json.dumps({"success": True})
            return json.dumps(r.json(), ensure_ascii=False)
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403) and self._auth_fn:
                return await self._retry_after_auth_refresh(method, path, params, body)
            return _format_http_error(self._service_name, e)
        except Exception as e:
            return json.dumps({"error": str(e)})

    async def _retry_after_auth_refresh(self, method: str, path: str, params: dict | None, body: dict | None) -> str:
        """Single retry after forcing a token refresh on 401/403."""
        try:
            from tools.firebase_auth import force_refresh
            await force_refresh()
            client = await self._get_client()
            headers = await self._headers()
            r = await client.request(method, path, params=params, json=body, headers=headers)
            r.raise_for_status()
            if r.status_code == 204 or not r.content:
                return json.dumps({"success": True})
            return json.dumps(r.json(), ensure_ascii=False)
        except httpx.HTTPStatusError as e:
            return _format_http_error(self._service_name, e)
        except Exception as e:
            return json.dumps({"error": str(e)})

    async def get(self, path: str, params: dict | None = None) -> str:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, body: dict | None = None) -> str:
        return await self._request("POST", path, body=body)

    async def put(self, path: str, body: dict | None = None) -> str:
        return await self._request("PUT", path, body=body)

    async def patch(self, path: str, body: dict | None = None) -> str:
        return await self._request("PATCH", path, body=body)

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
