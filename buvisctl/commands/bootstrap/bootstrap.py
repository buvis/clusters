from adapters import (FluxAdapter, KubernetesAdapter, SocketAdapter,
                      TalosAdapter, TerraformAdapter, cfg, console)


class CommandBootstrap:

    def __init__(self):
        self.socket = SocketAdapter()
        self.tf = TerraformAdapter()
        self.talos = TalosAdapter()
        self.k8s = KubernetesAdapter()
        self.flux = FluxAdapter()

    def execute(self):
        self.infra_create()
        self.generate_talos_config()
        self.configure_talos_nodes()
        self.bootstrap_talos()
        self.get_cluster_config()
        self.wait_for_cni()
        self.deploy_flux()

    def infra_create(self):
        res = self.tf.init()

        if res.is_nok():
            console.panic("Terraform initialization failed!")

        with console.status("Creating Proxmox nodes"):
            res = self.tf.apply()

            if res.is_ok():
                console.success("Proxmos nodes created")
            else:
                console.panic("Proxmox nodes creation failed", res.message)

    def generate_talos_config(self):
        with console.status("Generating Talos configuration"):
            res = self.talos.generate_config()

            if res.is_ok():
                console.success("Talos configuration generated")
            else:
                console.panic("Talos configuration generation failed",
                                res.message)

    def configure_talos_nodes(self):
        for node in cfg.nodes:
            with console.status(
                    f"Sending Talos configuration to {node.name}"):
                res = self.talos.configure_node(node)

                if res.is_ok():
                    console.success(
                        f"Talos configuration applied to {node.name}")
                else:
                    console.panic(f"Failed configuring {node.name}",
                                    res.message)

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
            else:
                console.panic("Failed retrieveing cluster's kubeconfig",
                                res.message)

    def wait_for_cni(self):
        with console.status("Waiting for CNI deployment"):
            res = self.k8s.is_namespace_active("tigera-operator")

            if res.is_ok():
                console.success("Namespace tigera-operator is active")
            else:
                console.panic("CNI deployment failed", res.message)

            res = self.k8s.is_namespace_active("calico-system")

            if res.is_ok():
                console.success("Namespace calico-system is active")
            else:
                console.panic("CNI deployment failed", res.message)

        console.success("CNI deployed")

    def deploy_flux(self):
        with console.status("Deploying Flux"):
            self.flux.refresh_kubeconfig()
            res = self.flux.deploy()

            if res.is_ok():
                console.success("Flux deployed successfully")
            else:
                console.panic("Failed deploying Flux", res.message)
