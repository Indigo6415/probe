import time

import requests

from dependencies.modules.base import BaseModule


class Module(BaseModule):
    name = "Version control"
    description = "Check if version control files and directories are publicly exposed"
    severity = "high"

    CHECKS: dict[str, tuple[str, callable]] = {
        # Git
        "/.git/HEAD": ("Git HEAD file", lambda r: r.text.startswith("ref:")),
        "/.git/config": ("Git config file", lambda r: "[core]" in r.text),
        "/.git/index": ("Git index file", lambda r: r.content[:4] == b"DIRC"),
        "/.git/COMMIT_EDITMSG": ("Git commit message", lambda r: len(r.text) > 0),
        "/.git/logs/HEAD": ("Git commit log", lambda r: "commit" in r.text),
        "/.git/description": ("Git description file", lambda r: len(r.text) > 0),
        "/.git/packed-refs": ("Git packed refs", lambda r: "# pack-refs" in r.text),
        "/.git/refs/heads": ("Git branch refs", lambda r: "index of" in r.text.lower()),
        "/.gitignore": ("Git ignore file", lambda r: len(r.text) > 0),
        "/.gitmodules": ("Git submodules file", lambda r: "[submodule" in r.text),
        "/.gitattributes": ("Git attributes file", lambda r: len(r.text) > 0),
        # Subversion
        "/.svn/entries": (
            "SVN entries file",
            lambda r: "dir" in r.text or r.text.startswith("10"),
        ),
        "/.svn/wc.db": (
            "SVN working copy database",
            lambda r: r.content[:6] == b"SQLite",
        ),
        "/.svn/format": ("SVN format file", lambda r: r.text.strip().isdigit()),
        # Mercurial
        "/.hg/dirstate": ("Mercurial dirstate", lambda r: len(r.content) > 0),
        "/.hg/hgrc": (
            "Mercurial config",
            lambda r: "[paths]" in r.text or "[ui]" in r.text,
        ),
        "/.hg/store/fncache": ("Mercurial file cache", lambda r: len(r.text) > 0),
        "/.hgignore": ("Mercurial ignore file", lambda r: len(r.text) > 0),
        # Bazaar
        ("/.bzr/README"): ("Bazaar repository", lambda r: "bazaar" in r.text.lower()),
        ("/.bzrignore"): ("Bazaar ignore file", lambda r: len(r.text) > 0),
        # CVS
        ("/CVS/Root"): ("CVS root file", lambda r: ":" in r.text),
        ("/CVS/Entries"): ("CVS entries file", lambda r: "/" in r.text),
    }

    def _run(self) -> bool:
        for path, (label, validate) in self.CHECKS.items():
            url = f"{self.target.url}{path}"
            try:
                r = requests.get(url, timeout=5, allow_redirects=False)
                if r.status_code == 200 and validate(r):
                    self.findings.append(f"{label} exposed at {url}")
                time.sleep(self.delay)
            except requests.RequestException:
                time.sleep(self.delay)
                pass
        return len(self.findings) > 0
