from adapters import (
    CiliumAdapter,
    FluxAdapter,
    KubernetesAdapter,
    SocketAdapter,
    TalosAdapter,
    TerraformAdapter,
    cfg,
    console,
)


class CommandBootstrap:
    def __init__(self) -> None:
        self.socket = SocketAdapter()
        self.tf = []

        for p in cfg.path_terraform_workspaces:
            self.tf.append(TerraformAdapter(p))
        self.talos = TalosAdapter()
        self.cilium = CiliumAdapter()

    def execute(self):
        self.infra_create()
        self.generate_talos_config()
        self.configure_talos_nodes()
        self.bootstrap_talos()
        self.get_cluster_config()
        self.wait_for_cni()
        self.deploy_flux()

    def infra_create(self):
        for tf in self.tf:
            with console.status(f"Initializing {tf.name} Terraform workspace"):
                res = tf.init()

                if res.is_ok():
                    console.success(f"Terraform workspace initialized for {tf.name}")
                else:
                    console.panic(
                        f"Terraform workspace initialization failed " f"for {tf.name}!",
                    )

            with console.status(f"Creating Proxmox nodes on {tf.name}"):
                res = tf.apply()

                if res.is_ok():
                    console.success(f"Proxmox nodes created on {tf.name}")
                else:
                    console.panic(
                        f"Proxmox nodes creation failed on {tf.name}",
                        res.message,
                    )

    def generate_talos_config(self):
        with console.status("Generating Talos configuration"):
            res = self.talos.generate_config()

            if res.is_ok():
                console.success("Talos configuration generated")
            else:
                console.panic("Talos configuration generation failed", res.message)

    def configure_talos_nodes(self):
        for node in cfg.nodes:
            with console.status(f"Sending Talos configuration to {node.name}"):
                res = self.talos.configure_node(node)

                if res.is_ok():
                    console.success(f"Talos configuration applied to {node.name}")
                else:
                    console.panic(f"Failed configuring {node.name}", res.message)

    def bootstrap_talos(self):
        with console.status("Waiting for master node configuration"):
            res = self.talos.bootstrap_cluster()

            if res.is_ok():
                console.success("Talos cluster creation requested")
            else:
                console.panic("Failed creating Talos cluster", res.message)

    def get_cluster_config(self):
        with console.status("Waiting for cluster bootstrap"):
            res = self.talos.get_kubeconfig()

            if res.is_ok():
                console.success("Cluster created and kubeconfig retrieved")
                self.k8s = KubernetesAdapter()
                self.flux = FluxAdapter()
            else:
                console.panic("Failed retrieveing cluster's kubeconfig", res.message)

    def wait_for_cni(self):
        with console.status("Waiting for CNI deployment"):
            while True:
                res = self.cilium.wait_for_install()

                if res.is_ok():
                    console.success("CNI is active")
                    return

    def deploy_flux(self):
        with console.status("Deploying Flux"):
            self.flux.refresh_kubeconfig()
            res = self.flux.deploy()

            if res.is_ok():
                console.success("Flux deployed successfully")
            else:
                console.panic("Failed deploying Flux", res.message)
