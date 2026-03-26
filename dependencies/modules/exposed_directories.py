import time

import requests

from dependencies.modules.base import BaseModule


class Module(BaseModule):
    name = "Directory listing"
    description = (
        "Check if directory listing is enabled or backup directories are exposed"
    )
    severity = "medium"

    # Paths to check for open directory listing
    DIRECTORIES: list[tuple[str, str]] = [
        # Backups
        ("/backup", "Backup directory"),
        ("/backups", "Backup directory"),
        ("/old", "Old files directory"),
        ("/archive", "Archive directory"),
        ("/archives", "Archive directory"),
        # Uploads
        ("/uploads", "Uploads directory"),
        ("/upload", "Upload directory"),
        ("/files", "Files directory"),
        ("/media", "Media directory"),
        ("/assets", "Assets directory"),
        # Development
        ("/src", "Source directory"),
        ("/source", "Source directory"),
        ("/dev", "Development directory"),
        ("/test", "Test directory"),
        ("/tests", "Tests directory"),
        ("/temp", "Temporary files directory"),
        ("/tmp", "Temporary files directory"),
        ("/logs", "Logs directory"),
        ("/log", "Log directory"),
        # Config / data
        ("/config", "Config directory"),
        ("/configs", "Config directory"),
        ("/data", "Data directory"),
        ("/db", "Database directory"),
        ("/sql", "SQL directory"),
        ("/dump", "Dump directory"),
        # Misc
        ("/private", "Private directory"),
        ("/secret", "Secret directory"),
        ("/hidden", "Hidden directory"),
    ]

    def _is_directory_listing(self, r: requests.Response) -> bool:
        """Check if the response looks like an open directory listing."""
        body = r.text.lower()
        indicators = [
            "index of /",
            "directory listing for",
            "parent directory",
            "<title>index of",
        ]
        return any(indicator in body for indicator in indicators)

    def _run(self) -> bool:
        for path, label in self.DIRECTORIES:
            url = f"{self.target.url}{path}"
            try:
                r = requests.get(url, timeout=5, allow_redirects=False)
                if r.status_code == 200 and self._is_directory_listing(r):
                    self.findings.append(f"{label} with open listing at {url}")
                elif r.status_code == 200:
                    self.findings.append(f"{label} accessible (no listing) at {url}")
                time.sleep(self.delay)
                r = requests.get(url + "/", timeout=5, allow_redirects=False)
                if r.status_code == 200 and self._is_directory_listing(r):
                    self.findings.append(f"{label} with open listing at {url + '/'}")
                elif r.status_code == 200:
                    self.findings.append(
                        f"{label} accessible (no listing) at {url + '/'}"
                    )
                time.sleep(self.delay)
            except requests.RequestException:
                time.sleep(self.delay)
                pass
        return len(self.findings) > 0
