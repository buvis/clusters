from adapters import TerraformAdapter, cfg, console


class CommandDestroy:

    def __init__(self):
        self.tf = TerraformAdapter()

    def execute(self):
        if console.confirm(f"Do you want to destroy {cfg.cluster_name}"):
            with console.status("Destroying Proxmox nodes"):
                res = self.tf.destroy()

                if res.is_ok():
                    console.success(
                        "Proxmox nodes destroyed. "
                        "Go to Proxmox UI and remove any leftover VM disks.")
                else:
                    console.panic("Proxmox nodes destruction failed",
                                  res.message)
        else:
            print("Quitting as you changed your mind")
