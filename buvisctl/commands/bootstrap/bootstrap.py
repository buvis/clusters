import os
import subprocess

from kubernetes import client, config, watch
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
        print(f"Waiting for {hostname} to be up.")
        is_connected = wait_for_connection(ip, port)

        if is_connected:
            print(f"Configure {hostname}.")
            self.apply_talos_config(hostname, ip, type)
        else:
            print(f"Unable to connect {hostname} node.")

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
            print(f"Applied configuration to {hostname}.")

    def bootstrap_talos(self):
        print("Wait for master node.")
        is_connected = wait_for_connection(os.getenv("MASTER1_IP"), 50001)

        if is_connected:
            print("Bootstrap talos cluster.")
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
                print(f"Failed cluster bootstrap. \n\n {result.stderr}")
            else:
                print("Cluster bootstrap successful.")
        else:
            print("Unable to bootstrap talos cluster.")

    def get_cluster_config(self):
        print("Wait for Kubernetes API to be ready.")
        is_connected = wait_for_connection(os.getenv("MASTER1_IP"), 6443)

        if is_connected:
            print("Get cluster configuration")
            cmd_get_config = [
                "talosctl",
                "kubeconfig",
                "infrastructure/.kube",
                "--force",
            ]
            result = subprocess.run(cmd_get_config, capture_output=True)

            if result.returncode > 0:
                print(
                    f"Failed retrieving cluster configuration. \n\n {result.stderr}"
                )
            else:
                print("Cluster configuration retrieved.")
                config.load_kube_config()
                self.api = client.CoreV1Api()
        else:
            print("Unable to connect Kubernetes API.")

    def wait_for_cni(self):
        if wait_for_namespace(self.api, "tigera-operator"):

            if wait_for_namespace(self.api, "calico-system"):
                print("CNI is ready.")
            else:
                print("CNI failed to deploy.")
        else:
            print("Namespace tigera-operator isn't ready.")

    def deploy_flux(self):
        print("Ready to deploy Flux")
        pass
