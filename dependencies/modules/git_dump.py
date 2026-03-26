from dependencies.modules.base import BaseModule
import requests

class Module(BaseModule):
    name        = ".git dump"
    description = "Check if .git directory is publicly exposed"
    severity    = "high"

    def run(self) -> bool:
        url = f"{self.target.url}/.git/HEAD"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200 and r.text.startswith("ref:"):
                self.findings.append(f"Exposed .git/HEAD at {url}")
                return True
        except requests.RequestException:
            pass
        return False
