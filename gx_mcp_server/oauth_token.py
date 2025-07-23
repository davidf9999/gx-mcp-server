"""OAuth token endpoint for testing purposes."""

import json
import time

from starlette.requests import Request
from starlette.responses import JSONResponse


# Default test credentials
DEFAULT_CLIENT_ID = "demo-client"
DEFAULT_CLIENT_SECRET = "demo-secret"


async def oauth_token_endpoint(request: Request) -> JSONResponse:
    """Handle OAuth 2.0 client credentials grant requests.
    
    This is a minimal implementation for testing purposes only.
    """
    if request.method != "POST":
        return JSONResponse(
            {"error": "invalid_request", "error_description": "Method not allowed"},
            status_code=405
        )
    
    try:
        # Parse form data
        form_data = await request.form()
        
        client_id = form_data.get("client_id")
        client_secret = form_data.get("client_secret")
        grant_type = form_data.get("grant_type")
        
        # Validate required parameters
        if not all([client_id, client_secret, grant_type]):
            return JSONResponse(
                {"error": "invalid_request", "error_description": "Missing required parameters"},
                status_code=400
            )
        
        # Only support client_credentials grant
        if grant_type != "client_credentials":
            return JSONResponse(
                {"error": "unsupported_grant_type", "error_description": "Only client_credentials grant is supported"},
                status_code=400
            )
        
        # Validate client credentials (simple check for testing)
        if client_id != DEFAULT_CLIENT_ID or client_secret != DEFAULT_CLIENT_SECRET:
            return JSONResponse(
                {"error": "invalid_client", "error_description": "Invalid client credentials"},
                status_code=401
            )
        
        # Generate a simple test token (not secure, for testing only)
        now = int(time.time())
        expires_in = 3600  # 1 hour
        
        # Create a minimal JWT-like token (just for testing)
        header = {"typ": "JWT", "alg": "none"}
        payload = {
            "iss": "local",
            "sub": client_id,
            "aud": "gx-mcp-server",
            "iat": now,
            "exp": now + expires_in,
            "client_id": client_id
        }
        
        # Simple base64 encoding (no signature for testing)
        import base64
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        token = f"{header_b64}.{payload_b64}."
        
        return JSONResponse({
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "scope": "read write"
        })
        
    except Exception as e:
        return JSONResponse(
            {"error": "server_error", "error_description": f"Internal server error: {str(e)}"},
            status_code=500
        )