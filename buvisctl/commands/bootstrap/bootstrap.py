import base64
import os
import subprocess

from kubernetes import client, config, utils
from terrapyst import TerraformWorkspace

from .wait_for_connection import wait_for_connection
from .wait_for_namespace import wait_for_namespace

DIR_TERRAFORM = "/infrastructure/terraform"


class CommandBootstrap:

    def __init__(self):
        self.tf = TerraformWorkspace(path=f"{os.getcwd()}{DIR_TERRAFORM}")

    def execute(self):
        self.infra_create()
        self.generate_talos_config()
        self.configure_talos_nodes()
        self.bootstrap_talos()
        self.get_cluster_config()
        self.wait_for_cni()
        self.deploy_flux()

    def infra_create(self):
        self.tf.init()
        print("Started creating VMs.")
        results, _ = self.tf.apply(auto_approve=True)

        if not results.successful:
            print(
                f"Failed creating VMs creation failed. \n\n {results.stdout}")
        else:
            print("Finished creating VMs.")

    def generate_talos_config(self):
        cluster_name = os.path.basename(os.getcwd()).replace(
            "cluster-", "buvis-")
        cmd = [
            "talosctl",
            "gen",
            "config",
            cluster_name,
            f"https://{os.getenv('MASTER1_IP')}:6443",
            "--output-dir",
            "infrastructure/talos/generated-config",
            "--config-patch",
            "@infrastructure/talos/patch-all.yaml",
            "--config-patch-control-plane",
            "@infrastructure/talos/patch-controlplane.yaml",
        ]
        result = subprocess.run(cmd, capture_output=True)

        if result.returncode > 0:
            print(
                f"Failed talos configuration generation. \n\n {result.stderr}")
        else:
            print("Generated talos configuration.")

    def configure_talos_nodes(self):
        # TODO: work with some inventory file
        self.configure_talos_node("higgs-master-1", os.getenv("MASTER1_IP"),
                                  50000, "controlplane")
        self.configure_talos_node("higgs-worker-1", os.getenv("WORKER2_IP"),
                                  50000, "worker")
        self.configure_talos_node("higgs-worker-2", os.getenv("WORKER3_IP"),
                                  50000, "worker")
        self.configure_talos_node("higgs-worker-3", os.getenv("WORKER4_IP"),
                                  50000, "worker")

    def configure_talos_node(self, hostname, ip, port, type):
        print(f"Waiting for {hostname} to get ready.")
        is_connected = wait_for_connection(ip, port)

        if is_connected:
            self.apply_talos_config(hostname, ip, type)
        else:
            print(f"Unable to connect {hostname}. Check it via Proxmox UI.")

    def apply_talos_config(self, hostname, ip, type):
        cmd = [
            "talosctl",
            "apply-config",
            "--insecure",
            "--nodes",
            ip,
            "--file",
            f"infrastructure/talos/generated-config/{type}.yaml",
        ]
        result = subprocess.run(cmd, capture_output=True)

        if result.returncode > 0:
            print(f"Failed {hostname} configuration. \n\n {result.stderr}")
        else:
            print(f"Pushed Talos configuration to {hostname}.")

    def bootstrap_talos(self):
        print("Waiting for master node to finish Talos configuration.")
        is_connected = wait_for_connection(os.getenv("MASTER1_IP"), 50001)

        if is_connected:
            cmd_endpoint_config = [
                "talosctl",
                "config",
                "endpoint",
                os.getenv("MASTER1_IP"),
            ]
            subprocess.run(cmd_endpoint_config)
            # TODO: this can fail if talosconfig file not found (check
            # TALOSCONFIG env variable)
            cmd_node_config = [
                "talosctl", "config", "node",
                os.getenv("MASTER1_IP")
            ]
            subprocess.run(cmd_node_config)
            cmd_bootstrap = ["talosctl", "bootstrap"]
            result = subprocess.run(cmd_bootstrap, capture_output=True)

            if result.returncode > 0:
                print(
                    f"Failed initiating cluster bootstrap. \n\n {result.stderr}"
                )
            else:
                print("Started cluster bootstrap.")
        else:
            print(
                "Failed initiating cluster bootstrap as master node isn't ready. Check it in Proxmox UI.."
            )

    def get_cluster_config(self):
        print("Waiting for Kubernetes API to be ready.")
        is_connected = wait_for_connection(os.getenv("MASTER1_IP"), 6443)

        if is_connected:
            cmd_get_config = [
                "talosctl",
                "kubeconfig",
                "infrastructure/.kube",
                "--force",
            ]
            result = subprocess.run(cmd_get_config, capture_output=True)

            if result.returncode > 0:
                print(f"""Failed retrieving cluster configuration.
                    \n {result.stderr}""")
            else:
                print("Retrieved cluster connection details.")
                config.load_kube_config()
                self.api = client.CoreV1Api()
                self.client = client.ApiClient()
        else:
            print(
                "Failed connecting to Kubernetes API. Check master node logs in Proxmox UI."
            )

    def wait_for_cni(self):
        if wait_for_namespace(self.api, "tigera-operator"):

            if wait_for_namespace(self.api, "calico-system"):
                print("CNI is ready.")
            else:
                print("CNI failed to deploy.")
        else:
            print("Namespace tigera-operator isn't ready.")

    def deploy_flux(self):
        print("Started Flux deployment.")
        namespaces = self.api.list_namespace()

        if not any(ns.metadata.name == "flux-system"
                   for ns in namespaces.items):
            namespace_flux_system = client.V1Namespace(
                metadata=client.V1ObjectMeta(name="flux-system"))
            self.api.create_namespace(namespace_flux_system)

        try:
            res = self.api.list_namespaced_config_map("flux-system")

            if not any(cm.metadata.name == "cluster-config"
                       for cm in res.items):
                utils.create_from_yaml(
                    self.client,
                    "operations/flux-system/extras/cluster-config.yaml",
                )
        except client.exceptions.ApiException:
            utils.create_from_yaml(
                self.client,
                "operations/flux-system/extras/cluster-config.yaml",
            )

        try:
            res = self.api.list_namespaced_secret("flux-system")

            if not any(s.metadata.name == "cluster-secret-vars"
                       for s in res.items):
                cluster_secret_vars = client.V1Secret(
                    api_version="v1",
                    kind="Secret",
                    metadata=client.V1ObjectMeta(name="cluster-secret-vars"),
                )
                self.api.create_namespaced_secret(namespace="flux-system",
                                                  body=cluster_secret_vars)
        except client.exceptions.ApiException:
            cluster_secret_vars = client.V1Secret(
                api_version="v1",
                kind="Secret",
                metadata=client.V1ObjectMeta(name="cluster-secret-vars"),
            )
            self.api.create_namespaced_secret(namespace="flux-system",
                                              body=cluster_secret_vars)

        try:
            res = self.api.list_namespaced_secret("flux-system")

            if not any(s.metadata.name == "sops-gpg" for s in res.items):
                create_sops_key = True
            else:
                create_sops_key = False
        except client.exceptions.ApiException:
            create_sops_key = True

        if create_sops_key:

            sops_key_export_cmd = [
                "gpg",
                "--export-secret-keys",
                "--armor",
                os.getenv("SOPS_KEY_FINGERPRINT"),
            ]
            sops_key_export = subprocess.run(sops_key_export_cmd,
                                             capture_output=True)
            sops_key = sops_key_export.stdout.decode()

            sops_key = client.V1Secret(
                api_version="v1",
                kind="Secret",
                metadata=client.V1ObjectMeta(name="sops-gpg"),
                data={
                    "sops.asc":
                    base64.standard_b64encode(sops_key.encode()).decode()
                },
                type="Opaque",
            )

            self.api.create_namespaced_secret(namespace="flux-system",
                                              body=sops_key)
        try:
            res = self.api.list_namespaced_secret("flux-system")

            if not any(s.metadata.name == "slack-url" for s in res.items):
                create_slack_url = True
            else:
                create_slack_url = False
        except client.exceptions.ApiException:
            create_slack_url = True

        if create_slack_url:
            slack_url = client.V1Secret(
                api_version="v1",
                kind="Secret",
                metadata=client.V1ObjectMeta(name="slack-url"),
                data={
                    "address":
                    base64.standard_b64encode(
                        os.getenv("SLACK_WEBHOOK_URL").encode()).decode()
                },
                type="Opaque",
            )
            self.api.create_namespaced_secret(namespace="flux-system",
                                              body=slack_url)

        flux_bootstrap_command = [
            "flux",
            "bootstrap",
            "github",
            "--owner=buvis",
            "--repository=clusters",
            f"--path=./{os.path.basename(os.getcwd())}/operations",
            "--branch=main",
            "--personal",
        ]
        flux_bootstrap = subprocess.run(flux_bootstrap_command,
                                        capture_output=True)
        print(flux_bootstrap.stderr.decode())
