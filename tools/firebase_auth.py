"""Firebase auth with automatic token refresh via Google refresh token."""

import asyncio
import json
import os
import time

import httpx

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN", "")

_cached_id_token: str | None = None
_token_expires_at: float = 0
_lock = asyncio.Lock()


async def _refresh_google_token() -> dict:
    """Use Google OAuth2 to refresh and get a fresh Google ID token."""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": GOOGLE_REFRESH_TOKEN,
                "grant_type": "refresh_token",
            },
        )
        r.raise_for_status()
        return r.json()


async def _exchange_for_firebase_token(google_id_token: str) -> dict:
    """Exchange a Google ID token for a Firebase ID token."""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_API_KEY}",
            json={
                "postBody": f"id_token={google_id_token}&providerId=google.com",
                "requestUri": "http://localhost",
                "returnIdpCredential": True,
                "returnSecureToken": True,
            },
        )
        r.raise_for_status()
        return r.json()


async def _do_refresh() -> str | None:
    """Perform the actual token refresh (called under lock)."""
    global _cached_id_token, _token_expires_at

    google_tokens = await _refresh_google_token()
    google_id_token = google_tokens["id_token"]

    firebase_data = await _exchange_for_firebase_token(google_id_token)

    _cached_id_token = firebase_data["idToken"]
    _token_expires_at = time.time() + int(firebase_data.get("expiresIn", 3600))
    return _cached_id_token


async def get_token() -> str | None:
    """Return a valid Firebase ID token, refreshing if needed."""
    global _cached_id_token, _token_expires_at

    if not GOOGLE_REFRESH_TOKEN:
        return os.getenv("FIREBASE_ID_TOKEN") or None

    if _cached_id_token and time.time() < _token_expires_at - 60:
        return _cached_id_token

    async with _lock:
        # Double-check after acquiring lock (another coroutine may have refreshed)
        if _cached_id_token and time.time() < _token_expires_at - 60:
            return _cached_id_token

        try:
            return await _do_refresh()
        except Exception as e:
            print(f"[firebase_auth] Token refresh failed: {e}")
            return _cached_id_token


async def force_refresh() -> str | None:
    """Force a token refresh regardless of expiry. Used on 401 retry."""
    async with _lock:
        try:
            return await _do_refresh()
        except Exception as e:
            print(f"[firebase_auth] Force refresh failed: {e}")
            return _cached_id_token


async def get_auth_headers() -> dict:
    """Return Authorization header dict, or empty dict if no token."""
    token = await get_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}
