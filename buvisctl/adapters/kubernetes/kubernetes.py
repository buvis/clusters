import base64
import time

from adapters.response import AdapterResponse
from kubernetes import client, config, dynamic, utils, watch
from kubernetes.client.exceptions import ApiException
from kubernetes.dynamic.exceptions import ResourceNotFoundError


class KubernetesAdapter:
    def __init__(self):
        config.load_kube_config()
        self.api = client.CoreV1Api()
        self.apps_api = client.AppsV1Api()
        self.batch_api = client.BatchV1Api()
        self.client = client.ApiClient()
        self.dynamic_client = dynamic.DynamicClient(self.client)
        self.watch = watch.Watch()

    def is_namespace_active(self, name, timeout=600):
        sleep_count = 0

        while True:
            try:
                namespace_status = self.api.read_namespace_status(name)

                if namespace_status.status.phase == "Active":
                    return AdapterResponse()
                sleep_count = sleep_count + 1

                if sleep_count > timeout / 5:
                    return AdapterResponse(
                        code=504,
                        message=f"Namespace {name} not active",
                    )
            except ApiException as e:
                time.sleep(5)
                sleep_count = sleep_count + 1

                if sleep_count > timeout / 5:
                    return AdapterResponse(code=1, message=e)

    def create_namespace(self, name):
        namespaces = self.api.list_namespace()

        if not any(ns.metadata.name == name for ns in namespaces.items):
            new_namespace = client.V1Namespace(metadata=client.V1ObjectMeta(name=name))
            try:
                self.api.create_namespace(new_namespace)

                return AdapterResponse()
            except ApiException as e:
                return AdapterResponse(code=1, message=e)

        return AdapterResponse()

    def create_config_map_from_file(self, name, namespace, filename):
        try:
            res = self.api.list_namespaced_config_map(namespace)

            if not any(cm.metadata.name == name for cm in res.items):
                config_map_create = True
            else:
                config_map_create = False
        except client.exceptions.ApiException:
            config_map_create = True

        if config_map_create:
            try:
                utils.create_from_yaml(
                    self.client,
                    filename,
                )
            except ApiException as e:
                return AdapterResponse(code=1, message=e)

        return AdapterResponse()

    def apply_manifest(self, filename):
        try:
            utils.create_from_yaml(
                self.client,
                filename,
            )
        except ApiException as e:
            return AdapterResponse(code=1, message=e)

        return AdapterResponse()

    def create_secret(self, name, namespace, data=""):
        try:
            res = self.api.list_namespaced_secret(namespace)

            if not any(s.metadata.name == name for s in res.items):
                create_secret = True
            else:
                create_secret = False
        except client.exceptions.ApiException:
            create_secret = True

        if create_secret:
            if data == "":
                new_secret = client.V1Secret(
                    api_version="v1",
                    kind="Secret",
                    metadata=client.V1ObjectMeta(name=name),
                    type="Opaque",
                )
            else:
                new_secret = client.V1Secret(
                    api_version="v1",
                    kind="Secret",
                    metadata=client.V1ObjectMeta(name=name),
                    type="Opaque",
                    data=data,
                )
            try:
                self.api.create_namespaced_secret(
                    namespace="flux-system", body=new_secret,
                )
            except ApiException as e:
                return AdapterResponse(code=1, message=e)

        return AdapterResponse()

    def encode_secret_data(self, data):
        if data:
            return base64.standard_b64encode(data.encode()).decode()

    def get_config_map_data(self, name, namespace):
        try:
            cms = self.dynamic_client.resources.get(api_version="v1", kind="ConfigMap")
            selected_cm = cms.get(name=name, namespace=namespace)

            return selected_cm.data
        except ApiException:
            return None

    def get_secret_data(self, name, namespace):
        try:
            secret = self.api.read_namespaced_secret(name=name, namespace=namespace)
        except ApiException:
            return None

        return secret.data or {}

    def get_pvc(self, name, namespace):
        try:
            pvcs = self.dynamic_client.resources.get(
                api_version="v1", kind="PersistentVolumeClaim",
            )
            selected_pvc = pvcs.get(name=name, namespace=namespace)

            return selected_pvc
        except ApiException:
            return None

    def get_app_deployment(self, app_name, app_instance, namespace):
        try:
            dps = self.apps_api.list_namespaced_deployment(
                namespace=namespace,
                label_selector=(
                    f"app.kubernetes.io/name={app_name},"
                    f"app.kubernetes.io/instance={app_instance}"
                ),
            )

            return dps
        except ApiException:
            return None

    def get_app_statefulset(self, app_name, app_instance, namespace):
        try:
            sts = self.apps_api.list_namespaced_stateful_set(
                namespace=namespace,
                label_selector=(
                    f"app.kubernetes.io/name={app_name},"
                    f"app.kubernetes.io/instance={app_instance}"
                ),
            )

            return sts
        except ApiException:
            return None

    def get_deployment(self, name, namespace):
        try:
            deployment = self.apps_api.read_namespaced_deployment(name=name, namespace=namespace)
            return deployment
        except ApiException:
            return None

    def get_statefulset(self, name, namespace):
        try:
            statefulset = self.apps_api.read_namespaced_stateful_set(name=name, namespace=namespace)
            return statefulset
        except ApiException:
            return None

    def create_from_file(self, yaml_file):
        utils.create_from_yaml(self.client, yaml_file)

    def scale_stateful_set(self, name, namespace, replicas):
        try:
            self.apps_api.patch_namespaced_stateful_set_scale(
                name,
                namespace,
                [{"op": "replace", "path": "/spec/replicas", "value": replicas}],
            )

            return True
        except ApiException:
            return False

    def scale_deployment(self, name, namespace, replicas):
        try:
            self.apps_api.patch_namespaced_deployment_scale(
                name,
                namespace,
                [{"op": "replace", "path": "/spec/replicas", "value": replicas}],
            )

            return True
        except ApiException:
            return False

    def wait_pod_delete(self, app_instance, app_name, namespace):
        label_selector = (
            f"app.kubernetes.io/name={app_name},"
            f"app.kubernetes.io/instance={app_instance}"
        )
        current_pods = self.api.list_namespaced_pod(
            namespace=namespace, label_selector=label_selector,
        )

        if len(current_pods.items) == 0:
            return True

        for event in self.watch.stream(
            func=self.api.list_namespaced_pod,
            namespace=namespace,
            label_selector=label_selector,
            timeout_seconds=1200,
        ):
            if event["type"] == "DELETED":
                return True

        return False

    def wait_job_complete(self, job_name, namespace):
        for event in self.watch.stream(
            func=self.api.list_namespaced_pod,
            namespace=namespace,
            label_selector=f"job-name={job_name}",
            timeout_seconds=1200,
        ):
            if event["object"].status.phase == "Succeeded":
                return True
            if event["object"].status.phase == "Failed":
                return False

        return False

    def delete_job(self, job_name, namespace):
        try:
            self.batch_api.delete_namespaced_job(
                job_name, namespace, propagation_policy="Background",
            )
        except ApiException:
            pass

    def run_job_from_cronjob(self, cron_job_name, job_name, namespace):
        try:
            cron_job = self.batch_api.read_namespaced_cron_job(cron_job_name, namespace)
        except ApiException as e:
            return AdapterResponse(code=404, message=e)

        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.models.V1ObjectMeta(
                name=job_name,
                annotations={"cronjob.kubernetes.io/instantiate": "manual"},
            ),
            spec=cron_job.spec.job_template.spec,
        )

        try:
            self.batch_api.create_namespaced_job(namespace, job)

            return AdapterResponse()
        except ApiException as e:
            return AdapterResponse(code=1, message=e)

    def get_pod(self, name, namespace):
        try:
            return self.api.read_namespaced_pod(name=name, namespace=namespace)
        except ApiException:
            return None

    def create_pod(self, pod, namespace):
        try:
            self.api.create_namespaced_pod(namespace=namespace, body=pod)
            return AdapterResponse()
        except ApiException as e:
            return AdapterResponse(code=1, message=e)

    def delete_pod(self, name, namespace):
        try:
            self.api.delete_namespaced_pod(name=name, namespace=namespace)
            return AdapterResponse()
        except ApiException as e:
            return AdapterResponse(code=1, message=e)

    def get_pv(self, name):
        try:
            return self.api.read_persistent_volume(name=name)
        except ApiException:
            return None

    def wait_pod_complete(self, name, namespace, timeout=600):
        for event in self.watch.stream(
            func=self.api.list_namespaced_pod,
            namespace=namespace,
            field_selector=f"metadata.name={name}",
            timeout_seconds=timeout,
        ):
            phase = event["object"].status.phase
            if phase == "Succeeded":
                return True
            if phase == "Failed":
                return False

        return False

    def get_pod_logs(self, name, namespace):
        try:
            return self.api.read_namespaced_pod_log(name=name, namespace=namespace)
        except ApiException:
            return None

    def label_node(self, node, label):
        label_name, label_value = label.split(": ")
        body = {"metadata": {"labels": {label_name: label_value}}}
        try:
            self.api.patch_node(node.name, body)
        except ApiException as e:
            return AdapterResponse(code=1, message=e)

        return AdapterResponse()

    def get_degraded_longhorn_volumes(self):
        """Names of Longhorn volumes whose robustness is 'degraded'.

        Detached volumes report robustness 'unknown' (no running consumer) and
        are not degraded, so they are ignored. Returns None when Longhorn is not
        installed, which callers treat as "nothing to wait for".
        """
        try:
            volumes = self.dynamic_client.resources.get(
                api_version="longhorn.io/v1beta2", kind="Volume",
            )
            items = volumes.get().items
        except (ApiException, ResourceNotFoundError):
            return None

        return [
            v.metadata.name
            for v in items
            if v.status and v.status.robustness == "degraded"
        ]

    def wait_longhorn_healthy(self, timeout=1800, interval=15):
        """Block until no Longhorn volume is degraded.

        After a node reboots, its replicas rebuild and the volumes they back
        report 'degraded' until the rebuild finishes. Rebooting the next node
        during that window can drop a volume to its last online replica and
        fault it. Gating on a fully-healed state keeps every volume redundant
        across the rolling upgrade. No-op when Longhorn is absent.
        """
        waited = 0

        while True:
            degraded = self.get_degraded_longhorn_volumes()

            if degraded is None or len(degraded) == 0:
                return AdapterResponse()

            if waited >= timeout:
                return AdapterResponse(
                    code=504,
                    message=(
                        f"{len(degraded)} Longhorn volume(s) still degraded "
                        f"after {timeout}s: {', '.join(sorted(degraded))}"
                    ),
                )

            time.sleep(interval)
            waited += interval
