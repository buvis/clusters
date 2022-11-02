from adapters import TerraformAdapter


class CommandDestroy:

    def __init__(self):
        self.tf = TerraformAdapter()

    def execute(self):
        approval = input(
            "Type yes if you really want to destroy the cluster: ")

        if approval == "yes":
            print("Started destroying VMs.")
            res = self.tf.destroy()

            if res.is_ok():
                print("Finished destroying VMs")
            else:
                print(f"Failed destroying VMs. \n\n {res.message}")
        else:
            print("Quitting as you changed your mind")
