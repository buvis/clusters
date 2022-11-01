import os

from python_terraform import IsNotFlagged, Terraform

DIR_TERRAFORM = "/infrastructure/terraform"


class CommandDestroy:

    def __init__(self):
        self.tf = Terraform()

    def execute(self):
        cwd = os.getcwd()

        try:
            os.chdir(cwd + DIR_TERRAFORM)
        except FileNotFoundError:
            print(f"No plan was found in {cwd + DIR_TERRAFORM}")
        else:
            self.tf.destroy(
                capture_output="yes",
                no_color=IsNotFlagged,
                force=IsNotFlagged,
                auto_approve=False,
            )
            os.chdir(cwd)
