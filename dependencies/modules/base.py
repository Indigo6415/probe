from abc import ABC, abstractmethod
from dependencies.target import Target

class BaseModule(ABC):
    # Metadata — override these in each module
    name: str = "unnamed"
    description: str = ""
    severity: str = "info"       # info | low | medium | high | critical

    def __init__(self, target: Target):
        self.target = target
        self.findings: list[str] = []

    @abstractmethod
    def run(self) -> bool:
        """Run the module. Return True if a finding was discovered."""
        ...

    def report(self) -> list[str]:
        """Return findings after run()."""
        return self.findings
