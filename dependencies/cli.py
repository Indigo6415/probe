import colorama

green = colorama.Fore.GREEN
red = colorama.Fore.RED
yellow = colorama.Fore.YELLOW
cyan = colorama.Fore.CYAN
blue = colorama.Fore.BLUE
reset = colorama.Fore.RESET

bold = colorama.Style.BRIGHT
dim = colorama.Style.DIM
normal = colorama.Style.NORMAL

success = f"{reset}{bold}[{green}OK{reset}]{normal}"
error = f"{reset}{bold}[{red}!!!{reset}]{normal}"
warning = f"{reset}{bold}[{yellow}!{reset}]{normal}"
info = f"{reset}{bold}[{cyan}I{reset}]{normal}"