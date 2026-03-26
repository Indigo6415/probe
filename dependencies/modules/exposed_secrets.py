from dependencies.modules.base import BaseModule


class Module(BaseModule):
    name = "Secrets"
    description = "Check if exposed secrets are present in frontend."
    severity = "critical"

    def _run(self) -> bool:
        return False
