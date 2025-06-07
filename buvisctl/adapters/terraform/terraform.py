import os

from adapters.response import AdapterResponse
from terrapyst import TerraformWorkspace


class TerraformAdapter:
    def __init__(self, path_workspace):
        self.workspace = TerraformWorkspace(path=path_workspace)
        self.name = os.path.basename(path_workspace)

    def destroy(self):
        init_results = self.workspace.init()

        if not init_results.successful:
            return AdapterResponse(code=1, message=init_results.stdout)

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
        os.environ["TF_CLI_ARGS_apply"] = (
            "-parallelism=2"  # Proxmox runs to race conditions if creating many VMs in parallel
        )
        results, _ = self.workspace.apply(auto_approve=True)

        if results.successful:
            return AdapterResponse()
        else:
            return AdapterResponse(code=1, message=results.stdout)

        if not results.successful:
            print(f"Failed creating VMs creation failed. \n\n {results.stdout}")
        else:
            print("Finished creating VMs.")
