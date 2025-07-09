#!/usr/bin/env python3
import json

from fastmcp import Client

# 1) Start the server: uvicorn gx_mcp_server.app:app --reload
MCP = Client("http://localhost:8000")

# 2) Load a tiny CSV inline
csv = "x,y\n1,2\n3,4\n5,6"
load_res = MCP.load_dataset(source=csv, source_type="inline")
print("Loaded dataset handle:", load_res.handle)

# 3) Create an expectation suite (no profiling)
suite_res = MCP.create_suite(
    suite_name="demo_suite", dataset_handle=load_res.handle, profiler=False
)
print("Created suite:", suite_res.suite_name)

# 4) Add an expectation
add_res = MCP.add_expectation(
    suite_name=suite_res.suite_name,
    expectation_type="expect_column_values_to_be_in_set",
    kwargs={"column": "x", "value_set": [1, 3, 5]},
)
print("Add expectation success:", add_res.success)

# 5) Run validation checkpoint
val_res = MCP.run_checkpoint(
    suite_name=suite_res.suite_name, dataset_handle=load_res.handle
)
print("Validation ID:", val_res.validation_id)

# 6) Fetch results
detail = MCP.get_validation_result(validation_id=val_res.validation_id)
print("Validation summary:", json.dumps(detail, indent=2))
