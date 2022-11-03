import base64
import time

from adapters.response import AdapterResponse

from kubernetes import client, config, utils
from kubernetes.client.exceptions import ApiException


class KubernetesAdapter:

    def __init__(self):
        config.load_kube_config()
        self.api = client.CoreV1Api()
        self.client = client.ApiClient()

    def is_namespace_active(self, name, timeout=600):
        sleep_count = 0

        while True:
            try:
                namespace_status = self.api.read_namespace_status(name)

                if namespace_status.status.phase == "Active":
                    return AdapterResponse()
                else:
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
            new_namespace = client.V1Namespace(metadata=client.V1ObjectMeta(
                name=name))
            try:
                self.api.create_namespace(new_namespace)

                return AdapterResponse()
            except ApiException as e:
                return AdapterResponse(code=1, message=e)

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
                self.api.create_namespaced_secret(namespace="flux-system",
                                                  body=new_secret)
            except ApiException as e:
                return AdapterResponse(code=1, message=e)

        return AdapterResponse()

    def encode_secret_data(self, data):
        if data:
            return base64.standard_b64encode(data.encode()).decode()
