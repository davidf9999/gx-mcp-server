#!/usr/bin/env bash
set -euo pipefail

echo "🚦 Launching STDIO smoke‑test…"

# Test STDIO MCP server functionality
echo "Testing STDIO MCP server..."

# Create test MCP initialization message
init_msg='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"roots":{"listChanged":true},"sampling":{}},"clientInfo":{"name":"smoke-test","version":"1.0"}}}'

# Test that the server can initialize via STDIO
echo "🔌 Testing MCP initialization..."
response=$(echo "$init_msg" | timeout 10 docker run --rm -i gx-mcp-server:prod-test)

if echo "$response" | grep -q '"result"'; then
    echo "✅ MCP initialization successful"
else
    echo "❌ MCP initialization failed"
    echo "Response: $response"
    exit 1
fi

# Test that the server reports correct capabilities
if echo "$response" | grep -q '"serverInfo"'; then
    echo "✅ Server info present"
else
    echo "❌ Server info missing"
    exit 1
fi

echo "✅ STDIO smoke‑test passed!"
echo "🚀 Ready for Smithery deployment"