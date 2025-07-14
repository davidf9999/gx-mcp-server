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

MCP = Client("http://localhost:8000/mcp")


async def main() -> None:
    print("Starting AI-driven MCP example...")
    print("Make sure the server is running: python -m gx_mcp_server --http")
    await asyncio.sleep(1)  # Give the server some time to start
    
    async with MCP:
        # 1) Load a small dataset
        df = pd.DataFrame({"age": [25, 32, 47, 51], "salary": [50000, 64000, 120000, 95000]})
        csv = df.to_csv(index=False)
        load_res = await MCP.call_tool("load_dataset", {"source": csv, "source_type": "inline"})
        if not load_res.structured_content or "handle" not in load_res.structured_content:
            print("❌ Error loading dataset:", load_res.structured_content)
            return
        dataset_handle = load_res.structured_content["handle"]

        # 2) Create an expectation suite
        suite_res = await MCP.call_tool(
            "create_suite", {"suite_name": "ai_suite", "dataset_handle": dataset_handle, "profiler": False}
        )
        if not suite_res.structured_content or "suite_name" not in suite_res.structured_content:
            print("❌ Error creating suite:", suite_res.structured_content)
            return
        suite_name = suite_res.structured_content["suite_name"]

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
            content = resp.choices[0].message.content
            if content:
                tool_args = json.loads(content)
            else:
                raise ValueError("No content in OpenAI response")
            print("AI proposed expectation:", tool_args)
        except Exception as e:
            print(f"AI request failed: {e}")
            print("Using fallback expectation for demo purposes...")
            tool_args = {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "age", "min_value": 0, "max_value": 100}
            }
            print("Fallback expectation:", tool_args)

        # 4) Add the expectation
        add_res = await MCP.call_tool(
            "add_expectation",
            {
                "suite_name": suite_name,
                "expectation_type": tool_args["expectation_type"],
                "kwargs": tool_args["kwargs"],
            }
        )
        if not add_res.structured_content or not add_res.structured_content.get("success", False):
            print("❌ Error adding expectation:", add_res.structured_content)
            return

        # 5) Run validation and fetch results
        val_res = await MCP.call_tool(
            "run_checkpoint", {"suite_name": suite_name, "dataset_handle": dataset_handle}
        )
        if not val_res.structured_content or "validation_id" not in val_res.structured_content:
            print("❌ Error running validation:", val_res.structured_content)
            return
        validation_id = val_res.structured_content["validation_id"]

        detail = await MCP.call_tool("get_validation_result", {"validation_id": validation_id})
        if not detail.structured_content:
            print("❌ Error fetching validation result:", detail.structured_content)
            return
        print("Validation summary:", json.dumps(detail.structured_content, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
