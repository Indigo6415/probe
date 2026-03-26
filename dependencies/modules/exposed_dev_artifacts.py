import time

import requests

from dependencies.modules.base import BaseModule


class Module(BaseModule):
    name = "Development artifacts"
    description = "Check if development artifacts are publicly accessible"
    severity = "medium"

    ARTIFACTS: list[tuple[str, str, callable]] = [
        # PHP info / debug pages
        (
            "/phpinfo.php",
            "PHP info page",
            lambda r: "phpinfo()" in r.text.lower() or "php version" in r.text.lower(),
        ),
        ("/info.php", "PHP info page", lambda r: "phpinfo()" in r.text.lower()),
        ("/test.php", "PHP test page", lambda r: len(r.text) > 0),
        ("/debug.php", "PHP debug page", lambda r: len(r.text) > 0),
        # Editor / IDE artifacts
        ("/.vscode/settings.json", "VSCode settings", lambda r: "{" in r.text),
        ("/.vscode/launch.json", "VSCode launch config", lambda r: "{" in r.text),
        (
            "/.idea/workspace.xml",
            "JetBrains workspace",
            lambda r: "<project" in r.text.lower(),
        ),
        ("/.idea/.name", "JetBrains project name", lambda r: len(r.text) > 0),
        # OS artifacts
        (
            "/.DS_Store",
            "macOS DS_Store file",
            lambda r: r.content[:4] == b"\x00\x00\x00\x01",
        ),
        ("/Thumbs.db", "Windows Thumbs.db file", lambda r: len(r.content) > 0),
        # Dependency / build manifests
        ("/composer.json", "PHP Composer manifest", lambda r: "require" in r.text),
        ("/composer.lock", "PHP Composer lockfile", lambda r: "packages" in r.text),
        (
            "/package.json",
            "Node.js package manifest",
            lambda r: "dependencies" in r.text or "name" in r.text,
        ),
        ("/package-lock.json", "Node.js lockfile", lambda r: "dependencies" in r.text),
        ("/yarn.lock", "Yarn lockfile", lambda r: "# yarn lockfile" in r.text.lower()),
        ("/Gemfile", "Ruby Gemfile", lambda r: "gem " in r.text),
        ("/Gemfile.lock", "Ruby Gemfile lockfile", lambda r: "GEM" in r.text),
        ("/requirements.txt", "Python requirements", lambda r: len(r.text) > 0),
        ("/Pipfile", "Python Pipfile", lambda r: "[packages]" in r.text),
        ("/Pipfile.lock", "Python Pipfile lockfile", lambda r: "default" in r.text),
        ("/go.mod", "Go module file", lambda r: "module " in r.text),
        ("/pom.xml", "Maven POM file", lambda r: "<project" in r.text.lower()),
        ("/build.gradle", "Gradle build file", lambda r: "dependencies" in r.text),
        # CI/CD configs (reveal pipeline structure)
        ("/.travis.yml", "Travis CI config", lambda r: "language:" in r.text),
        (
            "/.gitlab-ci.yml",
            "GitLab CI config",
            lambda r: "stages:" in r.text or "script:" in r.text,
        ),
        (
            "/.github/workflows",
            "GitHub Actions workflows",
            lambda r: "index of" in r.text.lower(),
        ),
        ("/Jenkinsfile", "Jenkinsfile", lambda r: "pipeline" in r.text.lower()),
        ("/docker-compose.yml", "Docker Compose file", lambda r: "services:" in r.text),
        (
            "/docker-compose.yaml",
            "Docker Compose file",
            lambda r: "services:" in r.text,
        ),
        ("/Dockerfile", "Dockerfile", lambda r: "FROM " in r.text),
        # Misc
        ("/webpack.config.js", "Webpack config", lambda r: "module.exports" in r.text),
        ("/vite.config.js", "Vite config", lambda r: "export default" in r.text),
        ("/vite.config.ts", "Vite config", lambda r: "export default" in r.text),
        ("/.editorconfig", "Editor config", lambda r: "[" in r.text),
        ("/.eslintrc", "ESLint config", lambda r: "{" in r.text),
        ("/.eslintrc.json", "ESLint config", lambda r: "{" in r.text),
        ("/tsconfig.json", "TypeScript config", lambda r: "compilerOptions" in r.text),
    ]

    def _run(self) -> bool:
        for path, label, validate in self.ARTIFACTS:
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
