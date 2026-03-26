import time

import requests

from dependencies.modules.base import BaseModule


class Module(BaseModule):
    name = "Miscellaneous"
    description = (
        "Check for miscellaneous misconfigurations and information disclosures"
    )
    severity = "low"

    CHECKS: dict[str, tuple[str, callable]] = {
        # Robots / sitemap (not vulns, but reveal hidden paths)
        "/robots.txt": (
            "Robots.txt file",
            lambda r: "disallow" in r.text.lower() or "allow" in r.text.lower(),
        ),
        "/sitemap.xml": ("Sitemap file", lambda r: "<url>" in r.text.lower()),
        "/sitemap_index.xml": (
            "Sitemap index file",
            lambda r: "<sitemap>" in r.text.lower(),
        ),
        # Security policy
        "/security.txt": ("Security.txt file", lambda r: "contact:" in r.text.lower()),
        "/.well-known/security.txt": (
            "Security.txt file",
            lambda r: "contact:" in r.text.lower(),
        ),
        # Cross-domain policies
        "/crossdomain.xml": (
            "Cross-domain policy",
            lambda r: "<cross-domain-policy>" in r.text.lower(),
        ),
        "/clientaccesspolicy.xml": (
            "Client access policy",
            lambda r: "<access-policy>" in r.text.lower(),
        ),
        # Server status / info pages
        "/server-status": (
            "Apache server status page",
            lambda r: "apache" in r.text.lower() and "server" in r.text.lower(),
        ),
        "/server-info": (
            "Apache server info page",
            lambda r: "apache" in r.text.lower(),
        ),
        "/nginx_status": (
            "Nginx status page",
            lambda r: "active connections" in r.text.lower(),
        ),
        "/stub_status": (
            "Nginx stub status page",
            lambda r: "active connections" in r.text.lower(),
        ),
        # Changelog / readme (reveal version info)
        "/CHANGELOG.md": ("Changelog file", lambda r: len(r.text) > 0),
        "/CHANGELOG.txt": ("Changelog file", lambda r: len(r.text) > 0),
        "/CHANGELOG": ("Changelog file", lambda r: len(r.text) > 0),
        "/README.md": ("Readme file", lambda r: len(r.text) > 0),
        "/README.txt": ("Readme file", lambda r: len(r.text) > 0),
        "/README": ("Readme file", lambda r: len(r.text) > 0),
        "/VERSION": ("Version file", lambda r: len(r.text.strip()) > 0),
        "/version.txt": ("Version file", lambda r: len(r.text.strip()) > 0),
        # License (reveals software in use)
        "/LICENSE": ("License file", lambda r: "license" in r.text.lower()),
        "/LICENSE.txt": ("License file", lambda r: "license" in r.text.lower()),
        "/LICENSE.md": ("License file", lambda r: "license" in r.text.lower()),
        # Exposed API specs (reveal endpoints)
        "/swagger.json": ("Swagger API spec", lambda r: "swagger" in r.text.lower()),
        "/swagger.yaml": ("Swagger API spec", lambda r: "swagger" in r.text.lower()),
        "/openapi.json": ("OpenAPI spec", lambda r: "openapi" in r.text.lower()),
        "/openapi.yaml": ("OpenAPI spec", lambda r: "openapi" in r.text.lower()),
        "/api-docs": (
            "API documentation",
            lambda r: "swagger" in r.text.lower() or "api" in r.text.lower(),
        ),
        "/api/swagger.json": (
            "Swagger API spec",
            lambda r: "swagger" in r.text.lower(),
        ),
        "/v1/swagger.json": (
            "Swagger API spec (v1)",
            lambda r: "swagger" in r.text.lower(),
        ),
        "/v2/swagger.json": (
            "Swagger API spec (v2)",
            lambda r: "swagger" in r.text.lower(),
        ),
        # Monitoring / metrics
        "/metrics": (
            "Prometheus metrics endpoint",
            lambda r: "# help" in r.text.lower() or "# type" in r.text.lower(),
        ),
        "/actuator": ("Spring Boot actuator", lambda r: "_links" in r.text),
        "/actuator/health": (
            "Spring Boot health endpoint",
            lambda r: "status" in r.text.lower(),
        ),
        "/actuator/env": (
            "Spring Boot env endpoint",
            lambda r: "propertySources" in r.text,
        ),
        "/actuator/mappings": (
            "Spring Boot mappings endpoint",
            lambda r: "dispatcherServlet" in r.text,
        ),
        "/health": (
            "Health check endpoint",
            lambda r: "status" in r.text.lower() or "ok" in r.text.lower(),
        ),
    }

    def _run(self) -> bool:
        for path, (label, validate) in self.CHECKS.items():
            url = f"{self.target.url}{path}"
            try:
                r = requests.get(url, timeout=5, allow_redirects=False)
                if r.status_code == 200 and validate(r):
                    self.findings.append(f"{label} found at {url}")
                time.sleep(0.05)
            except requests.RequestException:
                pass
        return len(self.findings) > 0
