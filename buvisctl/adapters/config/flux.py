import os


class FluxConfig:

    def __init__(self, config_dict):
        self.sops_key_fingerprint = config_dict.get("sops_key_fingerprint", "")
        self.url_slack_webhook = config_dict.get("url_slack_webhook", "")

        if config_dict.get("repository"):
            self.path_cluster_config = config_dict["repository"].get(
                "path_cluster_config", "")

            current_dir = os.path.basename(os.getcwd())

            if self.path_cluster_config.startswith(current_dir):
                self.path_cluster_config = self.path_cluster_config[
                    len(current_dir) + 1:]
            self.path_manifests_dir = config_dict["repository"].get(
                "dir_manifests", "")
            self.repository_owner = config_dict["repository"].get("owner", "")
            self.repository_name = config_dict["repository"].get("name", "")
            self.repository_branch = config_dict["repository"].get(
                "branch", "")
