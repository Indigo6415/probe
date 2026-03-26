import time

import requests

from dependencies.modules.base import BaseModule


class Module(BaseModule):
    name = "Sensitive files"
    description = "Check if sensitive files are publicly exposed"
    severity = "critical"

    CHECKS: dict[str, tuple[str, callable]] = {
        # Environment files
        "/.env": ("Environment file", lambda r: "=" in r.text),
        "/.env.backup": ("Environment backup file", lambda r: "=" in r.text),
        "/.env.local": ("Local environment file", lambda r: "=" in r.text),
        "/.env.production": ("Production environment file", lambda r: "=" in r.text),
        "/.env.staging": ("Staging environment file", lambda r: "=" in r.text),
        # Config files
        "/web.config": (
            "IIS web config",
            lambda r: "<configuration>" in r.text.lower(),
        ),
        "/.htpasswd": ("Apache password file", lambda r: ":" in r.text),
        "/wp-config.php.bak": ("WordPress config backup", lambda r: "DB_" in r.text),
        "/config.php.bak": ("PHP config backup", lambda r: len(r.text) > 0),
        "/database.yml": ("Rails database config", lambda r: "adapter:" in r.text),
        "/config/database.yml": (
            "Rails database config",
            lambda r: "adapter:" in r.text,
        ),
        # Dependency manifests (reveal stack/versions)
        "/composer.json": ("PHP composer manifest", lambda r: "require" in r.text),
        "/composer.lock": ("PHP composer lockfile", lambda r: "packages" in r.text),
        "/package.json": (
            "Node.js package manifest",
            lambda r: "dependencies" in r.text,
        ),
        "/Gemfile": ("Ruby Gemfile", lambda r: "gem " in r.text),
        "/requirements.txt": ("Python requirements file", lambda r: len(r.text) > 0),
        # Backup / dump files
        "/backup.sql": (
            "SQL database dump",
            lambda r: "INSERT" in r.text or "CREATE" in r.text,
        ),
        "/dump.sql": (
            "SQL database dump",
            lambda r: "INSERT" in r.text or "CREATE" in r.text,
        ),
        "/db.sql": (
            "SQL database dump",
            lambda r: "INSERT" in r.text or "CREATE" in r.text,
        ),
        "/backup.zip": ("Backup archive", lambda r: r.content[:4] == b"PK\x03\x04"),
        "/backup.tar.gz": ("Backup archive", lambda r: r.content[:2] == b"\x1f\x8b"),
        # Key / credential files
        "/.ssh/id_rsa": ("Private SSH key", lambda r: "PRIVATE KEY" in r.text),
        "/.ssh/id_ed25519": ("Private SSH key", lambda r: "PRIVATE KEY" in r.text),
        "/id_rsa": ("Private SSH key", lambda r: "PRIVATE KEY" in r.text),
        "/.aws/credentials": (
            "AWS credentials file",
            lambda r: "aws_access_key" in r.text.lower(),
        ),
        # Editor / OS artifacts
        "/.DS_Store": (
            "macOS DS_Store file",
            lambda r: r.content[:4] == b"\x00\x00\x00\x01",
        ),
        "/.vscode/settings.json": ("VSCode settings", lambda r: "{" in r.text),
        "/.idea/workspace.xml": (
            "JetBrains workspace file",
            lambda r: "<project" in r.text.lower(),
        ),
    }

    def _run(self) -> bool:
        for path, (label, validate) in self.CHECKS.items():
            url = f"{self.target.url}{path}"
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200 and validate(r):
                    self.findings.append(f"{label} exposed at {url}")
                time.sleep(self.delay)
            except requests.RequestException:
                time.sleep(self.delay)
                pass
        return len(self.findings) > 0
