import colorama
import os

green = colorama.Fore.GREEN
red = colorama.Fore.RED
yellow = colorama.Fore.YELLOW
cyan = colorama.Fore.CYAN
blue = colorama.Fore.BLUE
dim = colorama.Style.DIM # light grey
reset = colorama.Fore.RESET

bold = colorama.Style.BRIGHT
normal = colorama.Style.NORMAL

_success = f"{reset}{bold}[{green}OK{reset}]{normal}"
_fail = f"{reset}{bold}[{red}FAIL{reset}]{normal}"
_error = f"{reset}{bold}[{red}!!!{reset}]{normal}"
_warning = f"{reset}{bold}[{yellow}!{reset}]{normal}"
_info = f"{reset}{bold}[{cyan}INFO{reset}]{normal}"

clear = "\033[2J\033[H" # ANSI escape code to clear the screen and move cursor to top-left

def success(msg: str = "", end: str = "\n") -> None:
    """Print a success message with a green [OK] prefix."""
    print(f"{_success} {msg}", end=end)

def info(msg: str = "", end: str = "\n") -> None:
    """Print an informational message with a cyan [INFO] prefix."""
    print(f"{_info} {msg}", end=end)

def fail(msg: str = "", end: str = "\n") -> None:
    """Print a failure message with a red [FAIL] prefix."""
    print(f"{_fail} {msg}", end=end)

def error(msg: str = "", end: str = "\n") -> None:
    """Print an error message with a red [!!!] prefix. Exits immediately with error code 1."""
    print(f"{_error} {msg}", end=end)
    os._exit(1)  # Exit immediately with error code 1

def warning(msg: str = "", end: str = "\n") -> None:
    """Print a warning message with a yellow [!] prefix."""
    print(f"{_warning} {msg}", end=end)

def banner() -> None:
    """Print the probe banner."""
    width = os.get_terminal_size().columns if os.isatty(1) else 80

    print(f"""
        +--------------+
       /|             /|
      / |            / |
     *--+-----------*  |
     |  |           |  |
     |  |           |  |        {green}01010000 01010010 01001111 01000010 01000101{reset}
     |  |           |  |
     |  +-----------+--+        {cyan}indigo6415{reset} - Probe v1.0
     | /            | /
     |/             |/
     *--------------*

{green}{"─" * width}{reset}
        """)
