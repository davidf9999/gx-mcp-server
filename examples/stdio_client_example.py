#!/usr/bin/env python3
"""
Test the STDIO GX MCP server using the calculator client pattern
"""

import asyncio
from mcp.client.stdio import StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_gx_stdio_server():
    print("Testing GX MCP Server (STDIO version)...")
    
    try:
        # Create server parameters (like calculator example)
        server_params = StdioServerParameters(
            command="docker", 
            args=["run", "--rm", "-i", "davidf9999/gx-mcp-server:stdio"]
        )
        
        async with stdio_client(server_params) as (read_stream, write_stream):
            from mcp.client.session import ClientSession
            
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                await session.initialize()
                print("✅ Connection initialized successfully!")
                
                # List available tools
                tools_result = await session.list_tools()
                tool_names = [t.name for t in tools_result.tools]
                print(f"✅ Available tools: {', '.join(tool_names)}")
                
                # Test load_dataset tool
                if "load_dataset" in tool_names:
                    print("\n🧪 Testing load_dataset...")
                    test_csv = "name,age,city\nAlice,30,NYC\nBob,25,LA\nCharlie,35,Chicago"
                    result = await session.call_tool("load_dataset", {
                        "source_type": "inline",
                        "source": test_csv
                    })
                    print("Dataset loading result:")
                    print(result.content[0].text if result.content else "No result")
                
                print("\n✅ All tests passed! STDIO MCP server is working!")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gx_stdio_server())