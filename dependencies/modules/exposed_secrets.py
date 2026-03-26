from dependencies.modules.base import BaseModule
import requests

class Module(BaseModule):
    name        = "Exposed secrets"
    description = "Check if exposed secrets are present in frontend."
    severity    = "high"

    def run(self) -> bool:
        pass
