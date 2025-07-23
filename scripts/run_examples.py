#!/usr/bin/env python3
import glob
import os
import subprocess
import sys
import time
from typing import Optional

import requests
from requests.exceptions import ConnectionError
from dotenv import load_dotenv
from time import monotonic

# --- Configuration ---
HOST = "localhost"
PORT = 8000
MCP_URL = f"http://{HOST}:{PORT}/mcp/"
# vanilla server (no auth) so basic examples just work
SERVER_START_CMD = ["uv", "run", "python", "-m", "gx_mcp_server", "--http"]
EXAMPLE_PATTERN = "examples/*.py"

# the consolidated security test file:
SECURITY_SCRIPTS = {"examples/security_checks.py"}

# Max time to wait for the server to start up
SERVER_STARTUP_TIMEOUT = 20  # seconds


def is_server_running(verbose: bool = True) -> bool:
    if verbose:
        print(f"Checking for server at {MCP_URL}...")
    try:
        resp = requests.get(MCP_URL, timeout=1)
        if verbose:
            print(f"--> Server check successful with status code: {resp.status_code}")
        return True
    except ConnectionError:
        if verbose:
            print("--> Server check failed: Connection refused.")
        return False
    except Exception as e:
        if verbose:
            print(f"--> Server check failed with an unexpected error: {e}")
        return False


def start_server() -> subprocess.Popen:
    print(f"Starting server with command: {' '.join(SERVER_START_CMD)}")
    try:
        proc = subprocess.Popen(
            SERVER_START_CMD,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print(f"❌ Error: Command '{SERVER_START_CMD[0]}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: Failed to start server process: {e}")
        sys.exit(1)

    print(
        f"Server process started with PID: {proc.pid}. Waiting for it to become available..."
    )

    start_time = monotonic()
    while monotonic() - start_time < SERVER_STARTUP_TIMEOUT:
        if is_server_running(verbose=False):
            print("--> Server is up and running.")
            return proc
        time.sleep(0.5)

    print(
        f"❌ Error: Server did not become available within {SERVER_STARTUP_TIMEOUT} seconds."
    )
    stop_server(proc)
    sys.exit(1)


def stop_server(proc: subprocess.Popen):
    print(f"Stopping server process with PID: {proc.pid}...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
        print("--> Server process stopped successfully.")
    except subprocess.TimeoutExpired:
        print("--> Server process did not terminate gracefully, killing it.")
        proc.kill()


def run_file(path: str, extra_args=None, allow_fail=False):
    cmd = ["uv", "run", "python", path]
    if extra_args:
        cmd.extend(extra_args)

    print(f"▶️  Running: {' '.join(cmd)}")
    env = os.environ.copy()
    if "ai_expectation" in path and "OPENAI_API_KEY" not in env:
        env["OPENAI_API_KEY"] = "sk-dummy-for-testing"

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)

    if result.returncode == 0:
        print(f"✅ SUCCESS: {path}\n")
    else:
        print(f"❌ FAILED: {path}")
        print("--- STDOUT ---\n" + result.stdout)
        print("--- STDERR ---\n" + result.stderr)
        if not allow_fail:
            raise RuntimeError(f"{path} failed.")
        else:
            print("⚠️  Continuing despite failure (allow_fail=True).")


def main():
    load_dotenv()

    example_files = sorted(glob.glob(EXAMPLE_PATTERN))
    if not example_files:
        print(f"No examples found matching pattern: {EXAMPLE_PATTERN}")
        return

    # Separate security script(s)
    sec_files = [p for p in example_files if p in SECURITY_SCRIPTS]
    example_files = [p for p in example_files if p not in SECURITY_SCRIPTS]

    # Run normal examples first under vanilla server
    server_proc: Optional[subprocess.Popen] = None
    we_started_server = False

    if not is_server_running(verbose=True):
        we_started_server = True
        server_proc = start_server()

    try:
        # Prioritize simple example first
        basic_example = "examples/basic_roundtrip.py"
        if basic_example in example_files:
            example_files.remove(basic_example)
            example_files.insert(0, basic_example)

        print(
            f"\nFound {len(example_files)} non-security examples: {', '.join(example_files)}"
        )
        print("-" * 50)
        for f in example_files:
            run_file(f)

    finally:
        if we_started_server and server_proc:
            stop_server(server_proc)

    # Now run security checks (each script will manage its own secured server)
    if sec_files:
        print("\n=== Running security checks ===")
        for f in sec_files:
            # Let the script start its server. No need for allow_fail here—fail should break CI.
            run_file(f, extra_args=None, allow_fail=False)

    print("\nAll examples/tests completed.")


if __name__ == "__main__":
    main()
