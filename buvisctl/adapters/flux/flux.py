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
            {
                "address": self.k8s.encode_secret_data(
                    cfg.flux.url_slack_webhook)
            },
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
            return AdapterResponse(code=results.returncode,
                                   message=results.stderr.decode())
