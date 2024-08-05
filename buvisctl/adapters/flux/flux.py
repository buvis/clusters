import subprocess

from adapters.config.config import cfg
from adapters.gpg.gpg import GPGAdapter
from adapters.kubernetes.kubernetes import KubernetesAdapter
from adapters.response import AdapterResponse


class FluxAdapter:
    def __init__(self):
        self.k8s = KubernetesAdapter()
        self.gpg = GPGAdapter()

    def refresh_kubeconfig(self):
        self.k8s = KubernetesAdapter()

    def deploy(self):
        res = self.k8s.create_namespace("flux-system")

        if res.is_nok():
            return AdapterResponse(res.code, res.message)

        res = self.k8s.create_config_map_from_file(
            "cluster-config",
            "flux-system",
            cfg.flux.path_cluster_config,
        )

        if res.is_nok():
            return AdapterResponse(res.code, res.message)

        res = self.k8s.create_secret("cluster-secret-vars", "flux-system")

        if res.is_nok():
            return AdapterResponse(res.code, res.message)

        sops_key = self.gpg.export_secret_key(cfg.flux.sops_key_fingerprint)

        res = self.k8s.create_secret(
            "sops-gpg",
            "flux-system",
            {"sops.asc": self.k8s.encode_secret_data(sops_key)},
        )

        if res.is_nok():
            return AdapterResponse(res.code, res.message)

        res = self.k8s.create_secret(
            "slack-url",
            "flux-system",
            {"address": self.k8s.encode_secret_data(cfg.flux.url_slack_webhook)},
        )

        if res.is_nok():
            return AdapterResponse(res.code, res.message)

        return self.bootstrap()

    def bootstrap(self):
        flux_bootstrap_command = [
            "flux",
            "bootstrap",
            "github",
            f"--owner={cfg.flux.repository_owner}",
            f"--repository={cfg.flux.repository_name}",
            f"--path={cfg.flux.path_manifests_dir}",
            f"--branch={cfg.flux.repository_branch}",
            "--personal",
        ]
        results = subprocess.run(flux_bootstrap_command, capture_output=True)

        if results.returncode == 0:
            return AdapterResponse()
        else:
            return AdapterResponse(
                code=results.returncode, message=results.stderr.decode()
            )

    def suspend_hr(self, name, namespace):
        flux_suspend_command = ["flux", "suspend", "hr", "-n", namespace, name]
        results = subprocess.run(flux_suspend_command, capture_output=True)

        if results.stderr.decode().startswith("✗ no HelmRelease objects found"):
            return AdapterResponse(
                code=404,
                message=f"helmrelease {name} not in {namespace} namespace",
            )
        else:
            return AdapterResponse()

    def resume_hr(self, name, namespace):
        flux_resume_command = ["flux", "resume", "hr", "-n", namespace, name]
        results = subprocess.run(flux_resume_command, capture_output=True)

        if results.stderr.decode().startswith("✗ no HelmRelease objects found"):
            return AdapterResponse(
                code=404,
                message=f"helmrelease {name} not in {namespace} namespace",
            )
        else:
            return AdapterResponse()

    def stop_application(self, app_instance, app_name, namespace):
        app_stopped = False
        # TODO: I need to keep track of everything stopped for later starts
        deployments = self.k8s.get_app_deployment(app_name, app_instance, namespace)

        for d in deployments.items:
            res = self.k8s.scale_deployment_to_zero(d.metadata.name, namespace)

            if res:
                app_stopped = True

        stateful_sets = self.k8s.get_app_statefulset(app_name, app_instance, namespace)

        for s in stateful_sets.items:
            res = self.k8s.scale_stateful_set_to_zero(s.metadata.name, namespace)

            if res:
                app_stopped = True

        if app_stopped:
            return AdapterResponse()
        else:
            return AdapterResponse(
                code=1, message=f"Couldn't stop {app_instance}-{app_name} application"
            )
