import ipaddress
from urllib.parse import urlparse
import socket
import dependencies.cli as cli

class Target:
    def __init__(self, target: str):
        """
        Args: target (str): The target to be probed, which can be an IP address, hostname, or URL.
        Example:
            target = Target("http://example.com/")
            target = Target("10.10.10.10")
            target = Target("example.com:1234")
        """
        # Initialize variables
        self.target = target
        self.url = ""
        self.hostname = ""
        self.ip = ""
        self.port = 80

        # Disassemble the target into its components
        self.disassemble()


    def disassemble(self):
        """Disassemble the target into its components (URL, hostname, IP, port)"""
        # Normalise: add scheme if missing so urlparse works reliably
        raw = self.target
        if not raw.startswith("http://") and not raw.startswith("https://"):
            raw = "http://" + raw

        parsed = urlparse(raw.rstrip('/'))

        self.hostname = parsed.hostname or ""
        self.port = parsed.port or (443 if parsed.scheme == "https" else 80)

        # Build clean URL always
        explicit_port = parsed.port is not None
        original_had_scheme = self.target.startswith("http://") or self.target.startswith("https://")

        if explicit_port or not original_had_scheme:
            self.url = f"{parsed.scheme}://{self.hostname}:{self.port}"
        else:
            self.url = f"{parsed.scheme}://{self.hostname}"

        # Resolve IP
        if self.hostname:
            try:
                ipaddress.ip_address(self.hostname)
                self.ip = self.hostname
            except ValueError:
                try:
                    self.ip = socket.gethostbyname(self.hostname)
                except socket.gaierror:
                    self.ip = None


    def summary(self) -> None:
        """Print a summary of the target's components."""
        col_w = 12
        label = f"{cli.normal}{cli.dim}"
        value = f"{cli.normal}{cli.reset}"

        print(f"\n{cli.bold}{cli.cyan}  Target Summary{cli.reset}")
        print(f"  {cli.dim}{'─' * 30}{cli.reset}")
        print(f"  {label}{'Target':<{col_w}}{cli.reset}  {value}{self.target}{cli.reset}")
        print(f"  {label}{'URL':<{col_w}}{cli.reset}  {value}{self.url}{cli.reset}")
        print(f"  {label}{'Hostname':<{col_w}}{cli.reset}  {value}{self.hostname}{cli.reset}")
        print(f"  {label}{'IP':<{col_w}}{cli.reset}  {value}{self.ip if self.ip else f'{cli.yellow}unresolved{cli.reset}'}{cli.reset}")
        print(f"  {label}{'Port':<{col_w}}{cli.reset}  {value}{self.port}{cli.reset}")
        print(f"  {cli.dim}{'─' * 30}{cli.reset}{cli.normal}\n")
