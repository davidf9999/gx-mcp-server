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
SERVER_START_CMD = ["uv", "run", "python", "-m", "gx_mcp_server", "--http"]
EXAMPLE_PATTERN = "examples/*.py"
# Max time to wait for the server to start up
SERVER_STARTUP_TIMEOUT = 20  # seconds


def is_server_running(verbose: bool = True) -> bool:
    """Checks if the MCP server is responding."""
    if verbose:
        print(f"Checking for server at {MCP_URL}...")
    try:
        # A GET request to the base MCP URL should not raise a ConnectionError.
        response = requests.get(MCP_URL, timeout=1)
        # Any response (even 405 Method Not Allowed) means the server is up.
        if verbose:
            print(f"--> Server check successful with status code: {response.status_code}")
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
    """Starts the MCP server in a background process and waits for it to be ready."""
    print(f"Starting server with command: {' '.join(SERVER_START_CMD)}")
    # Use Popen for non-blocking execution.
    # Redirect stdout/stderr to DEVNULL to keep the runner script's output clean.
    try:
        proc = subprocess.Popen(
            SERVER_START_CMD,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print(f"❌ Error: Command '{SERVER_START_CMD[0]}' not found. Is 'uv' installed and in your PATH?")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: Failed to start server process: {e}")
        sys.exit(1)

    print(f"Server process started with PID: {proc.pid}. Waiting for it to become available...")

    start_time = monotonic()
    while monotonic() - start_time < SERVER_STARTUP_TIMEOUT:
        if is_server_running(verbose=False):
            print("--> Server is up and running.")
            return proc
        time.sleep(0.5)

    print(f"❌ Error: Server did not become available within {SERVER_STARTUP_TIMEOUT} seconds.")
    stop_server(proc)
    sys.exit(1)


def stop_server(proc: subprocess.Popen):
    """Stops the given server process."""
    print(f"Stopping server process with PID: {proc.pid}...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
        print("--> Server process stopped successfully.")
    except subprocess.TimeoutExpired:
        print("--> Server process did not terminate gracefully, killing it.")
        proc.kill()


def run_examples():
    """Finds and runs all example scripts."""
    example_files = sorted(glob.glob(EXAMPLE_PATTERN))
    if not example_files:
        print(f"No examples found matching pattern: {EXAMPLE_PATTERN}")
        return

    print(f"\nFound {len(example_files)} examples to run: {', '.join(example_files)}")
    print("-" * 50)

    for example_file in example_files:
        print(f"▶️  Running example: {example_file}...")
        # The AI example needs an API key. Provide a dummy one if not set
        # to prevent failure, as the script has a fallback.
        env = os.environ.copy()
        if "ai_expectation" in example_file and "OPENAI_API_KEY" not in env:
            env["OPENAI_API_KEY"] = "sk-dummy-for-testing"

        result = subprocess.run(["uv", "run", "python", example_file], capture_output=True, text=True, env=env)

        if result.returncode == 0:
            print(f"✅ SUCCESS: {example_file}\n")
        else:
            print(f"❌ FAILED: {example_file}")
            print("--- STDOUT ---\n" + result.stdout)
            print("--- STDERR ---\n" + result.stderr)
            # Stop on first failure
            raise RuntimeError(f"Example {example_file} failed.")


def main():
    """Main script logic."""
    # Load environment variables from .env file if it exists
    load_dotenv()

    server_proc: Optional[subprocess.Popen] = None
    we_started_server = False

    if not is_server_running(verbose=True):
        we_started_server = True
        server_proc = start_server()

    try:
        run_examples()
    finally:
        if we_started_server and server_proc:
            stop_server(server_proc)


if __name__ == "__main__":
    main()
