import platform
import socket
import subprocess

import dependencies.cli as cli
from dependencies.target import Target


# Main function, called by probe, to check the health of a target
def check_health(target: Target) -> bool:
    """Check if a target is responsive."""
    result = True
    # First, check if the target is reachable via ping
    print(f"       {cli.dim}Healthcheck: Ping...{cli.normal}", end="", flush=True)
    if ping(target.hostname):
        cli.success()
    else:
        cli.fail()
        result = False

    # Next, check if the target is reachable via TCP (for web servers, this is usually port 80 or 443)
    print(f"       {cli.dim}Healthcheck: TCP....{cli.normal}", end="", flush=True)
    if tcp(target.hostname, target.port):
        cli.success()
    else:
        cli.fail()
        result = False

    # Next, check if the target is responsive to HTTP requests
    print(f"       {cli.dim}Healthcheck: HTTP...{cli.normal}", end="", flush=True)
    if curl(target.url):
        cli.success()
    else:
        cli.fail()
        result = False

    return result


# From here on there are helper functions for the health check, such as ping and curl


def ping(target: str) -> bool:
    """Ping a target to check if it's reachable."""
    # If the target is a URL, extract the hostname for pinging
    target = target.split("/")[2] if "://" in target else target.split("/")[0]
    try:
        result = subprocess.run(
            ["ping", "-c" if platform.system() != "Windows" else "-n", "1", target],
            capture_output=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        return False

    if result.returncode != 0:
        return False
    return True


def tcp(host: str, port: int, timeout: float = 5.0) -> bool:
    """Check if a host is reachable by opening a TCP connection."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def curl(target: str) -> bool:
    """Perform an HTTP(S) request to check if the target is responsive."""
    try:
        result = subprocess.run(["curl", "-I", target], capture_output=True, timeout=5)
    except subprocess.TimeoutExpired:
        return False

    if result.returncode != 0:
        return False
    return True
