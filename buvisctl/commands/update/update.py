import os

from adapters import CiliumAdapter, FluxAdapter, TalosAdapter, console


class CommandUpdate:
    def __init__(self):
        pass

    def execute(self, component, version=None):
        if component == "flux":
            self.update_flux()
        elif component == "talos":
            self.update_talos()
        elif component == "cilium":
            if not version:
                console.panic("Cilium version is required: buvisctl update cilium <version>")
            self.update_cilium(version)
        else:
            console.panic(f"I don't know how to update {component}")

    def update_flux(self):
        with console.status("Updating Flux"):
            self.flux = FluxAdapter()
            res = self.flux.bootstrap()

            if res.is_ok():
                console.success("Flux deployed successfully")
            else:
                console.panic("Failed deploying Flux", res.message)

    def update_talos(self):
        self.talos = TalosAdapter()

        with console.status("Updating Talosctl CLI"):
            res = self.talos.update_talosctl()

            if res.is_ok():
                console.success("Latest talosctl CLI downloaded")
            else:
                console.panic("Failed downloading latest talosctl CLI", res.message)

        node_ips = os.getenv("NODE_IPS")

        if not node_ips:
            console.panic(
                "There are no Talos nodes IPs set in NODE_IPS.\nAre you in cluster directory and is direnv enabled?",
            )

        ips = [ip.strip() for ip in node_ips.split(",") if ip.strip()]

        for node_ip in ips:
            with console.status(f"Updating Talos node {node_ip}"):
                res = self.talos.update_node(node_ip)

                if res.is_ok():
                    console.success(res.message)
                else:
                    console.panic(res.message)

    def update_cilium(self, version):
        self.cilium = CiliumAdapter()

        with console.status(f"Rendering Cilium {version} manifests"):
            res = self.cilium.render_manifests(version)

            if res.is_ok():
                console.success(f"Cilium {version} manifests rendered")
            else:
                console.panic("Failed rendering Cilium manifests", res.message)

        with console.status("Embedding manifests in Talos controlplane patch"):
            res = self.cilium.embed_in_talos_patch(version)

            if res.is_ok():
                console.success("Talos controlplane patch updated")
            else:
                console.panic("Failed updating Talos patch", res.message)

        with console.status(f"Applying Cilium {version} to cluster"):
            res = self.cilium.apply_manifests()

            if res.is_ok():
                console.success(f"Cilium {version} applied to cluster")
            else:
                console.panic("Failed applying Cilium manifests", res.message)
