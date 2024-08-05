import os
from pathlib import Path

import yaml
from adapters.console.console import console

from .flux import FluxConfig
from .node import NodeConfig
from .talos import TalosConfig

CONFIG_FILENAME = "buvisctl.conf.yaml"


class ConfigAdapter:
    def __init__(self):
        if not os.path.basename(os.getcwd()).startswith("cluster-"):
            console.panic("You are not in cluster directory (cluster-<name>)!")

        self.path_config_file = Path(CONFIG_FILENAME).absolute()

        if self.path_config_file.is_file():
            with open(self.path_config_file, "r") as file_handle:
                config_file = yaml.safe_load(file_handle)
                self._process_config_file(config_file)
        else:
            console.panic(f"Configuration file {CONFIG_FILENAME} not found!")

        self.cluster_name = os.path.basename(os.getcwd()).replace("cluster-", "buvis-")

    def _process_config_file(self, config_file):
        self.path_terraform_workspaces = config_file.get("terraform_workspaces", "")

        self.nodes = []

        for node in config_file.get("nodes", []):
            self.nodes.append(NodeConfig(node))

        self.ip_master = ""

        for node in self.nodes:
            if node.role == "controlplane":
                self.ip_master = node.ip

        self.flux = FluxConfig(config_file["flux"])
        self.talos = TalosConfig(config_file["talos"])
        self.path_kubeconfig_dir = config_file.get("kubeconfig_dir", "")
        self.path_config_cni = Path(config_file["cilium_cfg"])
        self.path_backup_manifests_dir = config_file.get("backup_manifests_dir", "")


cfg = ConfigAdapter()
