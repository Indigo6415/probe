from abc import ABC, abstractmethod

import dependencies.cli as cli
from dependencies.target import Target


class BaseModule(ABC):
    # Metadata — override these in each module
    name: str = "unnamed"
    description: str = ""
    severity: str = "info"  # info | low | medium | high | critical

    def __init__(self, target: Target):
        self.target = target
        self.findings: list[str] = []
        self.delay: float = 0.001  # 100ms

    def run(self) -> bool:
        """Run the module. Return True if a finding was discovered."""
        # Fancy print statement that tells the user which module is running.
        print(
            f"       {cli.dim}Running module: {self.name}...{cli.reset}",
            end="",
            flush=True,
        )

        # Run the actual module
        result = self._run()
        # Print [HIT] if a finding was discovered, otherwise just move to the next line.
        if result:
            cli.hit()
        else:
            cli.done()

        return result

    @abstractmethod
    def _run(self) -> bool:
        """Run the module. Return True if a finding was discovered."""
        ...

    def report(self) -> list[str]:
        """Return findings after run()."""
        return self.findings
