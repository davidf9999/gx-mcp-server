#!/usr/bin/env python3
"""
verify_walkthrough.py  –  spin up gx-mcp-server, validate a demo CSV, print results.
"""

import asyncio
import csv
import json
import os
import subprocess
import sys
import time
import requests
import threading
from fastmcp import Client

URL = "http://localhost:8000/mcp/"
CSV_PATH = "customers.csv"
SERVER_CMD = [sys.executable, "-m", "gx_mcp_server", "--http"]
PROC = None


def stream_reader(stream, label):
    for line in iter(stream.readline, b''):
        print(f"[{label}] {line.decode().strip()}")
    stream.close()

# ── helpers ─────────────────────────────────────────────────────────────
def start_server():
    global PROC
    PROC = subprocess.Popen(SERVER_CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout_thread = threading.Thread(target=stream_reader, args=(PROC.stdout, "STDOUT"))
    stderr_thread = threading.Thread(target=stream_reader, args=(PROC.stderr, "STDERR"))
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()

    for _ in range(15):
        try:
            if requests.get(URL + "health").status_code == 200:
                return
        except requests.ConnectionError:
            time.sleep(1)
    raise RuntimeError("gx-mcp-server did not start in time")


def stop_server():
    if PROC and PROC.poll() is None:
        PROC.terminate()
        PROC.wait()


def generate_csv(path):
    rows = [
        ["id", "name", "email", "age", "purchase_amount"],
        [1, "Alice", "alice@example.com", 30, 120.50],
        [2, "Bob", "bob@example.com", 25, 75.00],
        [3, "Charlie", "charlie@example.com", "", 50.25],  # missing age
        [4, "Dana", "dana@example.com", 40, 200.00],
    ]
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(rows)


async def main():
    start_server()
    try:
        if not os.path.exists(CSV_PATH):
            generate_csv(CSV_PATH)

        async with Client(URL) as client:
            # 1 · load_dataset
            with open(CSV_PATH, "r") as f:
                csv_content = f.read()
            res = await client.call_tool("load_dataset", {"source_type": "inline", "source": csv_content})
            handle = res.structured_content["result"]["handle"]

            # 2 · create basic suite
            await client.call_tool(
                "create_suite",
                {
                    "dataset_handle": handle,
                    "suite_name": "customer_suite",
                    "profiler": True,
                },
            )

            # 3 · add simple expectation
            await client.call_tool(
                "add_expectation",
                {
                    "suite_name": "customer_suite",
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "id"},
                },
            )

            # 4 · run checkpoint
            chk = await client.call_tool(
                "run_checkpoint", {"dataset_handle": handle, "suite_name": "customer_suite"}
            )

            # 5 · fetch results
            result = await client.call_tool("get_validation_result", {"validation_id": chk.structured_content["validation_id"]})
            print(json.dumps(result.structured_content, indent=2))

    finally:
        stop_server()


# ── main ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(main())