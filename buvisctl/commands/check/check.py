from adapters import cfg, console


class CommandCheck:

    def __init__(self):
        self.check_failed = False

    def execute(self):
        if cfg.cluster_name:
            console.success("Cluster name")
        else:
            console.failure("Cluster name couldn't be determined")
            self.check_failed = True

        if cfg.path_terraform_workspace:
            console.success("Terraform workspace")
        else:
            console.failure(
                f"Missing terraform_workspace in {cfg.path_config_file}")
            self.check_failed = True

        if cfg.path_kubeconfig_dir:
            console.success("Kubeconfig dir")
        else:
            console.failure(
                f"Missing kubeconfig_dir in {cfg.path_config_file}")
            self.check_failed = True

        if cfg.nodes:
            nodes_ok = True

            for node in cfg.nodes:

                if node.name == "" or node.name is None:
                    console.failure(
                        f"Missing node name in {cfg.path_config_file}")
                    nodes_ok = False

                if node.ip == "" or node.ip is None:
                    console.failure(
                        f"Missing node ip in {cfg.path_config_file}")
                    nodes_ok = False

                if node.role == "" or node.role is None:
                    console.failure(
                        f"Missing node role in {cfg.path_config_file}")
                    nodes_ok = False

            if nodes_ok:
                console.success("Nodes")
            else:
                self.check_failed = True
        else:
            console.failure(f"Missing nodes in {cfg.path_config_file}")
            self.check_failed = True

        if cfg.ip_master:
            console.success("IP master")
        else:
            console.failure(
                f"Missing controlplane node in {cfg.path_config_file}")
            self.check_failed = True

        if cfg.flux:
            flux_ok = True

            if (cfg.flux.sops_key_fingerprint == ""
                    or cfg.flux.sops_key_fingerprint is None):
                console.failure(
                    f"Missing SOPS key fingerprint in {cfg.path_config_file}")
                flux_ok = False

            if cfg.flux.url_slack_webhook == "" or cfg.flux.url_slack_webhook is None:
                console.failure(
                    f"Missing Slack webhook URL in {cfg.path_config_file}")
                flux_ok = False

            if (cfg.flux.path_cluster_config == ""
                    or cfg.flux.path_cluster_config is None):
                console.failure(
                    f"Missing custer config path in {cfg.path_config_file}")
                flux_ok = False

            if cfg.flux.path_manifests_dir == "" or cfg.flux.path_manifests_dir is None:
                console.failure(
                    f"Missing manifests directory in {cfg.path_config_file}")
                flux_ok = False

            if cfg.flux.repository_owner == "" or cfg.flux.repository_owner is None:
                console.failure(
                    f"Missing repository owner in {cfg.path_config_file}")
                flux_ok = False

            if cfg.flux.repository_name == "" or cfg.flux.repository_name is None:
                console.failure(
                    f"Missing repository name in {cfg.path_config_file}")
                flux_ok = False

            if cfg.flux.repository_branch == "" or cfg.flux.repository_branch is None:
                console.failure(
                    f"Missing repository branch in {cfg.path_config_file}")
                flux_ok = False

            if flux_ok:
                console.success("Flux section")
            else:
                self.check_failed = True

        else:
            console.failure(
                f"Missing Flux section in {cfg.path_config_file}")
            self.check_failed = True

        if cfg.talos:
            talos_ok = True

            if (cfg.talos.dir_generated_configuration == ""
                    or cfg.talos.dir_generated_configuration is None):
                console.failure(
                    f"Missing Talos directory for generated configuration files in {cfg.path_config_file}"
                )
                talos_ok = False

            if cfg.talos.path_patch_all == "" or cfg.talos.path_patch_all is None:
                console.failure(
                    f"Missing Talos configuration patch for all nodes in {cfg.path_config_file}"
                )
                talos_ok = False

            if (cfg.talos.path_patch_controlplane == ""
                    or cfg.talos.path_patch_controlplane is None):
                console.failure(
                    f"Missing Talos configuration patch for controlplane nodes in {cfg.path_config_file}"
                )
                talos_ok = False

            if talos_ok:
                console.success("Talos section")
            else:
                self.check_failed = True
        else:
            console.failure(
                f"Missing Talos section in {cfg.path_config_file}")
            self.check_failed = True
