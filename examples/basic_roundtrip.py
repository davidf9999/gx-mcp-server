#!/usr/bin/env python3
import json

from fastmcp import Client

# 1) Start the server: python -m gx_mcp_server --http
MCP = Client("http://localhost:8000/mcp")


async def main() -> None:
    print("Starting MCP client example...")
    print("Make sure the server is running: python -m gx_mcp_server --http")
    await asyncio.sleep(1)  # Give the server some time to start
    async with MCP:
        # 2) Load a tiny CSV inline
        csv = "x,y\n1,2\n3,4\n5,6"
        load_res = await MCP.call_tool("load_dataset", {"source": csv, "source_type": "inline"})
        dataset_handle = load_res.structured_content["handle"]
        print("Loaded dataset handle:", dataset_handle)

        # 3) Create an expectation suite (no profiling)
        suite_res = await MCP.call_tool(
            "create_suite", {"suite_name": "demo_suite", "dataset_handle": dataset_handle, "profiler": False}
        )
        suite_name = suite_res.structured_content["suite_name"]
        print("Created suite:", suite_name)

        # 4) Add an expectation
        add_res = await MCP.call_tool(
            "add_expectation",
            {
                "suite_name": suite_name,
                "expectation_type": "expect_column_values_to_be_in_set",
                "kwargs": {"column": "x", "value_set": [1, 3, 5]},
            }
        )
        print("Add expectation success:", add_res.structured_content["success"])

        # 5) Run validation checkpoint
        val_res = await MCP.call_tool(
            "run_checkpoint", {"suite_name": suite_name, "dataset_handle": dataset_handle}
        )
        validation_id = val_res.structured_content["validation_id"]
        print("Validation ID:", validation_id)

        # 6) Fetch results
        detail = await MCP.call_tool("get_validation_result", {"validation_id": validation_id})
        print("Validation summary:", json.dumps(detail.structured_content, indent=2))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
