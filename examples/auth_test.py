#!/usr/bin/env python3
"""
auth_test_extended.py
---------------------
End-to-end manual security regression tester for gx-mcp-server (minimal-security branch).

What it does:
  * Starts the server locally if nothing is listening.
  * Tests:
      - Basic Auth: valid / missing / wrong creds
      - Bearer Auth: fetch token (client_credentials) + valid / missing / bad / tampered
      - Origin / Host header validation (expects 403/401 on bad origins)
      - CORS preflight OPTIONS flow
      - Optional HTTP -> HTTPS redirect check
  * Prints a colored summary of passes/fails.

Edit the CONFIG section to match your server flags and endpoints.

Usage:
  $ python examples/auth_test.py               # auto-detect/run server, run all tests
  $ python examples/auth_test.py --api http://127.0.0.1:8000 --skip-basic
  $ python examples/auth_test.py --keep-server # don

Requirements:
  pip install requests colorama
"""

from __future__ import annotations
import argparse
import base64
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

import requests
from colorama import Fore, Style, init as colorama_init

# ----------------------- CONFIG (edit to your setup) ----------------------- #
API_DEFAULT = "http://127.0.0.1:8000"
HEALTH_PATH = "/mcp/health"
TOKEN_ENDPOINT = "/oauth/token"  # adjust if your server exposes another path
PROTECTED_PATH = HEALTH_PATH # "/load_dataset"  # "/mcp/health"? path that requires Bearer (or Basic) – adjust!
BASIC_USER = "user"
BASIC_PASS = "pass"

# If your server needs these to mint tokens (client_credentials flow):
CLIENT_ID = os.getenv("GX_CLIENT_ID", "demo-client")
CLIENT_SECRET = os.getenv("GX_CLIENT_SECRET", "demo-secret")
TOKEN_GRANT_TYPE = "client_credentials"

# How to start the server (basic + bearer flags shown as example)
SERVER_CMD = [
    sys.executable,
    "-m",
    "gx_mcp_server",
    "--http",
    "--basic-auth",
    f"{BASIC_USER}:{BASIC_PASS}",
    # "--bearer-issuer",
    # "local",  # <— adjust for your implementation
    "--allowed-origins",
    "http://localhost",
    "http://127.0.0.1",
]
SERVER_START_TIMEOUT_SEC = 12
# --------------------------------------------------------------------------- #


@dataclass
class TestResult:
    name: str
    passed: bool
    status: Optional[int] = None
    detail: str = ""


def wait_for(url: str, timeout: int = 10) -> bool:
    for _ in range(timeout):
        try:
            # When server requires auth, health check needs it too
            headers = get_basic_headers(BASIC_USER, BASIC_PASS)
            requests.get(url, timeout=1, headers=headers)
            return True
        except requests.RequestException:
            time.sleep(1)
    return False


def is_up(url: str) -> bool:
    try:
        headers = get_basic_headers(BASIC_USER, BASIC_PASS)
        requests.get(url, timeout=1, headers=headers)
        return True
    except requests.RequestException:
        return False


def start_server_if_needed(api_base: str) -> Tuple[Optional[subprocess.Popen], bool]:
    health_url = api_base + HEALTH_PATH
    if is_up(health_url):
        print("▶ Server already running.")
        return None, False
    print("▶ Starting local server...")
    proc = subprocess.Popen(
        SERVER_CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if not wait_for(health_url, SERVER_START_TIMEOUT_SEC):
        proc.terminate()
        out, err = proc.communicate(timeout=3)
        raise RuntimeError(f"Server failed to start.\nSTDOUT:\n{out}\nSTDERR:\n{err}")
    print("✅ Server is up.")
    return proc, True


def stop_server(proc: Optional[subprocess.Popen]):
    if proc:
        print("▶ Terminating server...")
        proc.terminate()
        try:
            out, err = proc.communicate(timeout=5)
            if out or err:
                print("--- Server stdout ---")
                print(out)
                print("--- Server stderr ---", file=sys.stderr)
                print(err, file=sys.stderr)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("✅ Server stopped.")


# ---------- Auth helpers --------------------------------------------------- #


def get_basic_headers(user: str, pwd: str) -> Dict[str, str]:
    token = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def fetch_bearer_token(api: str) -> str:
    url = api + TOKEN_ENDPOINT
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": TOKEN_GRANT_TYPE,
    }
    r = requests.post(url, data=data, timeout=5)
    r.raise_for_status()
    js = r.json()
    return js.get("access_token") or js["token"]  # support either key name


