import time

import requests

from dependencies.modules.base import BaseModule


class Module(BaseModule):
    name = "Flask / Django"
    description = "Check for Flask and Django specific misconfigurations"
    severity = "high"

    CHECKS: dict[str, tuple[str, callable]] = {
        # Werkzeug / Flask debugger — RCE if exposed
        "/console": (
            "Werkzeug interactive debugger",
            lambda r: (
                "werkzeug" in r.text.lower()
                or "interactive console" in r.text.lower()
                or "debugger" in r.text.lower()
            ),
        ),
        "/?__debugger__=yes": (
            "Werkzeug debugger probe",
            lambda r: "werkzeug" in r.text.lower() or "traceback" in r.text.lower(),
        ),
        # Django admin
        "/django-admin/": (
            "Django admin panel",
            lambda r: "django" in r.text.lower() and "login" in r.text.lower(),
        ),
        "/admin/login/": (
            "Django admin login",
            lambda r: (
                "csrfmiddlewaretoken" in r.text.lower() and "django" in r.text.lower()
            ),
        ),
        # Django debug toolbar
        "/__debug__/": (
            "Django debug toolbar",
            lambda r: "djdt" in r.text.lower() or "debug toolbar" in r.text.lower(),
        ),
        "/__debug__/sql_select/": (
            "Django debug toolbar SQL panel",
            lambda r: "sql" in r.text.lower(),
        ),
        # Django error pages (DEBUG=True leaks full stack trace)
        "/this-path-should-not-exist": (
            "Django DEBUG mode enabled",
            lambda r: (
                "django" in r.text.lower()
                and "traceback" in r.text.lower()
                and "request information" in r.text.lower()
            ),
        ),
        # Django REST framework browsable API
        "/api/": (
            "Django REST framework browsable API",
            lambda r: (
                "django rest framework" in r.text.lower()
                or "browsable api" in r.text.lower()
            ),
        ),
        # Flask debug mode
        "/debug": (
            "Flask debug page",
            lambda r: "flask" in r.text.lower() and "debug" in r.text.lower(),
        ),
        # Exposed config / settings
        "/config": (
            "Exposed config endpoint",
            lambda r: (
                "secret" in r.text.lower()
                or "debug" in r.text.lower()
                or "database" in r.text.lower()
            ),
        ),
        "/settings": (
            "Exposed settings endpoint",
            lambda r: "secret" in r.text.lower() or "debug" in r.text.lower(),
        ),
        # Static file misconfigurations
        "/static/admin/": (
            "Django static admin files exposed",
            lambda r: "index of" in r.text.lower(),
        ),
        "/media/": (
            "Django media directory exposed",
            lambda r: "index of" in r.text.lower(),
        ),
        # Celery / task queue
        "/flower/": (
            "Celery Flower task monitor",
            lambda r: "flower" in r.text.lower() or "celery" in r.text.lower(),
        ),
        "/flower/dashboard": (
            "Celery Flower dashboard",
            lambda r: "flower" in r.text.lower() or "celery" in r.text.lower(),
        ),
    }

    def _detect_framework(self) -> tuple[bool, bool]:
        """
        Returns (is_flask, is_django) by inspecting headers and response body.
        If neither is detected, skip the module.
        """
        try:
            r = requests.get(self.target.url, timeout=5)
            headers = {k.lower(): v.lower() for k, v in r.headers.items()}
            body = r.text.lower()

            is_flask = (
                "werkzeug" in headers.get("server", "")
                or "flask" in body
                or "jinja" in body
            )
            is_django = (
                "csrftoken" in r.cookies
                or "django" in body
                or "csrfmiddlewaretoken" in body
                or "django" in headers.get("x-powered-by", "")
            )
            return is_flask, is_django
        except requests.RequestException:
            return False, False

    def _check_werkzeug_pin(self) -> None:
        """
        Check if the Werkzeug debugger PIN screen is exposed.
        Even PIN-protected, its presence is a critical misconfiguration.
        """
        url = f"{self.target.url}/console"
        try:
            r = requests.get(url, timeout=5)
            if (
                r.status_code == 200
                and "pin" in r.text.lower()
                and "werkzeug" in r.text.lower()
            ):
                self.findings.append(
                    f"Werkzeug debugger PIN prompt exposed at {url} — PIN can potentially be calculated from server info"
                )
        except requests.RequestException:
            pass

    def _check_django_debug(self) -> None:
        """
        Request a path that definitely does not exist.
        Django with DEBUG=True returns a detailed error page with settings, paths, and env vars.
        """
        url = f"{self.target.url}/__probe_debug_check__"
        try:
            r = requests.get(url, timeout=5)
            if (
                r.status_code == 404
                and "django" in r.text.lower()
                and "traceback" not in r.text.lower()
                and "request information" not in r.text.lower()
            ):
                pass  # Normal Django 404
            elif r.status_code == 404 and "request information" in r.text.lower():
                self.findings.append(
                    f"Django DEBUG=True detected — detailed error pages expose settings, environment, and file paths at {url}"
                )
        except requests.RequestException:
            pass

    def _run(self) -> bool:
        is_flask, is_django = self._detect_framework()

        if not is_flask and not is_django:
            return False

        for path, (label, validate) in self.CHECKS.items():
            url = f"{self.target.url}{path}"
            try:
                r = requests.get(url, timeout=5, allow_redirects=True)
                if r.status_code == 200 and validate(r):
                    self.findings.append(f"{label} at {url}")
                time.sleep(0.05)
            except requests.RequestException:
                pass

        self._check_werkzeug_pin()
        self._check_django_debug()

        return len(self.findings) > 0
