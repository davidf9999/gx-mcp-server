#!/usr/bin/env python3
import asyncio
import json
import os

import openai
import pandas as pd
from fastmcp import Client

# ── Configuration ──────────────────────────────────────────────────────────────
# Replace with your OpenAI API key, or set env var OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-...")

MCP = Client("http://localhost:8000/mcp")  # your running MCP server


async def main() -> None:
    print("Starting AI-driven MCP example...")
    print("Make sure the server is running: python -m gx_mcp_server --http")
    await asyncio.sleep(1)  # Give the server some time to start
    
    async with MCP:
        # ── 1) Load a small dataset ────────────────────────────────────────────────────
        df = pd.DataFrame({"age": [25, 32, 47, 51], "salary": [50000, 64000, 120000, 95000]})
        csv = df.to_csv(index=False)
        load_res = await MCP.call_tool("load_dataset", {"source": csv, "source_type": "inline"})
        dataset_handle = load_res.structured_content["handle"]
        print("Loaded dataset handle:", dataset_handle)

        # ── 2) Create an expectation suite ─────────────────────────────────────────────
        suite_res = await MCP.call_tool(
            "create_suite", {"suite_name": "ai_suite", "dataset_handle": dataset_handle, "profiler": False}
        )
        suite_name = suite_res.structured_content["suite_name"]
        print("Created suite:", suite_name)

        # ── 3) Ask the AI for an expectation ───────────────────────────────────────────
        prompt = f"""
I have a CSV dataset with columns: {list(df.columns)}.
Please choose one column and propose a Great Expectations expectation
to validate that column.  Respond *only* with a JSON object 
with keys "expectation_type" and "kwargs".  For example:
{{"expectation_type":"expect_column_values_to_be_between","kwargs":{{"column":"age","min_value":0,"max_value":100}}}}
"""
        try:
            # Use the new OpenAI client API
            client = openai.OpenAI()
            resp = client.chat.completions.create(
                model="gpt-4", 
                messages=[{"role": "user", "content": prompt}]
            )
            # The model should answer e.g.:
            # {"expectation_type":"expect_column_values_to_be_between","kwargs":{"column":"age","min_value":0,"max_value":120}}
            tool_args = json.loads(resp.choices[0].message.content)
            print("AI proposed expectation:", tool_args)
        except Exception as e:
            print(f"AI request failed: {e}")
            print("Using fallback expectation for demo purposes...")
            tool_args = {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "age", "min_value": 0, "max_value": 100}
            }
            print("Fallback expectation:", tool_args)

        # ── 4) Invoke the MCP tool ────────────────────────────────────────────────────
        add_res = await MCP.call_tool(
            "add_expectation",
            {
                "suite_name": suite_name,
                "expectation_type": tool_args["expectation_type"],
                "kwargs": tool_args["kwargs"],
            }
        )
        print("Add expectation succeeded:", add_res.structured_content["success"])

        # ── 5) Run validation and fetch results ────────────────────────────────────────
        val_res = await MCP.call_tool(
            "run_checkpoint", {"suite_name": suite_name, "dataset_handle": dataset_handle}
        )
        validation_id = val_res.structured_content["validation_id"]
        print("Validation ID:", validation_id)
        
        detail = await MCP.call_tool("get_validation_result", {"validation_id": validation_id})
        print("Validation summary:", json.dumps(detail.structured_content, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