# ---------- Test functions ------------------------------------------------- #


def expect_status(
    fn: Callable[[], requests.Response], want: int, name: str
) -> TestResult:
    try:
        resp = fn()
        passed = resp.status_code == want
        return TestResult(
            name, passed, resp.status_code, detail=resp.text[:200] if not passed else ""
        )
    except Exception as e:
        return TestResult(name, False, None, f"Exception: {e}")


def run_basic_tests(api: str, enabled: bool) -> list[TestResult]:
    print("\n🔐 Basic Auth tests")
    results = []
    url = api + HEALTH_PATH

    # valid
    results.append(
        expect_status(
            lambda: requests.get(
                url, headers=get_basic_headers(BASIC_USER, BASIC_PASS), timeout=5
            ),
            200,
            "Basic valid creds",
        )
    )
    # missing
    results.append(
        expect_status(
            lambda: requests.get(url, timeout=5),
            401 if enabled else 200,
            "Basic missing creds",
        )
    )
    # wrong
    results.append(
        expect_status(
            lambda: requests.get(
                url, headers=get_basic_headers(BASIC_USER, "wrongpass"), timeout=5
            ),
            401 if enabled else 200,
            "Basic wrong creds",
        )
    )
    return results


def run_bearer_tests(api: str, enabled: bool) -> list[TestResult]:
    print("\n🪙 Bearer Token tests")
    results = []
    url = api + PROTECTED_PATH

    if not enabled:
        results.append(
            TestResult("Bearer disabled - skipping", True)
        )
        return results

    token = None
    try:
        token = fetch_bearer_token(api)
        results.append(TestResult("Fetch token", True))
    except Exception as e:
        results.append(
            TestResult("Fetch token", False, None, f"Token fetch failed: {e}")
        )
        return results

    def hdr(tok):
        return {"Authorization": f"Bearer {tok}"}

    # valid
    results.append(
        expect_status(
            lambda: requests.get(url, headers=hdr(token), timeout=5),
            200,
            "Bearer valid token",
        )
    )

    # missing
    results.append(
        expect_status(
            lambda: requests.get(url, timeout=5), 401, "Bearer missing header"
        )
    )

    # bad
    results.append(
        expect_status(
            lambda: requests.get(url, headers=hdr("badtoken"), timeout=5),
            401,
            "Bearer invalid token",
        )
    )

    # tampered / expired simulation (truncate last char)
    if len(token) > 5:
        bad2 = token[:-1] + "x"
        results.append(
            expect_status(
                lambda: requests.get(url, headers=hdr(bad2), timeout=5),
                401,
                "Bearer tampered token",
            )
        )
    return results


def run_origin_host_tests(api: str, expect_block: bool, basic_auth_enabled: bool) -> list[TestResult]:
    print("\n🌐 Origin/Host header validation")
    results = []
    url = api + PROTECTED_PATH
    
    auth_headers = get_basic_headers(BASIC_USER, BASIC_PASS) if basic_auth_enabled else {}

    # Allowed origin
    headers = {"Origin": "http://localhost", **auth_headers}
    results.append(
        expect_status(
            lambda: requests.get(url, headers=headers, timeout=5),
            200,
            "Origin allowed",
        )
    )

    # Disallowed origin
    headers = {"Origin": "http://evil.example", **auth_headers}
    results.append(
        expect_status(
            lambda: requests.get(url, headers=headers, timeout=5),
            400 if expect_block else 200,
            "Origin disallowed",
        )
    )

    # Host header spoof (override Host) - this is harder to test reliably
    # as `requests` might not allow setting it directly for security.
    # This test is more of an idea than a guarantee.
    # headers = {"Host": "evil.example", **auth_headers}
    # results.append(
    #     expect_status(
    #         lambda: requests.get(url, headers=headers, timeout=5),
    #         401 if basic_auth_enabled else 200, # Should be caught by auth, not origin
    #         "Host spoofed",
    #     )
    # )
    return results


