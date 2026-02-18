import json
import os
import platform
import re
import subprocess
from pathlib import Path

import requests
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
        return AdapterResponse(
            code=results.returncode, message=results.stderr.decode(),
        )

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
        return AdapterResponse(
            code=results.returncode, message=results.stderr.decode(),
        )

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
            return AdapterResponse(
                code=results.returncode, message=results.stderr.decode(),
            )

        cmd_node_config = ["talosctl", "config", "node", cfg.ip_master]
        results = subprocess.run(cmd_node_config)

        if results.returncode > 0:
            return AdapterResponse(
                code=results.returncode, message=results.stderr.decode(),
            )

        cmd_bootstrap = ["talosctl", "bootstrap"]
        results = subprocess.run(cmd_bootstrap, capture_output=True)

        if results.returncode > 0:
            return AdapterResponse(
                code=results.returncode, message=results.stderr.decode(),
            )
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
            return AdapterResponse(
                code=results.returncode, message=results.stderr.decode(),
            )
        return AdapterResponse()

    def _get_latest_talos_version(self) -> str:
        """
        Get the latest Talos version from GitHub releases API.

        Returns:
            str: The latest version tag (e.g., 'v1.7.0')

        Raises:
            SystemExit: If unable to fetch version information
        """
        url = "https://github.com/siderolabs/talos/releases/latest"
        headers = {"Accept": "application/json"}

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            return data["tag_name"]
        except (requests.RequestException, KeyError, json.JSONDecodeError):
            return ""

    def _update_talos_version_files(self, talos_version: str) -> None:
        """Update Talos version in .envrc, .envrc.sample, and infrastructure/talos/patch-all.yaml files.

        Args:
            talos_version: The Talos version to set in the files.
        """

        env_files = [".envrc", ".envrc.sample"]
        patch_file = Path("infrastructure/talos/patch-all.yaml")

        # Regex pattern for .envrc and .envrc.sample
        env_pattern = re.compile(r"^export TF_VAR_talos_version=.*$", re.MULTILINE)
        env_replacement = f"export TF_VAR_talos_version={talos_version}"

        for env_file in env_files:
            file_path = Path(env_file)

            if not file_path.exists():
                continue
            content = file_path.read_text(encoding="utf-8")

            if env_pattern.search(content):
                updated_content = env_pattern.sub(env_replacement, content)
                file_path.write_text(updated_content, encoding="utf-8")
            else:
                updated_content = content.rstrip() + f"\n{env_replacement}\n"
                file_path.write_text(updated_content, encoding="utf-8")

        if patch_file.exists():
            patch_content = patch_file.read_text(encoding="utf-8")
            # Regex to find the line with the image version and replace only the version part after colon
            patch_pattern = re.compile(
                r"(image: factory\.talos\.dev/metal-installer/[a-f0-9]+:)(v[\d\.]+)",
            )
            updated_patch_content = patch_pattern.sub(
                lambda m: m.group(1) + talos_version, patch_content,
            )
            patch_file.write_text(updated_patch_content, encoding="utf-8")

    def update_talosctl(self):
        talos_version = self._get_latest_talos_version()

        if not talos_version:
            return AdapterResponse(
                code=1,
                message="Couldn't get the latest Talos version tag from GitHub",
            )

        os_name = platform.system().lower()
        download_url = (
            f"https://github.com/siderolabs/talos/releases/download/"
            f"{talos_version}/talosctl-{os_name}-amd64"
        )

        bin_dir = Path.home() / ".local" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)

        talosctl_path = bin_dir / "talosctl"

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "application/octet-stream,*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

        try:
            with requests.get(
                download_url,
                headers=headers,
                stream=True,
                timeout=30,
            ) as response:
                response.raise_for_status()

                with talosctl_path.open("wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            talosctl_path.chmod(0o755)
            self._update_talos_version_files(talos_version)

            return AdapterResponse()

        except requests.RequestException as e:
            return AdapterResponse(
                code=1,
                message=f"Error downloading talosctl: {e}",
            )

    def update_node(self, node_ip):
        talos_version = self._get_latest_talos_version()

        if not talos_version:
            return AdapterResponse(
                code=1,
                message="Couldn't get the latest Talos version tag from GitHub",
            )

        schematic_id = os.getenv("TF_VAR_talos_schematic_id")

        if not schematic_id:
            return AdapterResponse(
                code=1,
                message="TF_VAR_talos_schematic_id environment variable is not set",
            )

        cmd = [
            "talosctl",
            "upgrade",
            "--nodes",
            node_ip,
            "--image",
            f"factory.talos.dev/installer/{schematic_id}:{talos_version}",
            "--preserve",
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)

            return AdapterResponse(
                code=0,
                message=f"Node {node_ip} upgrade to Talos {talos_version} successful",
            )
        except subprocess.CalledProcessError as e:
            return AdapterResponse(
                code=1,
                message=f"Error upgrading node {node_ip}:\n{e.stderr.strip()}",
            )
        except FileNotFoundError:
            return AdapterResponse(code=1, message="talosctl command not found")
