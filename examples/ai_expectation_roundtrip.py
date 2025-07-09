#!/usr/bin/env python3
import json
import os

import openai
import pandas as pd
from fastmcp import Client

# ── Configuration ──────────────────────────────────────────────────────────────
# Replace with your OpenAI API key, or set env var OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-...")

MCP = Client("http://localhost:8000")  # your running MCP server

# ── 1) Load a small dataset ────────────────────────────────────────────────────
df = pd.DataFrame({"age": [25, 32, 47, 51], "salary": [50000, 64000, 120000, 95000]})
csv = df.to_csv(index=False)
load_res = MCP.load_dataset(source=csv, source_type="inline")
print("Loaded dataset handle:", load_res.handle)

# ── 2) Create an expectation suite ─────────────────────────────────────────────
suite_res = MCP.create_suite(
    suite_name="ai_suite", dataset_handle=load_res.handle, profiler=False
)
print("Created suite:", suite_res.suite_name)

# ── 3) Ask the AI for an expectation ───────────────────────────────────────────
prompt = f"""
I have a CSV dataset with columns: {list(df.columns)}.
Please choose one column and propose a Great Expectations expectation
to validate that column.  Respond *only* with a JSON object 
with keys "expectation_type" and "kwargs".  For example:
{{"expectation_type":"expect_column_values_to_be_between","kwargs":{{"column":"age","min_value":0,"max_value":100}}}}
"""
resp = openai.ChatCompletion.create(
    model="gpt-4", messages=[{"role": "user", "content": prompt}]
)
# The model should answer e.g.:
# {"expectation_type":"expect_column_values_to_be_between","kwargs":{"column":"age","min_value":0,"max_value":120}}
tool_args = json.loads(resp.choices[0].message.content)
print("AI proposed expectation:", tool_args)

# ── 4) Invoke the MCP tool ────────────────────────────────────────────────────
add_res = MCP.add_expectation(
    suite_name=suite_res.suite_name,
    expectation_type=tool_args["expectation_type"],
    kwargs=tool_args["kwargs"],
)
print("Add expectation succeeded:", add_res.success)

# ── 5) Run validation and fetch results ────────────────────────────────────────
val_res = MCP.run_checkpoint(
    suite_name=suite_res.suite_name, dataset_handle=load_res.handle
)
print("Validation ID:", val_res.validation_id)
detail = MCP.get_validation_result(validation_id=val_res.validation_id)
print("Validation summary:", json.dumps(detail, indent=2))
