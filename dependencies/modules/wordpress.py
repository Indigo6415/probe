import time

import requests

from dependencies.modules.base import BaseModule


class Module(BaseModule):
    name = "WordPress"
    description = "Check for WordPress-specific misconfigurations and exposures"
    severity = "high"

    CHECKS: dict[str, tuple[str, callable]] = {
        # User enumeration
        "/wp-json/wp/v2/users": (
            "WordPress REST API user enumeration",
            lambda r: "[" in r.text and "slug" in r.text,
        ),
        "/?author=1": (
            "WordPress author enumeration",
            lambda r: "author" in r.url.lower(),
        ),
        # Exposed logs / debug
        "/wp-content/debug.log": (
            "WordPress debug log",
            lambda r: (
                "php" in r.text.lower()
                or "error" in r.text.lower()
                or "warning" in r.text.lower()
            ),
        ),
        "/wp-content/uploads/": (
            "WordPress uploads directory listing",
            lambda r: "index of" in r.text.lower(),
        ),
        # Config backups
        "/wp-config.php~": ("WordPress config backup", lambda r: "DB_" in r.text),
        "/wp-config.php.bak": ("WordPress config backup", lambda r: "DB_" in r.text),
        "/wp-config.php.old": ("WordPress config backup", lambda r: "DB_" in r.text),
        "/wp-config.php.save": ("WordPress config backup", lambda r: "DB_" in r.text),
        "/wp-config.bak": ("WordPress config backup", lambda r: "DB_" in r.text),
        # XML-RPC (can be abused for brute force / DDoS amplification)
        "/xmlrpc.php": (
            "WordPress XML-RPC enabled",
            lambda r: "xml" in r.text.lower() and "rpc" in r.text.lower(),
        ),
        # Readme / license (reveals exact WP version)
        "/readme.html": (
            "WordPress readme exposes version",
            lambda r: "wordpress" in r.text.lower(),
        ),
        "/license.txt": (
            "WordPress license file",
            lambda r: "wordpress" in r.text.lower(),
        ),
        # Install / upgrade pages
        "/wp-admin/install.php": (
            "WordPress install page accessible",
            lambda r: "installation" in r.text.lower() or "wordpress" in r.text.lower(),
        ),
        "/wp-admin/upgrade.php": (
            "WordPress upgrade page accessible",
            lambda r: "wordpress" in r.text.lower(),
        ),
        # Sensitive plugin / theme paths
        "/wp-content/plugins/": (
            "WordPress plugins directory listing",
            lambda r: "index of" in r.text.lower(),
        ),
        "/wp-content/themes/": (
            "WordPress themes directory listing",
            lambda r: "index of" in r.text.lower(),
        ),
    }

    def _is_wordpress(self) -> bool:
        """Quick check to see if the target is actually running WordPress."""
        try:
            r = requests.get(self.target.url, timeout=5)
            return (
                "wp-content" in r.text
                or "wp-json" in r.text
                or "wordpress" in r.text.lower()
                or "wordpress" in r.headers.get("x-powered-by", "").lower()
            )
        except requests.RequestException:
            return False

    def _check_debug_mode(self) -> None:
        """Check if WP_DEBUG is leaking PHP errors into the page source."""
        try:
            r = requests.get(self.target.url, timeout=5)
            if (
                "<b>Notice</b>" in r.text
                or "<b>Warning</b>" in r.text
                or "<b>Fatal error</b>" in r.text
            ):
                self.findings.append(
                    f"WP_DEBUG appears enabled — PHP errors exposed in page source at {self.target.url}"
                )
        except requests.RequestException:
            pass

    def _check_xmlrpc_pingback(self) -> None:
        """Check if XML-RPC pingback is enabled (can be abused for DDoS amplification)."""
        url = f"{self.target.url}/xmlrpc.php"
        payload = """<?xml version="1.0" encoding="utf-8"?>
<methodCall>
  <methodName>system.listMethods</methodName>
  <params></params>
</methodCall>"""
        try:
            r = requests.post(
                url, data=payload, headers={"Content-Type": "text/xml"}, timeout=5
            )
            if r.status_code == 200 and "pingback.ping" in r.text:
                self.findings.append(
                    f"XML-RPC pingback enabled at {url} — potential DDoS amplification vector"
                )
        except requests.RequestException:
            pass

    def _run(self) -> bool:
        if not self._is_wordpress():
            return False

        for path, (label, validate) in self.CHECKS.items():
            url = f"{self.target.url}{path}"
            try:
                r = requests.get(url, timeout=5, allow_redirects=True)
                if r.status_code == 200 and validate(r):
                    self.findings.append(f"{label} at {url}")
                time.sleep(self.delay)
            except requests.RequestException:
                time.sleep(self.delay)
                pass

        self._check_debug_mode()
        self._check_xmlrpc_pingback()

        return len(self.findings) > 0
