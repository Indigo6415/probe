import time

import requests

from dependencies.modules.base import BaseModule


class Module(BaseModule):
    name = "API Endpoints"
    description = "Check if sensitive API endpoints are publicly accessible"
    severity = "high"

    CHECKS: dict[str, tuple[str, callable]] = {
        # GraphQL
        "/graphql": (
            "GraphQL endpoint",
            lambda r: "data" in r.text.lower() or "errors" in r.text.lower(),
        ),
        "/graphiql": ("GraphiQL interface", lambda r: "graphiql" in r.text.lower()),
        "/playground": ("GraphQL playground", lambda r: "playground" in r.text.lower()),
        "/api/graphql": (
            "GraphQL endpoint",
            lambda r: "data" in r.text.lower() or "errors" in r.text.lower(),
        ),
        # REST - generic
        "/api": ("API root", lambda r: "{" in r.text or "[" in r.text),
        "/api/v1": ("API v1 root", lambda r: "{" in r.text or "[" in r.text),
        "/api/v2": ("API v2 root", lambda r: "{" in r.text or "[" in r.text),
        "/api/v3": ("API v3 root", lambda r: "{" in r.text or "[" in r.text),
        "/rest": ("REST API root", lambda r: "{" in r.text or "[" in r.text),
        "/rest/v1": ("REST API v1 root", lambda r: "{" in r.text or "[" in r.text),
        # Sensitive REST endpoints
        "/api/v1/users": (
            "User list endpoint",
            lambda r: "{" in r.text or "[" in r.text,
        ),
        "/api/v1/admin": (
            "Admin API endpoint",
            lambda r: "{" in r.text or "[" in r.text,
        ),
        "/api/v1/config": (
            "Config API endpoint",
            lambda r: "{" in r.text or "[" in r.text,
        ),
        "/api/v1/keys": ("API keys endpoint", lambda r: "{" in r.text or "[" in r.text),
        "/api/v1/secrets": (
            "Secrets endpoint",
            lambda r: "{" in r.text or "[" in r.text,
        ),
        "/api/v1/tokens": ("Tokens endpoint", lambda r: "{" in r.text or "[" in r.text),
        "/api/v1/credentials": (
            "Credentials endpoint",
            lambda r: "{" in r.text or "[" in r.text,
        ),
        "/api/v1/logs": ("Logs endpoint", lambda r: "{" in r.text or "[" in r.text),
        "/api/v1/debug": ("Debug endpoint", lambda r: "{" in r.text or "[" in r.text),
        "/api/v2/users": (
            "User list endpoint",
            lambda r: "{" in r.text or "[" in r.text,
        ),
        "/api/v2/admin": (
            "Admin API endpoint",
            lambda r: "{" in r.text or "[" in r.text,
        ),
        # Debug / trace
        "/api/debug": ("API debug endpoint", lambda r: "{" in r.text or "[" in r.text),
        "/api/test": ("API test endpoint", lambda r: "{" in r.text or "[" in r.text),
        "/api/health": (
            "API health endpoint",
            lambda r: "status" in r.text.lower() or "ok" in r.text.lower(),
        ),
        "/api/status": (
            "API status endpoint",
            lambda r: "status" in r.text.lower() or "ok" in r.text.lower(),
        ),
        "/api/info": ("API info endpoint", lambda r: "{" in r.text or "[" in r.text),
        "/api/version": (
            "API version endpoint",
            lambda r: "{" in r.text or "[" in r.text,
        ),
        "/api/env": (
            "API environment endpoint",
            lambda r: "{" in r.text or "[" in r.text,
        ),
        "/api/config": (
            "API config endpoint",
            lambda r: "{" in r.text or "[" in r.text,
        ),
        # Laravel / Symfony / common frameworks
        "/api/user": ("User endpoint", lambda r: "{" in r.text or "[" in r.text),
        "/api/me": ("Current user endpoint", lambda r: "{" in r.text or "[" in r.text),
        "/api/profile": ("Profile endpoint", lambda r: "{" in r.text or "[" in r.text),
        # JSON-RPC
        "/rpc": ("JSON-RPC endpoint", lambda r: "jsonrpc" in r.text.lower()),
        "/jsonrpc": ("JSON-RPC endpoint", lambda r: "jsonrpc" in r.text.lower()),
        "/api/rpc": ("JSON-RPC endpoint", lambda r: "jsonrpc" in r.text.lower()),
    }

    def _probe_graphql(self, url: str) -> bool:
        """Send an introspection query to check if GraphQL is exposed and introspection is enabled."""
        query = '{"query": "{__schema { queryType { name } } }"}'
        try:
            r = requests.post(
                url, data=query, headers={"Content-Type": "application/json"}, timeout=5
            )
            if r.status_code == 200 and "__schema" in r.text:
                self.findings.append(f"GraphQL introspection enabled at {url}")
                return True
        except requests.RequestException:
            pass
        return False

    def _run(self) -> bool:
        for path, (label, validate) in self.CHECKS.items():
            url = f"{self.target.url}{path}"
            try:
                r = requests.get(url, timeout=5, allow_redirects=False)
                if r.status_code == 200 and validate(r):
                    self.findings.append(f"{label} accessible at {url}")
                time.sleep(0.05)
            except requests.RequestException:
                pass

        # Separately probe GraphQL endpoints for introspection
        for path in ("/graphql", "/api/graphql", "/graphiql"):
            self._probe_graphql(f"{self.target.url}{path}")

        return len(self.findings) > 0
