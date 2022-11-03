from adapters import cfg
from adapters.response import AdapterResponse
from terrapyst import TerraformWorkspace


class TerraformAdapter:

    def __init__(self):
        self.workspace = TerraformWorkspace(path=cfg.path_terraform_workspace)

    def destroy(self):
        results, _ = self.workspace.destroy(auto_approve=True)

        if results.successful:
            return AdapterResponse()
        else:
            return AdapterResponse(code=1, message=results.stdout)

    def init(self):
        results = self.workspace.init()

        if results.successful:
            return AdapterResponse()
        else:
            return AdapterResponse(code=1, message=results.stdout)

    def apply(self):
        results, _ = self.workspace.apply(auto_approve=True)

        if results.successful:
            return AdapterResponse()
        else:
            return AdapterResponse(code=1, message=results.stdout)

        if not results.successful:
            print(
                f"Failed creating VMs creation failed. \n\n {results.stdout}")
        else:
            print("Finished creating VMs.")
