import subprocess

import yaml
from adapters.config.config import cfg
from adapters.response import AdapterResponse


CILIUM_OCI_CHART = "oci://quay.io/cilium/charts/cilium"


class _LiteralDumper(yaml.Dumper):
    pass


def _literal_representer(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_LiteralDumper.add_representer(str, _literal_representer)


class CiliumAdapter:
    def __init__(self):
        pass

    def wait_for_install(self):
        cmd = [
            "kubectl",
            "rollout",
            "status",
            "daemonset/cilium",
            "-n",
            "kube-system",
            "--timeout=15m",
        ]

        results = subprocess.run(cmd, capture_output=True)

        if results.returncode == 0:
            return AdapterResponse()
        else:
            return AdapterResponse(
                code=results.returncode, message=results.stderr.decode()
            )

    def render_manifests(self, version):
        cmd = [
            "helm",
            "template",
            "cilium",
            CILIUM_OCI_CHART,
            "--version",
            version,
            "--namespace",
            "kube-system",
            "-f",
            str(cfg.cilium.path_values),
        ]

        results = subprocess.run(cmd, capture_output=True, text=True)

        if results.returncode != 0:
            return AdapterResponse(code=results.returncode, message=results.stderr)

        output = results.stdout
        first_doc = output.find("---")
        if first_doc > 0:
            output = output[first_doc:]

        lines = [line.rstrip() for line in output.splitlines()]
        self._manifests = "\n".join(lines) + "\n"
        return AdapterResponse()

    def embed_in_talos_patch(self, version):
        patch_path = cfg.talos.path_patch_controlplane

        with open(patch_path, "r") as f:
            patch = yaml.safe_load(f)

        patch.setdefault("cluster", {})["inlineManifests"] = [
            {
                "name": "cilium",
                "contents": self._manifests,
            }
        ]

        with open(patch_path, "w") as f:
            yaml.dump(
                patch,
                f,
                Dumper=_LiteralDumper,
                default_flow_style=False,
                sort_keys=False,
                width=10000,
            )

        self._update_upgrade_compatibility(version)
        return AdapterResponse()

    def apply_manifests(self):
        cmd = [
            "kubectl",
            "apply",
            "--server-side",
            "--force-conflicts",
            "-f",
            "-",
        ]

        results = subprocess.run(
            cmd, input=self._manifests, capture_output=True, text=True,
        )

        if results.returncode != 0:
            return AdapterResponse(code=results.returncode, message=results.stderr)

        return AdapterResponse()

    def _update_upgrade_compatibility(self, version):
        major_minor = ".".join(version.split(".")[:2])
        values_path = cfg.cilium.path_values

        with open(values_path, "r") as f:
            values = yaml.safe_load(f)

        values["upgradeCompatibility"] = major_minor

        with open(values_path, "w") as f:
            yaml.dump(values, f, default_flow_style=False, sort_keys=False)
