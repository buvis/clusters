from pathlib import Path

from adapters import KubernetesAdapter, cfg, console
from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader("commands", "generate"))
backup_job_template = env.get_template("backup-job-template.j2")


class CommandGenerate:

    def __init__(self):
        self.k8s = KubernetesAdapter()

    def execute(self, kind, name, namespace):
        if kind == "backup-job":
            self._generate_backup_job(name, namespace)

    def _generate_backup_job(self, pvc, namespace):
        job_name = f"{namespace}-{pvc}-snapshot"
        app_instance, app_name = self._get_app_labels_from_pvc(pvc, namespace)

        console.success(f"Gathered all information needed to create "
                        f" backup job for {pvc}")

        with console.status(f"Generating {pvc} backup job manifest"):
            manifest_path = Path(cfg.path_backup_manifests_dir,
                                 f"{job_name}.yaml")
            self._generate_backup_job_manifest(
                {
                    "JOBNAME": job_name,
                    "NAMESPACE": namespace,
                    "PVC": pvc,
                    "APP_INSTANCE": app_instance,
                    "APP_NAME": app_name,
                },
                manifest_path,
            )

            console.success(f"Generated {pvc} backup job manifest")

    def _get_app_labels_from_pvc(self, pvc, namespace):
        pvc_resource = self.k8s.get_pvc(pvc, namespace)

        if pvc_resource is None:
            console.panic(f"PVC {pvc} doesn't exist in {namespace} namespace")

        app_instance = pvc_resource.metadata.labels.get(
            "app.kubernetes.io/instance", "")
        app_name = pvc_resource.metadata.labels.get("app.kubernetes.io/name",
                                                    "")

        if not (app_instance and app_name):
            console.panic("Can't determine application name from PVC. "
                          "Please add app.kubernetes.io/name and "
                          "app.kubernetes.io/instance labels to it.")

        return (app_instance, app_name)

    def _generate_backup_job_manifest(self, template_vars, manifest_path):
        with open(manifest_path, "w") as backup_job_manifest:
            backup_job_manifest.write(
                backup_job_template.render(template_vars))