def run_cors_preflight(api: str, expect_cors_headers: bool) -> list[TestResult]:
    print("\n🛫 CORS preflight (OPTIONS)")
    results = []
    url = api + PROTECTED_PATH

    def do():
        return requests.options(
            url,
            headers={
                "Origin": "http://localhost",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type, Authorization",
            },
            timeout=5,
        )

    r = None
    try:
        r = do()
        # CORS preflight should not be blocked by auth, should return 200/204
        ok = (r.status_code in (200, 204))
        detail = ""
        if not ok:
            detail = str(dict(r.headers))[:200]
        elif expect_cors_headers and "access-control-allow-origin" not in r.headers:
             ok = False
             detail = "Missing 'access-control-allow-origin' header"

        results.append(
            TestResult("CORS preflight", ok, r.status_code, detail=detail)
        )
    except Exception as e:
        results.append(TestResult("CORS preflight", False, None, f"Exception: {e}"))
    return results


def run_https_redirect_test(api: str) -> list[TestResult]:
    # Only meaningful if you run an HTTPS endpoint as well
    if api.startswith("https://"):
        return []
    print("\n🔐 HTTPS redirect check (optional)")
    results = []
    # try plain http to a server that should redirect/forbid
    http_url = api.replace("https://", "http://")
    url = http_url + PROTECTED_PATH
    results.append(
        expect_status(
            lambda: requests.get(url, allow_redirects=False, timeout=5),
            401, # Expect auth error, not redirect
            "HTTP to HTTPS redirect/deny",
        )
    )
    return results


# ------------------------- Main runner ------------------------------------- #


def print_summary(results: list[TestResult]):
    print("\n──────── Summary ────────")
    ok = 0
    for res in results:
        color = Fore.GREEN if res.passed else Fore.RED
        status = f" ({res.status})" if res.status is not None else ""
        print(
            f"{color}{'✔' if res.passed else '✘'} {res.name}{status}{Style.RESET_ALL}"
        )
        if not res.passed and res.detail:
            print(f"    {Fore.YELLOW}{res.detail}{Style.RESET_ALL}")
        ok += int(res.passed)
    print(f"\nTotal: {ok}/{len(results)} passed")
    print("─────────────────────────")


def parse_args():
    ap = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--api", default=API_DEFAULT, help="Base API URL")
    ap.add_argument("--skip-basic", action="store_true")
    ap.add_argument("--skip-bearer", action="store_true")
    ap.add_argument("--skip-origin", action="store_true")
    ap.add_argument("--skip-cors", action="store_true")
    ap.add_argument("--skip-https", action="store_true")
    ap.add_argument(
        "--keep-server",
        action="store_true",
        help="Do not stop server when tests finish",
    )
    
    # These flags can be auto-detected from SERVER_CMD now
    ap.add_argument("--basic-enabled", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--bearer-enabled", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--expect-origin-block", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--expect-cors-headers", action="store_true", help=argparse.SUPPRESS)

    args = ap.parse_args()

    # Auto-detect config from SERVER_CMD
    args.basic_enabled = "--basic-auth" in SERVER_CMD
    args.bearer_enabled = "--bearer-issuer" in SERVER_CMD
    args.expect_origin_block = "--allowed-origins" in SERVER_CMD
    args.expect_cors_headers = args.expect_origin_block

    return args


def main():
    colorama_init()
    args = parse_args()

    proc, started = start_server_if_needed(args.api)

    results: list[TestResult] = []
    try:
        if not args.skip_basic:
            results += run_basic_tests(args.api, enabled=args.basic_enabled)
        if not args.skip_bearer:
            results += run_bearer_tests(args.api, enabled=args.bearer_enabled)
        if not args.skip_origin:
            results += run_origin_host_tests(
                args.api, 
                expect_block=args.expect_origin_block,
                basic_auth_enabled=args.basic_enabled
            )
        if not args.skip_cors:
            results += run_cors_preflight(
                args.api, expect_cors_headers=args.expect_cors_headers
            )
        if not args.skip_https:
            results += run_https_redirect_test(args.api)
    finally:
        if started and not args.keep_server:
            stop_server(proc)

    print_summary(results)
    failed = [r for r in results if not r.passed]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

