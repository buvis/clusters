import socket
import time

from kubernetes.client.exceptions import ApiException


def wait_for_namespace(api, namespace, timeout=600):
    sleep_count = 0

    while True:
        try:
            namespace_status = api.read_namespace_status(namespace)

            if namespace_status.status.phase == "Active":
                return True
            else:
                sleep_count = sleep_count + 1

                if sleep_count > timeout / 5:
                    return False
        except ApiException:
            time.sleep(5)
            sleep_count = sleep_count + 1

            if sleep_count > timeout / 5:
                return False
