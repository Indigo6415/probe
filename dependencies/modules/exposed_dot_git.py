import time

import requests

from dependencies.modules.base import BaseModule


class Module(BaseModule):
    name = "Exposed .git"
    description = "Check if .git directory is publicly exposed"
    severity = "high"

    def _run(self) -> bool:
        # Define common files in a .git directory and how to validate them
        checks = {
            "/.git/HEAD": lambda r: r.text.startswith("ref:"),
            "/.git/config": lambda r: "[core]" in r.text,
            "/.git/index": lambda r: r.content[:4] == b"DIRC",  # binary magic bytes
            "/.git/COMMIT_EDITMSG": lambda r: len(r.text) > 0,
            "/.git/logs/HEAD": lambda r: "commit" in r.text,
        }

        # Check each path and validate the response
        for path, validate in checks.items():
            url = f"{self.target.url}{path}"
            try:
                # Use a short timeout to avoid hanging on unresponsive targets
                r = requests.get(url, timeout=5)
                if r.status_code == 200 and validate(r):
                    self.findings.append(f"Exposed {path} at {url}")
                # Dont DoS the target if it is vulnerable, just wait a bit before the next request
                time.sleep(0.05)
            except requests.RequestException:
                pass

        return len(self.findings) > 0
