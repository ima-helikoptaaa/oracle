#!/usr/bin/env python3
"""One-time Google OAuth setup for Oracle.

Opens a browser for Google Sign-In, captures the refresh token,
exchanges it for a Firebase ID token, and saves both to ~/.hermes/.env.

Usage:
    python oracle/auth_setup.py
"""

import http.server
import json
import os
import sys
import urllib.parse
import webbrowser

FIREBASE_API_KEY = "AIzaSyDQA0UvfCS9j6S1drFWf3zDHziKLwhdxLM"
# This is the OAuth 2.0 client ID from your Firebase/GCP project (web client)
GOOGLE_CLIENT_ID = "103377356088-chhvt9op75epfle4n8ac7dh7je0sp24v.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = ""  # iOS client IDs don't have secrets; we need a web client ID

REDIRECT_PORT = 9004
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"
SCOPES = "openid email profile"

ENV_FILE = os.path.expanduser("~/.hermes/.env")


def get_web_client_id():
    """Prompt for web OAuth client ID if the iOS one won't work."""
    print()
    print("=" * 60)
    print("  Oracle — Firebase Auth Setup")
    print("=" * 60)
    print()
    print("This script needs a Web OAuth 2.0 Client ID from your")
    print("Google Cloud Console (not the iOS client ID).")
    print()
    print("To get one:")
    print("  1. Go to https://console.cloud.google.com/apis/credentials")
    print(f"     (project: progression-df0af)")
    print("  2. Click '+ CREATE CREDENTIALS' > 'OAuth client ID'")
    print("  3. Application type: 'Web application'")
    print("  4. Add authorized redirect URI: http://localhost:9004")
    print("  5. Copy the Client ID and Client Secret")
    print()

    client_id = input("Web OAuth Client ID: ").strip()
    client_secret = input("Web OAuth Client Secret: ").strip()

    if not client_id or not client_secret:
        print("Both Client ID and Client Secret are required.")
        sys.exit(1)

    return client_id, client_secret


def start_oauth_flow(client_id: str):
    """Open browser for Google OAuth consent."""
    params = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
    })
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{params}"
    print()
    print("Opening browser for Google Sign-In...")
    print(f"If it doesn't open, visit: {url}")
    print()
    webbrowser.open(url)


def wait_for_callback() -> str:
    """Run a tiny HTTP server to capture the OAuth callback code."""
    auth_code = None

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal auth_code
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)

            if "code" in params:
                auth_code = params["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h2>Auth successful! You can close this tab.</h2>")
            else:
                error = params.get("error", ["unknown"])[0]
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(f"<h2>Auth failed: {error}</h2>".encode())

        def log_message(self, format, *args):
            pass  # suppress logs

    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), Handler)
    print(f"Waiting for OAuth callback on port {REDIRECT_PORT}...")
    server.handle_request()
    server.server_close()

    if not auth_code:
        print("Failed to capture authorization code.")
        sys.exit(1)

    return auth_code


def exchange_code_for_tokens(code: str, client_id: str, client_secret: str) -> dict:
    """Exchange auth code for Google tokens."""
    import urllib.request

    data = urllib.parse.urlencode({
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }).encode()

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def exchange_for_firebase_token(google_id_token: str) -> dict:
    """Exchange Google ID token for Firebase ID token."""
    import urllib.request

    data = json.dumps({
        "postBody": f"id_token={google_id_token}&providerId=google.com",
        "requestUri": "http://localhost",
        "returnIdpCredential": True,
        "returnSecureToken": True,
    }).encode()

    req = urllib.request.Request(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_API_KEY}",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def save_to_env(refresh_token: str):
    """Save or update GOOGLE_REFRESH_TOKEN in ~/.hermes/.env."""
    lines = []
    found = False

    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                if line.startswith("GOOGLE_REFRESH_TOKEN="):
                    lines.append(f"GOOGLE_REFRESH_TOKEN={refresh_token}\n")
                    found = True
                elif line.startswith("FIREBASE_ID_TOKEN="):
                    # Remove old static token
                    continue
                else:
                    lines.append(line)

    if not found:
        lines.append(f"GOOGLE_REFRESH_TOKEN={refresh_token}\n")

    os.makedirs(os.path.dirname(ENV_FILE), exist_ok=True)
    with open(ENV_FILE, "w") as f:
        f.writelines(lines)


def main():
    client_id, client_secret = get_web_client_id()

    start_oauth_flow(client_id)
    code = wait_for_callback()

    print("Exchanging code for tokens...")
    google_tokens = exchange_code_for_tokens(code, client_id, client_secret)
    google_refresh_token = google_tokens["refresh_token"]

    print("Exchanging for Firebase token...")
    firebase_data = exchange_for_firebase_token(google_tokens["id_token"])

    print(f"Signed in as: {firebase_data.get('email', 'unknown')}")

    save_to_env(google_refresh_token)
    print()
    print(f"Saved GOOGLE_REFRESH_TOKEN to {ENV_FILE}")
    print("Oracle will now auto-refresh your Firebase token. You're all set!")


if __name__ == "__main__":
    main()
