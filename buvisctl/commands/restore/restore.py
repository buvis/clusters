import os
import time

from adapters import FluxAdapter, KubernetesAdapter, console
from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader("commands", "restore"))
job_template = env.get_template("restore-job-template.j2")


class CommandRestore:
    def __init__(self):
        self.k8s = KubernetesAdapter()
        self.flux = FluxAdapter()

    def execute(self, pvc, namespace, snapshot=""):
        job_name = f"{namespace}-{pvc}-restore-snapshot"
        app_instance, app_name = self._get_app_labels_from_pvc(pvc, namespace)
        nfs_server_ip, nfs_server_path = self._get_nfs_backup_location()

        if snapshot == "":
            restore_command = "restore --snapshot-time latest"
        else:
            restore_command = f"snap restore {snapshot}"

        self.k8s.delete_job(job_name, namespace)
        self._generate_restore_job_manifest(
            {
                "NFS_SERVER_IP": nfs_server_ip,
                "NFS_SERVER_PATH_KOPIA": f"{nfs_server_path}/storage/kopia",
                "JOBNAME": job_name,
                "NAMESPACE": namespace,
                "PVC": pvc,
                "RESTORE_COMMAND": restore_command,
            }
        )
        console.success(f"Gathered all information needed to restore {pvc}")
        res = self.flux.suspend_hr(app_instance, namespace)

        if res.is_ok():
            console.success(f"Suspended {app_instance} helmrelease")

        self._stop_application(app_instance, app_name, namespace)
        self._submit_restore_job(pvc, namespace, job_name)

        with console.status(f"Resuming {app_instance} helmrelease"):
            res = self.flux.resume_hr(app_instance, namespace)

            if res.is_ok():
                console.success(f"Resumed {app_instance} helmrelease")
            else:
                console.panic(
                    f"Can't resume {app_instance} helmrelease. "
                    f"Run `kubectl describe hr -n {namespace} {app_instance}`"
                )
        self._start_application(namespace)


    def _get_app_labels_from_pvc(self, pvc, namespace):
        pvc_resource = self.k8s.get_pvc(pvc, namespace)

        if pvc_resource is None:
            console.panic(f"PVC {pvc} doesn't exist in {namespace} namespace")

        app_instance = pvc_resource.metadata.labels.get(
            "app.kubernetes.io/instance", ""
        )
        app_name = pvc_resource.metadata.labels.get("app.kubernetes.io/name", "")

        if not (app_instance and app_name):
            console.panic(
                "Can't determine application name from PVC. "
                "Please add app.kubernetes.io/name and "
                "app.kubernetes.io/instance labels to it."
            )

        return (app_instance, app_name)

    def _get_nfs_backup_location(self):
        cluster_config = self.k8s.get_config_map_data("cluster-config", "flux-system")

        if cluster_config is None:
            console.panic("Can't determine backups location")

        nfs_server_ip = cluster_config.get("FAST_NAS_SERVER_IP", "")
        nfs_server_path = cluster_config.get("FAST_NAS_PATH_PV", "")

        if not (nfs_server_ip and nfs_server_path):
            console.panic("Can't determine backups location")

        return (nfs_server_ip, nfs_server_path)

    def _generate_restore_job_manifest(self, template_vars):
        with open(template_vars["JOBNAME"], "w") as restore_job_manifest:
            restore_job_manifest.write(job_template.render(template_vars))

        stopped_apps = {}

    def _stop_application(self, app_instance, app_name, namespace):
        with console.status(f"Stopping {app_instance}-{app_name} application"):
            res = self.flux.stop_application(app_instance, app_name, namespace)

            manual_stop_required = False

            if res.is_ok():
                self.stopped_apps = res.message
                if self.k8s.wait_pod_delete(app_instance, app_name, namespace):
                    console.success(f"Stopped {app_instance}-{app_name} application")
                else:
                    manual_stop_required = True
            else:
                manual_stop_required = True

        if manual_stop_required:
            console.failure(
                f"Can't stop application {app_instance}-{app_name} application"
            )
            manual_stop = console.confirm(
                f"Can you stop {app_instance}-{app_name} application, please?"
            )

            if not manual_stop:
                console.panic(
                    "It isn't safe to proceed with restore while "
                    "application is running"
                )

    def _start_application(self, namespace):
        with console.status(f"Starting application"):
            res = self.flux.start_application(
                namespace, self.stopped_apps
            )

            if res.is_ok():
                console.success(f"Started application")
            else:
                console.failure(
                    f"Can't start application"
                )

    def _submit_restore_job(self, pvc, namespace, job_name):
        with console.status(f"Restoring {pvc} data"):
            self.k8s.create_from_file(job_name)
            time.sleep(5)

            if self.k8s.wait_job_complete(job_name, namespace):
                console.success(f"Restored {pvc} data")
            else:
                console.failure(f"Couldn't restore {pvc} data")

        os.remove(job_name)
