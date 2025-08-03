"""
Custom Bearer Auth provider for FastMCP.
"""

import time
from typing import Any

import httpx
from authlib.jose import JsonWebToken, jwk
from authlib.jose.errors import JoseError
from fastmcp.server.auth.auth import (
    ClientRegistrationOptions,
    OAuthProvider,
    RevocationOptions,
)
from fastmcp.utilities.logging import get_logger
from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    OAuthToken,
    RefreshToken,
)
from mcp.shared.auth import OAuthClientInformationFull
from pydantic import AnyHttpUrl, ValidationError


class BearerAuthProvider(OAuthProvider):
    """
    Custom Bearer Token validator that supports both signed and unsigned JWT tokens.
    """

    def __init__(
        self,
        public_key: str | None = None,
        jwks_uri: str | None = None,
        issuer: str | None = None,
        audience: str | list[str] | None = None,
        required_scopes: list[str] | None = None,
    ):
        """
        Initialize the provider.

        Args:
            public_key: RSA public key for signed tokens.
            jwks_uri: JWKS URI for signed tokens.
            issuer: Expected issuer claim.
            audience: Expected audience claim.
            required_scopes: List of required scopes.
        """
        try:
            issuer_url = AnyHttpUrl(issuer) if issuer else "https://fastmcp.example.com"
        except ValidationError:
            issuer_url = "https://fastmcp.example.com"

        super().__init__(
            issuer_url=issuer_url,
            client_registration_options=ClientRegistrationOptions(enabled=False),
            revocation_options=RevocationOptions(enabled=False),
            required_scopes=required_scopes,
        )

        self.public_key = public_key
        self.jwks_uri = jwks_uri
        self.issuer = issuer
        self.audience = audience
        self.jwt = JsonWebToken(["RS256", "none"])
        self.logger = get_logger(__name__)
        self._jwks_cache: dict[str, Any] = {}
        self._jwks_cache_time: float = 0

    async def _get_jwks(self) -> Any:
        """Fetch JWKS from URI with a 5-minute cache."""
        if self.jwks_uri and (
            not self._jwks_cache or time.time() - self._jwks_cache_time > 300
        ):
            async with httpx.AsyncClient() as client:
                try:
                    resp = await client.get(self.jwks_uri)
                    resp.raise_for_status()
                    self._jwks_cache = resp.json()
                    self._jwks_cache_time = time.time()
                    self.logger.info("Fetched and cached JWKS from %s", self.jwks_uri)
                except httpx.HTTPError as e:
                    self.logger.error("Failed to fetch JWKS: %s", e)
                    # Return stale cache if available
                    return self._jwks_cache or {}
        return self._jwks_cache

    async def load_access_token(self, token: str) -> AccessToken | None:
        """
        Validates the provided JWT bearer token.
        """
        try:
            key = self.public_key or ""
            if self.jwks_uri:
                jwks = await self._get_jwks()
                key = jwk.loads(jwks)

            claims = self.jwt.decode(token, key=key)
            client_id = claims.get("client_id") or claims.get("sub") or "unknown"

            exp = claims.get("exp")
            if exp and exp < time.time():
                self.logger.debug(
                    "Token validation failed: expired token for client %s", client_id
                )
                self.logger.info("Bearer token rejected for client %s", client_id)
                return None

            if self.issuer:
                if claims.get("iss") != self.issuer:
                    self.logger.debug(
                        "Token validation failed: issuer mismatch for client %s (expected %s, got %s)",
                        client_id,
                        self.issuer,
                        claims.get("iss"),
                    )
                    self.logger.info("Bearer token rejected for client %s", client_id)
                    return None

            if self.audience:
                aud = claims.get("aud")
                audience_valid = False

                if isinstance(self.audience, list):
                    if isinstance(aud, list):
                        audience_valid = any(
                            expected in aud for expected in self.audience
                        )
                    else:
                        audience_valid = aud in self.audience
                else:
                    if isinstance(aud, list):
                        audience_valid = self.audience in aud
                    else:
                        audience_valid = aud == self.audience

                if not audience_valid:
                    self.logger.debug(
                        "Token validation failed: audience mismatch for client %s (expected %s, got %s)",
                        client_id,
                        self.audience,
                        aud,
                    )
                    self.logger.info("Bearer token rejected for client %s", client_id)
                    return None

            scopes = self._extract_scopes(claims)

            self.logger.info("Bearer token accepted for client %s", client_id)
            return AccessToken(
                token=token,
                client_id=str(client_id),
                scopes=scopes,
                expires_at=int(exp) if exp else None,
            )

        except JoseError as e:
            self.logger.debug("Token validation failed: JWT format invalid: %s", str(e))
            return None
        except Exception as e:
            self.logger.debug("Token validation failed: %s", str(e))
            return None

    def _extract_scopes(self, claims: dict[str, Any]) -> list[str]:
        """Extract scopes from JWT claims."""
        for claim in ["scope", "scp"]:
            if claim in claims:
                if isinstance(claims[claim], str):
                    return claims[claim].split()
                elif isinstance(claims[claim], list):
                    return claims[claim]
        return []

    async def verify_token(self, token: str) -> AccessToken | None:
        """Verify a bearer token and return access info if valid."""
        return await self.load_access_token(token)

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        raise NotImplementedError("Client management not supported")

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        raise NotImplementedError("Client registration not supported")

    async def authorize(
        self, client: OAuthClientInformationFull, params: Any
    ) -> str:
        raise NotImplementedError("Authorization flow not supported")

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        raise NotImplementedError("Authorization code exchange not supported")

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        raise NotImplementedError("Token revocation not supported")

    async def exchange_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: RefreshToken, scopes: list[str]
    ) -> OAuthToken:
        raise NotImplementedError("Refresh token exchange not supported")

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, code: str
    ) -> AuthorizationCode | None:
        raise NotImplementedError("Authorization code loading not supported")

    async def load_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: str
    ) -> RefreshToken | None:
        raise NotImplementedError("Refresh token loading not supported")
