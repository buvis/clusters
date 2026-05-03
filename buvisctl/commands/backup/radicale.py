import base64
import contextlib
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from adapters import KubernetesAdapter, console

RADICALE_APP = "radicale"
RADICALE_PORT = 5232
RADICALE_USERS_SECRET = "radicale-users"
RADICALE_USERS_SECRET_KEY = "users"
COLLECTIONS_ROOT = "/data/collections/collection-root"
PORT_FORWARD_TIMEOUT = 15

MIME_TO_EXT = {
    "text/calendar": ".ics",
    "text/vcard": ".vcf",
}


class CommandBackupRadicale:

    def __init__(self):
        self.k8s = KubernetesAdapter()

    def execute(self, namespace, raw):
        pod_name = self._find_radicale_pod(namespace)
        collections = self._list_collections(pod_name, namespace)

        if not collections:
            console.panic(
                f"No Radicale collections found under {COLLECTIONS_ROOT} "
                f"in pod {pod_name}",
            )

        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        cwd = Path.cwd()

        if raw:
            for user, collection in collections:
                archive_name = (
                    f"radicale-{user}-{collection}-{timestamp}.tar.gz"
                )
                self._dump_raw_collection(
                    pod_name, namespace, user, collection, cwd / archive_name,
                )
                console.success(
                    f"Backed up {user}/{collection} to {archive_name}",
                )
            return

        creds = self._load_credentials(namespace)

        with self._port_forward_pod(pod_name, namespace) as local_port:
            for user, collection in collections:
                self._download_collection(
                    local_port, creds, user, collection, cwd, timestamp,
                )

    def _find_radicale_pod(self, namespace):
        pods = self.k8s.api.list_namespaced_pod(
            namespace=namespace,
            label_selector=(
                f"app.kubernetes.io/name={RADICALE_APP},"
                f"app.kubernetes.io/instance={RADICALE_APP}"
            ),
        )
        running = [p for p in pods.items if p.status.phase == "Running"]

        if not running:
            console.panic(
                f"No running Radicale pod found in namespace {namespace}",
            )

        return running[0].metadata.name

    def _list_collections(self, pod_name, namespace):
        cmd = [
            "kubectl", "exec",
            "-n", namespace,
            pod_name,
            "--",
            "find", COLLECTIONS_ROOT,
            "-mindepth", "2", "-maxdepth", "2", "-type", "d",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            console.panic(
                f"Failed to list collections in pod {pod_name}",
                details=result.stderr,
            )

        collections = []
        for raw_line in result.stdout.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            relative = Path(line).relative_to(COLLECTIONS_ROOT)
            parts = relative.parts
            if len(parts) != 2:
                continue
            user, collection = parts
            collections.append((user, collection))

        return collections

    def _dump_raw_collection(self, pod_name, namespace, user, collection,
                             archive_path):
        cmd = [
            "kubectl", "exec",
            "-n", namespace,
            pod_name,
            "--",
            "tar", "-czf", "-",
            "-C", f"{COLLECTIONS_ROOT}/{user}",
            collection,
        ]

        with archive_path.open("wb") as out:
            result = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE)

        if result.returncode != 0:
            archive_path.unlink(missing_ok=True)
            console.panic(
                f"Failed to archive {user}/{collection}",
                details=result.stderr.decode(errors="replace"),
            )

    def _load_credentials(self, namespace):
        data = self.k8s.get_secret_data(RADICALE_USERS_SECRET, namespace)

        if data is None:
            console.panic(
                f"Secret {RADICALE_USERS_SECRET} not found in {namespace}",
            )

        encoded = data.get(RADICALE_USERS_SECRET_KEY)

        if not encoded:
            console.panic(
                f"Secret {RADICALE_USERS_SECRET} has no "
                f"'{RADICALE_USERS_SECRET_KEY}' key",
            )

        try:
            htpasswd = base64.b64decode(encoded).decode()
        except (ValueError, UnicodeDecodeError) as e:
            console.panic(
                f"Failed to decode {RADICALE_USERS_SECRET} contents",
                details=str(e),
            )

        creds = {}
        for raw_line in htpasswd.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            user, _, password = line.partition(":")
            creds[user] = password

        if not creds:
            console.panic(
                f"No usable credentials in secret {RADICALE_USERS_SECRET}. "
                "Radicale must be configured with htpasswd_encryption = plain.",
            )

        return creds

    @contextlib.contextmanager
    def _port_forward_pod(self, pod_name, namespace):
        cmd = [
            "kubectl", "port-forward",
            "-n", namespace,
            f"pod/{pod_name}",
            f":{RADICALE_PORT}",
        ]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        try:
            local_port = self._wait_for_port_forward(proc)
            yield local_port
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

    def _wait_for_port_forward(self, proc):
        deadline = time.monotonic() + PORT_FORWARD_TIMEOUT
        pattern = re.compile(r"127\.0\.0\.1:(\d+)")
        captured = []

        while time.monotonic() < deadline:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            captured.append(line)
            match = pattern.search(line)
            if match:
                return int(match.group(1))

        proc.terminate()
        console.panic(
            "Timed out waiting for `kubectl port-forward` to be ready",
            details="".join(captured) or "no output",
        )

    def _download_collection(self, local_port, creds, user, collection, cwd,
                             timestamp):
        if user not in creds:
            console.panic(
                f"No credentials for Radicale user '{user}' in secret "
                f"{RADICALE_USERS_SECRET}",
            )

        password = creds[user]
        path = (
            f"/{urllib.parse.quote(user, safe='')}"
            f"/{urllib.parse.quote(collection, safe='')}/"
        )
        url = f"http://127.0.0.1:{local_port}{path}"
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        request = urllib.request.Request(
            url, headers={"Authorization": f"Basic {token}"},
        )

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                content_type = response.headers.get(
                    "Content-Type", "",
                ).split(";")[0].strip().lower()
                body = response.read()
        except urllib.error.HTTPError as e:
            console.panic(
                f"Radicale GET {path} failed: HTTP {e.code}",
                details=e.read().decode(errors="replace"),
            )
        except urllib.error.URLError as e:
            console.panic(
                f"Radicale GET {path} failed",
                details=str(e.reason),
            )

        ext = MIME_TO_EXT.get(content_type)

        if ext is None:
            console.panic(
                f"Unexpected Content-Type '{content_type}' for "
                f"{user}/{collection}",
            )

        archive_name = f"radicale-{user}-{collection}-{timestamp}{ext}"
        archive_path = cwd / archive_name
        archive_path.write_bytes(body)
        console.success(f"Downloaded {user}/{collection} to {archive_name}")
