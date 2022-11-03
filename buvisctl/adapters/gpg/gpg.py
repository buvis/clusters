import subprocess


class GPGAdapter:

    def __init__(self):
        pass

    def export_secret_key(self, fingerprint):
        sops_key_export_cmd = [
            "gpg",
            "--export-secret-keys",
            "--armor",
            fingerprint,
        ]
        sops_key_export = subprocess.run(sops_key_export_cmd,
                                         capture_output=True)

        return sops_key_export.stdout.decode()
