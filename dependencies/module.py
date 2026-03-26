import importlib
import pkgutil

import dependencies.cli as cli
import dependencies.modules as modules_pkg
from dependencies.modules.base import BaseModule
from dependencies.target import Target


def load_all() -> list[type[BaseModule]]:
    """Dynamically import every module_name.py in the modules/ folder."""
    found = []
    for _, module_name, _ in pkgutil.iter_modules(modules_pkg.__path__):
        if module_name == "base":
            continue
        mod = importlib.import_module(f"dependencies.modules.{module_name}")
        if hasattr(mod, "Module"):
            found.append(mod.Module)
    return sorted(found, key=lambda m: m.name)


def run_all(target: Target) -> dict[str, list[str]]:
    """Run all modules against a target and return findings per module."""
    results = {}
    for ModuleClass in load_all():
        instance = ModuleClass(target)
        instance.run()
        findings = instance.report()
        if findings:
            results[ModuleClass.name] = findings
            for i, finding in enumerate(findings):
                print(f"          {cli.red}{i + 1}. * {finding}{cli.reset}")
            # TODO: Display findings in real-time instead of waiting until the end
    return results


def summary(active_modules: list[type[BaseModule]]) -> None:
    width = 100
    col_w = 32
    severity_color = {
        "info": cli.cyan,
        "low": cli.green,
        "medium": cli.yellow,
        "high": cli.red,
        "critical": f"{cli.bold}{cli.red}",
    }
    print(f"{cli.bold}{cli.cyan}  Module Summary{cli.reset}\n")
    print(
        f"{cli.normal}{cli.reset}  Loaded Modules ({cli.cyan}{len(active_modules)}{cli.reset}){cli.reset}\n"
    )
    # print(f"  {cli.dim}{'─' * (width - 4)}{cli.reset}")
    print(
        f"  {cli.normal}{cli.dim}{'Name':<{col_w}}{cli.reset}  {cli.normal}{cli.dim}{'Severity':<8}{cli.reset}  {cli.normal}{cli.dim}{'Description'}{cli.reset}"
    )
    print(f"  {cli.dim}{'─' * (width - 4)}{cli.reset}{cli.normal}")
    for ModuleClass in active_modules:
        sev_color = severity_color.get(ModuleClass.severity, cli.reset)
        sev = f"{sev_color}{ModuleClass.severity:<8}{cli.reset}{cli.normal}"
        print(
            f"  {cli.normal}{cli.reset}{ModuleClass.name:<{col_w}}{cli.reset}  {sev}  {cli.dim}{ModuleClass.description:<35}{cli.normal}"
        )
    print(f"  {cli.dim}{'─' * (width - 4)}{cli.reset}{cli.normal}\n")
