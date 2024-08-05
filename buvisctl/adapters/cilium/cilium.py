import subprocess

from adapters.response import AdapterResponse


class CiliumAdapter:
    def __init__(self):
        pass

    def wait_for_install(self):
        cmd = [
            "cilium",
            "status",
            "--wait",
            "--wait-duration",
            "15m",
        ]

        results = subprocess.run(cmd, capture_output=True)

        if results.returncode == 0:
            return AdapterResponse()
        else:
            return AdapterResponse(
                code=results.returncode, message=results.stderr.decode()
            )
