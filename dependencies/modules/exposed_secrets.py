from dependencies.modules.base import BaseModule


class Module(BaseModule):
    name = "Secrets"
    description = "Check if exposed secrets are present in frontend."
    severity = "critical"

    def _run(self) -> bool:
        # TODO: Implement a module that checks for exposed secrets
        return False
