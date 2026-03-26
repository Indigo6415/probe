# probe

A fast, modular web server misconfiguration scanner. Point it at a URL or IP address and it automatically runs a suite of checks — exposed `.git` directories, sensitive files, open admin panels, and more.

```
[INFO] Target Summary
  ──────────────────────────────────────────────
  Target        https://example.com
  URL           https://example.com
  Hostname      example.com
  IP            93.184.216.34
  Port          443
  ──────────────────────────────────────────────

       Running module: Exposed .git...          [HIT]
       Running module: Exposed Sensitive Files... [DONE]
       Running module: Exposed Admin Panels...   [DONE]
```

---

## Features

- Detects exposed `.git`, `.svn`, `.hg` and other version control artifacts
- Checks for sensitive files (`.env`, private keys, database dumps, config backups)
- Identifies open directory listings and accessible backup directories
- Scans for exposed admin panels (WordPress, phpMyAdmin, Tomcat, Jenkins, and more)
- Detects development artifacts (CI configs, Dockerfiles, dependency manifests)
- Probes API endpoints including GraphQL introspection
- Checks for miscellaneous misconfigurations (server status pages, Swagger specs, Spring Boot actuators)
- Modular architecture — drop in a new `.py` file to add a check
- Supports URLs, hostnames, and bare IP addresses with optional port

---

## Installation

**Requirements:** Python 3.10+

### 1. Clone the repository

```bash
git clone https://github.com/indigo6415/probe.git
cd probe
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Make the script executable *(Linux / macOS)*

```bash
chmod +x probe
```

---

## Usage

```
usage: probe [-h] [--batch] target

Probe a website URL or IP for misconfigurations

positional arguments:
  target        Website URL (http/https), hostname, or IP address

options:
  -h, --help    show this help message and exit
  --batch       Run in batch mode (disables interactive prompts)
```

### Examples

```bash
# Scan a URL
./probe https://example.com

# Scan an IP address
./probe 10.10.10.10

# Scan a HTTP host on a non-standard port
./probe http://example.com:8080

# Scan with HTTPS on a custom port
./probe https://example.com:8443

# Non-interactive batch mode (for scripting / pipelines) (or if you have Parkinson and have trouble hitting "Enter")
./probe https://example.com --batch
```

---

## Modules

| Module | Severity | Description |
|---|---|---|
| Exposed .git | High | Checks for publicly accessible `.git` directory and its files |
| Exposed Version Control | High | Checks for `.svn`, `.hg`, `.bzr`, and CVS artifacts |
| Exposed Sensitive Files | Critical | Checks for `.env`, private keys, config backups, database dumps |
| Exposed Directories | Medium | Checks for open directory listings and accessible backup paths |
| Exposed Admin Panels | High | Checks for admin panels across common frameworks and tools |
| Exposed Dev Artifacts | Medium | Checks for CI configs, Dockerfiles, IDE files, and build manifests |
| Exposed API Endpoints | High | Checks for exposed REST/GraphQL endpoints and introspection |
| Miscellaneous | Low | Checks for server status pages, Swagger specs, Spring Boot actuators |

---

## Adding a Module

Drop a new file into the `modules/` directory. It will be picked up automatically — no registration required.

```python
# modules/my_check.py
import requests
from dependencies.modules.base import BaseModule

class Module(BaseModule):
    name        = "My Check"
    description = "Short description of what this checks"
    severity    = "medium"   # info | low | medium | high | critical

    def _run(self) -> bool:
        url = f"{self.target.url}/some-path"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200 and "some indicator" in r.text:
                self.findings.append(f"Found something at {url}")
                return True
        except requests.RequestException:
            pass
        return False
```

The base class handles printing the module name and result prefix (`[HIT]` / `[DONE]`) automatically — your `_run()` only needs to populate `self.findings` and return `True` if anything was found.

---

## Project Structure

```
probe/
├── probe               # Entrypoint
├── requirements.txt
├── dependencies/
│   ├── cli.py          # Coloured output helpers
│   ├── target.py       # Target parsing (URL, hostname, IP, port)
│   └── modules/
│       ├── __init__.py
│       ├── base.py     # BaseModule abstract class
│       ├── git_dump.py
│       ├── version_control.py
│       ├── sensitive_files.py
│       ├── directories.py
│       ├── admin_panels.py
│       ├── dev_artifacts.py
│       ├── api_endpoints.py
│       └── miscellaneous.py
└── modules.py          # Module loader and runner
```

---

## Disclaimer

This tool is intended for use on systems you own or have explicit permission to test. Unauthorized scanning of systems is illegal. The authors accept no liability for misuse.
