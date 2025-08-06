#!/usr/bin/env python3
"""
Simple GX MCP Server using mcp.server.fastmcp (like calculator)
"""

import pandas as pd
from io import StringIO
from mcp.server.fastmcp import FastMCP

# Create the MCP server instance
mcp = FastMCP("gx-mcp-simple")


@mcp.tool()
async def load_dataset(csv_data: str) -> str:
    """
    Load and analyze a CSV dataset.

    Args:
        csv_data: CSV data as a string

    Returns:
        Dataset information and first 5 rows
    """
    try:
        # Parse CSV data
        df = pd.read_csv(StringIO(csv_data))

        # Build result
        result = []
        result.append("✅ Dataset loaded successfully!")
        result.append(f"📊 Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        result.append(f"📋 Columns: {', '.join(df.columns.tolist())}")
        result.append("\n🔍 First 5 rows:")
        result.append(df.head().to_string(index=False))

        return "\n".join(result)

    except Exception as e:
        return f"❌ Error loading dataset: {str(e)}"


def main():
    """Entry point for the server."""
    mcp.run()


if __name__ == "__main__":
    main()
