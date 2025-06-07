import os
from platform import node

from adapters import FluxAdapter, TalosAdapter, console


class CommandUpdate:
    def __init__(self):
        pass

    def execute(self, component):
        if component == "flux":
            self.update_flux()
        elif component == "talos":
            self.update_talos()
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
                "There are no Talos nodes IPs set in NODE_IPS.\nAre you in cluster directory and is direnv enabled?"
            )

        ips = [ip.strip() for ip in node_ips.split(",") if ip.strip()]

        for node_ip in ips:
            with console.status(f"Updating Talos node {node_ip}"):
                res = self.talos.update_node(node_ip)

                if res.is_ok():
                    console.success(res.message)
                else:
                    console.panic(res.message)
