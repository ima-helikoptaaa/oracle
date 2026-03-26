"""Firebase auth with automatic token refresh via Google refresh token."""

import json
import os
import time

import httpx

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "AIzaSyDQA0UvfCS9j6S1drFWf3zDHziKLwhdxLM")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN", "")

_cached_id_token: str | None = None
_token_expires_at: float = 0


async def get_token() -> str | None:
    """Return a valid Firebase ID token, refreshing if needed."""
    global _cached_id_token, _token_expires_at

    if not GOOGLE_REFRESH_TOKEN:
        return os.getenv("FIREBASE_ID_TOKEN") or None

    if _cached_id_token and time.time() < _token_expires_at - 60:
        return _cached_id_token

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"https://securetoken.googleapis.com/v1/token?key={FIREBASE_API_KEY}",
                json={
                    "grant_type": "refresh_token",
                    "refresh_token": GOOGLE_REFRESH_TOKEN,
                },
            )
            r.raise_for_status()
            data = r.json()

        _cached_id_token = data["id_token"]
        _token_expires_at = time.time() + int(data.get("expires_in", 3600))
        return _cached_id_token

    except Exception as e:
        print(f"[firebase_auth] Token refresh failed: {e}")
        return _cached_id_token


async def get_auth_headers() -> dict:
    """Return Authorization header dict, or empty dict if no token."""
    token = await get_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}
