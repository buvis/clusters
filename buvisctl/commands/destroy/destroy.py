import os

from terrapyst import TerraformWorkspace

DIR_TERRAFORM = "/infrastructure/terraform"


class CommandDestroy:

    def __init__(self):
        self.tf = TerraformWorkspace(path=f"{os.getcwd()}{DIR_TERRAFORM}")

    def execute(self):
        approval = input(
            "Type yes if you really want to destroy the cluster: ")

        if approval == "yes":
            print("Started destroying VMs.")
            results, _ = self.tf.destroy(auto_approve=True)

            if not results.successful:
                print(f"Failed destroying VMs. \n\n {results.stdout}")
            else:
                print("Finished destroying VMs")

        else:
            print("Quitting as you changed your mind")
