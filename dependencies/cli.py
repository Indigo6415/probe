import os
import random

import colorama

import dependencies.args as args

green = colorama.Fore.GREEN
red = colorama.Fore.RED
yellow = colorama.Fore.YELLOW
cyan = colorama.Fore.CYAN
blue = colorama.Fore.BLUE
pink = colorama.Fore.LIGHTBLUE_EX
magenta = colorama.Fore.MAGENTA
black = colorama.Fore.BLACK
dim = colorama.Style.DIM  # light grey
reset = colorama.Fore.RESET

bold = colorama.Style.BRIGHT
normal = colorama.Style.NORMAL

_success = f"{reset}{bold}[{green}OK{reset}]{normal}"
_fail = f"{reset}{bold}[{red}FAIL{reset}]{normal}"
_error = f"{reset}{bold}[{red}!!!{reset}]{normal}"
_warning = f"{reset}{bold}[{yellow}WARNING{reset}]{normal}"
_info = f"{reset}{bold}[{cyan}INFO{reset}]{normal}"

clear = (
    "\033[2J\033[H"  # ANSI escape code to clear the screen and move cursor to top-left
)

parsed_args = args.parse_args()


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


def hit(msg: str = "", end: str = "\n") -> None:
    """Print a hit message with a red [HIT] prefix."""
    print(f"{normal}{bold}[{green}HIT!{reset}]{normal} {msg}", end=end)


def done(msg: str = "", end: str = "\n") -> None:
    """Print a done message with a blue [DONE] prefix."""
    print(f"{normal}{bold}[{blue}DONE{reset}]{normal} {msg}", end=end)


def continue_prompt(msg: str, default: str = "y") -> None:
    """Prompts the user to continue with a yes/no question. Default is 'y' (yes). Exits if the user answers no."""
    prompt = f"{msg} [{f'{green}YES{reset}' if default.lower() == 'y' else 'yes'}/{f'{red}NO{reset}' if default.lower() == 'n' else 'no'}]: "
    while True:
        if parsed_args.batch:
            print(prompt + default)
            choice = default.lower()
        else:
            choice = input(prompt).strip().lower()
        # If the user just presses enter, use the default choice
        if not choice and default:
            choice = default.lower()
        if choice in ["y", "yes"]:
            return
        elif choice in ["n", "no"]:
            print("Exiting.")
            os._exit(0)
        else:
            print("Please enter 'y' or 'n'.")


def end_msg() -> None:
    """Print a final message at the end of the probe execution."""
    print()
    print(f"Module execution complete! {green}Probe finished!{reset}")
    print()
    warning("These modules only check for a set number of triggers.")
    warning(
        f"{red}{bold}ALWAYS{reset}{normal} manually check the target yourself, even if no findings were discovered."
    )


def banner() -> None:
    """Print the probe banner."""
    width = os.get_terminal_size().columns if os.isatty(1) else 80
    random_number = random.randint(1, 2)
    if random_number == 1:
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
    elif random_number == 2:
        print(f"""
                                           -
                                     -      -
        ---=---+---=---        -      -      -
               \\                -      -      -
         ---=---+-I-=---        -      -      -         {green}01010000 01010010 01001111 01000010 01000101{reset}
                |\\              -      -      -
          ---=----+----=---    -      -      -          {cyan}indigo6415{reset} - Probe v1.0
                |                    -      -
                |                          -
                |
                |
                ^

{green}{"─" * width}{reset}
        """)
