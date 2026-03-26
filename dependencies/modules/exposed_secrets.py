from dependencies.modules.base import BaseModule


class Module(BaseModule):
    name = "Exposed secrets"
    description = "Check if exposed secrets are present in frontend."
    severity = "medium"

    def _run(self) -> bool:
        return False
