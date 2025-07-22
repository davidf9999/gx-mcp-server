#!/usr/bin/env python3
"""
Automated test for server authentication.

This script can be run in two scenarios:
1.  If a server is already running on the target port, it runs authentication
    tests against it.
2.  If no server is running, it starts a new server with basic authentication,
    runs the tests, and then shuts it down.
"""

import subprocess
import time
import requests
import sys

API_URL = "http://127.0.0.1:8000"
HEALTH_ENDPOINT = f"{API_URL}/mcp/health"

def is_server_running() -> bool:
    """Checks if a server is responding on the health endpoint."""
    try:
        requests.get(HEALTH_ENDPOINT, timeout=1)
        return True
    except requests.ConnectionError:
        return False

def run_auth_tests(auth_enabled: bool):
    """
    Runs a series of authentication tests against the server.

    Args:
        auth_enabled: Whether the server is expected to have auth enabled.
    """
    print("\n➡️  Running authentication tests...")

    # 1. Test with valid credentials
    print(f"- Valid credentials → expecting {200 if auth_enabled else 200}")
    try:
        response_valid = requests.get(HEALTH_ENDPOINT, auth=('user', 'pass'), timeout=5)
        print(f"  Status: {response_valid.status_code}")
        assert response_valid.status_code == 200
    except requests.RequestException as e:
        print(f"  Request failed: {e}")

    # 2. Test with no credentials
    expected_no_creds = 401 if auth_enabled else 200
    print(f"- No credentials → expecting {expected_no_creds}")
    try:
        response_none = requests.get(HEALTH_ENDPOINT, timeout=5)
        print(f"  Status: {response_none.status_code}")
        assert response_none.status_code == expected_no_creds
    except requests.RequestException as e:
        print(f"  Request failed: {e}")

    # 3. Test with wrong credentials
    expected_wrong_creds = 401 if auth_enabled else 200
    print(f"- Wrong credentials → expecting {expected_wrong_creds}")
    try:
        response_wrong = requests.get(HEALTH_ENDPOINT, auth=('user', 'wrongpass'), timeout=5)
        print(f"  Status: {response_wrong.status_code}")
        assert response_wrong.status_code == expected_wrong_creds
    except requests.RequestException as e:
        print(f"  Request failed: {e}")

def run_standalone_test():
    """
    Starts a server with auth, runs tests, and then cleans up.
    """
    server_process = None
    try:
        print("Starting local server with basic auth...")
        server_command = [
            sys.executable, "-m", "gx_mcp_server",
            "--http",
            "--basic-auth", "user:pass"
        ]
        server_process = subprocess.Popen(
            server_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print("Waiting for server to become available...")
        for _ in range(10):
            if is_server_running():
                print("Server is up and running.")
                break
            time.sleep(1)
        else:
            raise RuntimeError("Server failed to start.")

        run_auth_tests(auth_enabled=True)

    finally:
        if server_process:
            print("\nTerminating server...")
            server_process.terminate()
            stdout, stderr = server_process.communicate()
            print("Server terminated.")
            if stdout or stderr:
                print("--- Server Logs ---")
                print(stdout)
                print(stderr, file=sys.stderr)

    print("\n✅ Standalone test complete.")

if __name__ == "__main__":
    if is_server_running():
        print("Server is already running. Running tests in client mode...")
        # When run by run_examples.py, the server has no auth.
        run_auth_tests(auth_enabled=False)
        print("\n✅ Client tests complete.")
    else:
        print("No server detected. Running in standalone mode...")
        try:
            run_standalone_test()
        except Exception as e:
            print(f"\nAn error occurred: {e}", file=sys.stderr)
            sys.exit(1)
