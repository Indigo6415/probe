import subprocess
import platform

def check_health(target: str) -> bool:
    """Check if a target is responsive."""
    # Placeholder for actual health check logic
    print("Probing target for response")
    if not ping(target):
        print("Target is not responsive to PING requests")
        return False
    if not curl(target):
        print("Target is not responsive to HTTP requests")
    return True
    

def ping(target: str) -> bool:
    """Ping a target to check if it's reachable."""
    target = target.split('/')[2] if '://' in target else target.split('/')[0]

    try:
        result = subprocess.run(
            ["ping", "-c" if platform.system() != "Windows" else "-n", "1", target],
            capture_output=True,
            timeout=5
        )
    except subprocess.TimeoutExpired:
        return False
    return True


def curl(target: str) -> bool:
    """Perform an HTTP request to check if the target is responsive."""
    try:
        result = subprocess.run(
            ["curl", "-I", target],
            capture_output=True,
            timeout=5
        )
    except subprocess.TimeoutExpired:
        return False
    return True