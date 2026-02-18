from kubernetes import client

from adapters import KubernetesAdapter, console


class CommandFsck:

    def __init__(self):
        self.k8s = KubernetesAdapter()

    def execute(self, pod_name, namespace):
        pod = self.k8s.get_pod(pod_name, namespace)

        if pod is None:
            console.panic(f"Pod {pod_name} not found in namespace {namespace}")

        node_name = pod.spec.node_name
        pvc_names = self._get_pvc_names(pod)

        if not pvc_names:
            console.panic(f"Pod {pod_name} has no PVCs")

        device_paths = self._get_device_paths(pvc_names, namespace)

        if not device_paths:
            console.panic(f"No Longhorn device paths found for {pod_name}")

        for device_path in device_paths:
            self._run_fsck(device_path, node_name, namespace)

        res = self.k8s.delete_pod(pod_name, namespace)

        if res.is_ok():
            console.success(f"Deleted pod {pod_name} to trigger restart")
        else:
            console.failure(f"Failed to delete pod {pod_name}", details=str(res.message))

    def _get_pvc_names(self, pod):
        pvc_names = []

        for volume in pod.spec.volumes or []:
            if volume.persistent_volume_claim:
                pvc_names.append(volume.persistent_volume_claim.claim_name)

        return pvc_names

    def _get_device_paths(self, pvc_names, namespace):
        device_paths = []

        for pvc_name in pvc_names:
            pvc = self.k8s.get_pvc(pvc_name, namespace)

            if pvc is None:
                console.failure(f"PVC {pvc_name} not found")
                continue

            pv_name = pvc.spec.volumeName

            if not pv_name:
                console.failure(f"PVC {pvc_name} has no bound PV")
                continue

            device_paths.append(f"/dev/longhorn/{pv_name}")

        return device_paths

    def _run_fsck(self, device_path, node_name, namespace):
        fsck_pod_name = f"fsck-{device_path.split('/')[-1][:48]}"

        fsck_pod = client.V1Pod(
            api_version="v1",
            kind="Pod",
            metadata=client.V1ObjectMeta(name=fsck_pod_name),
            spec=client.V1PodSpec(
                restart_policy="Never",
                node_selector={"kubernetes.io/hostname": node_name},
                containers=[
                    client.V1Container(
                        name="fsck",
                        image="alpine:latest",
                        command=["fsck", "-y", device_path],
                        security_context=client.V1SecurityContext(privileged=True),
                        volume_mounts=[
                            client.V1VolumeMount(
                                name="dev",
                                mount_path="/dev",
                            ),
                        ],
                    ),
                ],
                volumes=[
                    client.V1Volume(
                        name="dev",
                        host_path=client.V1HostPathVolumeSource(path="/dev"),
                    ),
                ],
            ),
        )

        with console.status(f"Running fsck on {device_path}"):
            res = self.k8s.create_pod(fsck_pod, namespace)

            if res.is_nok():
                console.failure(f"Failed to create fsck pod for {device_path}", details=str(res.message))
                return

            completed = self.k8s.wait_pod_complete(fsck_pod_name, namespace)
            logs = self.k8s.get_pod_logs(fsck_pod_name, namespace)

        if logs:
            console.success(f"fsck output for {device_path}:\n{logs}")

        if completed:
            console.success(f"fsck completed on {device_path}")
        else:
            console.failure(f"fsck failed on {device_path}")

        self.k8s.delete_pod(fsck_pod_name, namespace)
