import time

import requests

from dependencies.modules.base import BaseModule


class Module(BaseModule):
    name = "Admin panels"
    description = "Check if admin panels are publicly accessible"
    severity = "medium"

    PANELS: list[tuple[str, str]] = [
        # Generic
        ("/admin", "Generic admin panel"),
        ("/admin/", "Generic admin panel"),
        ("/administrator", "Generic administrator panel"),
        ("/administrator/", "Generic administrator panel"),
        ("/adminpanel", "Generic admin panel"),
        ("/admin/login", "Generic admin login"),
        ("/admin/dashboard", "Generic admin dashboard"),
        # WordPress
        ("/wp-admin", "WordPress admin panel"),
        ("/wp-admin/", "WordPress admin panel"),
        ("/wp-login.php", "WordPress login page"),
        # Joomla
        ("/administrator/index.php", "Joomla admin panel"),
        # Drupal
        ("/user/login", "Drupal login page"),
        ("/admin/config", "Drupal config panel"),
        # Laravel
        ("/nova", "Laravel Nova admin panel"),
        ("/horizon", "Laravel Horizon dashboard"),
        ("/telescope", "Laravel Telescope debugger"),
        # Django
        ("/django-admin", "Django admin panel"),
        ("/django-admin/", "Django admin panel"),
        # phpMyAdmin
        ("/phpmyadmin", "phpMyAdmin panel"),
        ("/phpmyadmin/", "phpMyAdmin panel"),
        ("/pma", "phpMyAdmin panel"),
        ("/pma/", "phpMyAdmin panel"),
        ("/mysql", "MySQL admin panel"),
        ("/mysqladmin", "MySQL admin panel"),
        # Tomcat
        ("/manager/html", "Tomcat manager panel"),
        ("/host-manager/html", "Tomcat host manager panel"),
        # Jenkins
        ("/jenkins", "Jenkins dashboard"),
        ("/jenkins/login", "Jenkins login"),
        # Grafana
        ("/grafana", "Grafana dashboard"),
        ("/grafana/login", "Grafana login"),
        # Kibana
        ("/kibana", "Kibana dashboard"),
        ("/app/kibana", "Kibana dashboard"),
        # Other
        ("/portainer", "Portainer container manager"),
        ("/adminer.php", "Adminer database manager"),
        ("/cpanel", "cPanel hosting panel"),
        ("/plesk", "Plesk hosting panel"),
        ("/webmail", "Webmail panel"),
    ]

    def _looks_like_login(self, r: requests.Response) -> bool:
        """Check if the response looks like an admin/login page."""
        body = r.text.lower()
        indicators = [
            "login",
            "log in",
            "sign in",
            "username",
            "password",
            "admin",
            "dashboard",
            "panel",
            "authenticate",
        ]
        return any(indicator in body for indicator in indicators)

    def _run(self) -> bool:
        for path, label in self.PANELS:
            url = f"{self.target.url}{path}"
            try:
                r = requests.get(url, timeout=5, allow_redirects=False)
                if r.status_code == 200 and self._looks_like_login(r):
                    self.findings.append(f"{label} accessible at {url}")
                elif r.status_code == 200:
                    self.findings.append(
                        f"{label} returned 200 at {url} (no login form detected)"
                    )
                elif r.status_code == 403:
                    self.findings.append(f"{label} exists but is forbidden at {url}")
                time.sleep(self.delay)
            except requests.RequestException:
                time.sleep(self.delay)
                pass
        return len(self.findings) > 0
