import time

from adapters import KubernetesAdapter, console


class CommandBackup:

    def __init__(self):
        self.k8s = KubernetesAdapter()

    def execute(self, pvc, namespace):
        cron_job_name = f"{namespace}-{pvc}-snapshot"
        current_time = time.localtime()
        current_time_string = time.strftime("%Y%m%d%H%M%S", current_time)
        job_name = f"{namespace}-{pvc}-manual-snapshot-{current_time_string}"

        res = self.k8s.run_job_from_cronjob(cron_job_name, job_name, namespace)

        if res.is_ok():
            console.success(f"Started backup job {job_name}")
        else:
            console.panic(
                f"Failed starting job {job_name}. Details: {res.message}")
