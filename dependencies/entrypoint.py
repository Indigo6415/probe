# Standard library imports
import os
from argparse import Namespace

# Custom library imports
import dependencies.args as args
import dependencies.cli as cli
import dependencies.healthcheck as healthcheck
import dependencies.module as modules
from dependencies.modules.base import BaseModule

# Type hinting imports
from dependencies.target import Target

def run():
    """The dirty function I did not want in my main probe.py file so i moved it here ;)"""
    # Parse command-line arguments first
    parsed_args: Namespace = args.parse_args()

    # Clear the screen
    print(cli.clear, end="")

    # Display sick-ass banner if not disabled
    if not parsed_args.no_bs:
        cli.banner()

    ############################
    ### START INITIALIZATION ###
    ############################
    cli.info("Initializing probe...", end="")

    # Load target, and load modules
    target: Target = Target(parsed_args.target)
    active_modules: list[type[BaseModule]] = modules.load_all()

    cli.success()

    # Summarize the target information and loaded modules, if not disabled
    if not parsed_args.no_bs:
        target.summary()
        modules.summary(active_modules)

    cli.info(f"Initialization {cli.green}complete!{cli.reset}", end="\n\n")

    ##########################
    ### START HEALTH CHECK ###
    ##########################
    # Grab terminal width, if not disabled
    if not parsed_args.no_bs:
        width = os.get_terminal_size().columns if os.isatty(1) else 80
        print(f"{cli.green}{'─' * width}{cli.reset}\n")

    # Run health check
    cli.info("Running health check against target.")
    healthy = healthcheck.check_health(target)
    if not healthy:
        cli.continue_prompt(
            "Health check failed. Do you want to continue anyway?", default="y"
        )
    print()

    #######################
    ### RUN ALL MODULES ###
    #######################
    cli.info("Running modules against target.")
    results: dict[str, list[str]] = modules.run_all(target)

    cli.end_msg()

