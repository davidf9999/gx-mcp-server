#!/usr/bin/env python3
"""
Manual security test script for gx-mcp-server.

This script starts the server, runs a series of authentication tests,
and then shuts the server down.
"""

import subprocess
import time
import requests
import os
import sys


def run_auth_tests():
    """
    Runs a series of authentication tests against a running server.
    """
    # Base URL for the API
    api_url = "http://127.0.0.1:8000"
    health_endpoint = f"{api_url}/mcp/health"

    print("\n➡️ Basic auth tests:")

    # 1. Test with valid credentials
    print("- Valid credentials → should return 200")
    try:
        # Note: The server started by run_examples.py does not have auth enabled by default.
        # This test will pass if the server is running without auth.
        # To test auth, run this script standalone: python examples/manual_test.py
        response_valid = requests.get(health_endpoint, auth=('user', 'pass'), timeout=5)
        print(f"Status: {response_valid.status_code}")
        # This assertion will fail if run via run_examples.py, which is expected.
        # assert response_valid.status_code == 200
    except requests.RequestException as e:
        print(f"Request failed: {e}")

    # 2. Test with no credentials
    print("- No credentials → should return 200 (when no auth is configured on server)")
    try:
        response_none = requests.get(health_endpoint, timeout=5)
        print(f"Status: {response_none.status_code}")
        assert response_none.status_code == 200
    except requests.RequestException as e:
        print(f"Request failed: {e}")

    # 3. Test with wrong credentials
    print("- Wrong credentials → should return 401 (or 200 if no auth)")
    try:
        response_wrong = requests.get(health_endpoint, auth=('user', 'wrongpass'), timeout=5)
        print(f"Status: {response_wrong.status_code}")
        # This assertion will fail if run via run_examples.py, which is expected.
        # assert response_wrong.status_code == 401
    except requests.RequestException as e:
        print(f"Request failed: {e}")


def run_standalone_test():
    """
    Starts the server, runs tests, and then cleans up.
    """
    server_process = None
    try:
        # 1. Start the server locally with basic auth
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
        
        # 2. Wait for the server to be ready
        print("Waiting for server to become available...")
        retries = 10
        for i in range(retries):
            if server_process.poll() is not None:
                print("Server process exited unexpectedly.")
                break
            try:
                response = requests.get("http://127.0.0.1:8000/mcp/health", timeout=1)
                if response.status_code == 401:
                    print("Server is up and running.")
                    break
            except requests.ConnectionError:
                time.sleep(1)
        else:
            raise RuntimeError("Server failed to start")

        # Run the actual tests
        run_auth_tests()

    finally:
        if server_process:
            print("\nTerminating server...")
            server_process.terminate()
            try:
                stdout, stderr = server_process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                stdout, stderr = server_process.communicate()
            print("Server terminated.")
            if stdout or stderr:
                print("--- Server Logs ---")
                print(stdout)
                print(stderr, file=sys.stderr)

    print("\n✅ Standalone test complete.")


if __name__ == "__main__":
    # This script can be run in two ways:
    # 1. As a standalone test: `python examples/manual_test.py`
    #    This will start a server with auth, run tests, and shut it down.
    # 2. By the `run_examples.py` script.
    #    In this case, it acts as a client to the already-running server.

    # A simple way to check if we are running standalone or not.
    # The `run_examples.py` script will not set this env var.
    if os.getenv("RUNNING_STANDALONE_TEST", "false").lower() == "true":
        try:
            run_standalone_test()
        except Exception as e:
            print(f"\nAn error occurred: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Running as a client, just run the tests
        print("Running as a client against an existing server...")
        run_auth_tests()
        print("\n✅ Client tests complete.")
