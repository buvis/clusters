import subprocess

from adapters.config.config import cfg
from adapters.response import AdapterResponse
from adapters.socket.socket import SocketAdapter

PORT_TALOS_INIT = 50000
PORT_TALOS_API = 50001
PORT_K8S_API = 6443


class TalosAdapter:

    def __init__(self):
        self.socket = SocketAdapter()

    def generate_config(self):
        cmd = [
            "talosctl",
            "gen",
            "config",
            cfg.cluster_name,
            f"https://{cfg.ip_master}:{PORT_K8S_API}",
            "--force",
            "--output-dir",
            f"{cfg.talos.dir_generated_configuration}",
            "--config-patch",
            f"@{cfg.talos.path_patch_all}",
            "--config-patch-control-plane",
            f"@{cfg.talos.path_patch_controlplane}",
            "--config-patch-worker",
            f"@{cfg.talos.path_patch_worker}",
        ]

        results = subprocess.run(cmd, capture_output=True)

        if results.returncode == 0:
            return AdapterResponse()
        else:
            return AdapterResponse(code=results.returncode,
                                   message=results.stderr.decode())

    def configure_node(self, node):
        res = self.socket.is_open(node.ip, PORT_TALOS_INIT)

        if res.is_nok():
            return AdapterResponse(code=res.code, message=res.message)

        cmd = [
            "talosctl",
            "apply-config",
            "--insecure",
            "--nodes",
            node.ip,
            "--file",
            f"{cfg.talos.dir_generated_configuration}/{node.role}.yaml",
        ]
        results = subprocess.run(cmd, capture_output=True)

        if results.returncode == 0:
            return AdapterResponse()
        else:
            return AdapterResponse(code=results.returncode,
                                   message=results.stderr.decode())

    def bootstrap_cluster(self):
        res = self.socket.is_open(cfg.ip_master, PORT_TALOS_API)

        if res.is_nok():
            return AdapterResponse(code=res.code, message=res.message)

        cmd_endpoint_config = [
            "talosctl",
            "config",
            "endpoint",
            cfg.ip_master,
        ]
        results = subprocess.run(cmd_endpoint_config)

        if results.returncode > 0:
            return AdapterResponse(code=results.returncode,
                                   message=results.stderr.decode())

        cmd_node_config = ["talosctl", "config", "node", cfg.ip_master]
        results = subprocess.run(cmd_node_config)

        if results.returncode > 0:
            return AdapterResponse(code=results.returncode,
                                   message=results.stderr.decode())

        cmd_bootstrap = ["talosctl", "bootstrap"]
        results = subprocess.run(cmd_bootstrap, capture_output=True)

        if results.returncode > 0:
            return AdapterResponse(code=results.returncode,
                                   message=results.stderr.decode())
        else:
            return AdapterResponse()

    def get_kubeconfig(self):
        res = self.socket.is_open(cfg.ip_master, PORT_K8S_API)

        if res.is_nok():
            return AdapterResponse(code=res.code, message=res.message)

        cmd_get_config = [
            "talosctl",
            "kubeconfig",
            cfg.path_kubeconfig_dir,
            "--force",
        ]
        results = subprocess.run(cmd_get_config, capture_output=True)

        if results.returncode > 0:
            return AdapterResponse(code=results.returncode,
                                   message=results.stderr.decode())
        else:
            return AdapterResponse()
