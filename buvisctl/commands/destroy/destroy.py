from adapters import TerraformAdapter, cfg, console


class CommandDestroy:
    def __init__(self):
        self.tf = []

        for p in cfg.path_terraform_workspaces:
            self.tf.append(TerraformAdapter(p))

        if len(self.tf) == 0:
            console.panic(
                "There is no Terraform workspaces defined in the configuration.",
            )
        elif len(self.tf) == 1:
            self.tf[0].name = cfg.cluster_name

    def execute(self):
        if console.confirm(f"Do you want to destroy {cfg.cluster_name}"):
            for tf in self.tf:
                with console.status(f"Destroying Proxmox VMs on {tf.name}"):
                    res = tf.destroy()

                    if res.is_ok():
                        console.success(
                            f"Proxmox VMs destroyed on {tf.name}. "
                            "Go to Proxmox UI and remove any leftover VM disks.",
                        )
                    else:
                        console.panic(
                            f"Proxmox VMs destruction failed on {tf.name}",
                            res.message,
                        )
        else:
            print("Quitting as you changed your mind")
