from adapters.response import AdapterResponse
from terrapyst import TerraformWorkspace


class TerraformAdapter:

    def __init__(self):
        self.workspace = TerraformWorkspace(path="infrastructure/terraform")

    def destroy(self):
        results, _ = self.workspace.destroy(auto_approve=True)

        if results.successful:
            return AdapterResponse(code=0, message=results.stdout)
        else:
            return AdapterResponse(code=1, message=results.stdout)
