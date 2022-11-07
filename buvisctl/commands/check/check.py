from adapters import cfg, console


class CommandCheck:

    def __init__(self):
        self.check_failed = False

    def execute(self):
        if _is_missing(cfg.cluster_name):
            console.failure("Cluster name couldn't be determined")
            self.check_failed = True
        else:
            console.success("Cluster name")

        if _is_missing(cfg.path_terraform_workspace):
            console.failure(
                f"Missing terraform_workspace in {cfg.path_config_file}")
            self.check_failed = True
        else:
            console.success("Terraform workspace")

        if _is_missing(cfg.path_kubeconfig_dir):
            console.failure(
                f"Missing kubeconfig_dir in {cfg.path_config_file}")
            self.check_failed = True
        else:
            console.success("Kubeconfig directory")

        if _is_missing(cfg.path_backup_manifests_dir):
            console.failure(
                f"Missing backup_manifests_dir in {cfg.path_config_file}")
            self.check_failed = True
        else:
            console.success("Backup jobs directory")

        if cfg.nodes:
            is_nodes_section_ok = True

            for node in cfg.nodes:

                if _is_missing(node.name):
                    console.failure(
                        f"Missing node name in {cfg.path_config_file}")
                    is_nodes_section_ok = False

                if _is_missing(node.ip):
                    console.failure(
                        f"Missing node ip in {cfg.path_config_file}")
                    is_nodes_section_ok = False

                if _is_missing(node.role):
                    console.failure(
                        f"Missing node role in {cfg.path_config_file}")
                    is_nodes_section_ok = False

            if is_nodes_section_ok:
                console.success("Nodes")
            else:
                self.check_failed = True
        else:
            console.failure(f"Missing nodes in {cfg.path_config_file}")
            self.check_failed = True

        if _is_missing(cfg.ip_master):
            console.failure(
                f"Missing controlplane node in {cfg.path_config_file}")
            self.check_failed = True
        else:
            console.success("IP master")

        if cfg.flux:
            is_flux_section_ok = True

            if _is_missing(cfg.flux.sops_key_fingerprint):
                console.failure(
                    f"Missing SOPS key fingerprint in {cfg.path_config_file}")
                is_flux_section_ok = False

            if _is_missing(cfg.flux.url_slack_webhook):
                console.failure(
                    f"Missing Slack webhook URL in {cfg.path_config_file}")
                is_flux_section_ok = False

            if _is_missing(cfg.flux.path_cluster_config):
                console.failure(
                    f"Missing custer config path in {cfg.path_config_file}")
                is_flux_section_ok = False

            if _is_missing(cfg.flux.path_manifests_dir):
                console.failure(
                    f"Missing manifests directory in {cfg.path_config_file}")
                is_flux_section_ok = False

            if _is_missing(cfg.flux.repository_owner):
                console.failure(
                    f"Missing repository owner in {cfg.path_config_file}")
                is_flux_section_ok = False

            if _is_missing(cfg.flux.repository_name):
                console.failure(
                    f"Missing repository name in {cfg.path_config_file}")
                is_flux_section_ok = False

            if _is_missing(cfg.flux.repository_branch):
                console.failure(
                    f"Missing repository branch in {cfg.path_config_file}")
                is_flux_section_ok = False

            if is_flux_section_ok:
                console.success("Flux section")
            else:
                self.check_failed = True
        else:
            console.failure(f"Missing Flux section in {cfg.path_config_file}")
            self.check_failed = True

        if cfg.talos:
            is_talos_section_ok = True

            if _is_missing(cfg.talos.dir_generated_configuration):
                console.failure(
                    f"Missing Talos directory for generated configuration "
                    f"files in {cfg.path_config_file}")
                is_talos_section_ok = False

            if _is_missing(cfg.talos.path_patch_all):
                console.failure(
                    f"Missing Talos configuration patch for all nodes "
                    f"in {cfg.path_config_file}")
                is_talos_section_ok = False

            if _is_missing(cfg.talos.path_patch_controlplane):
                console.failure(
                    f"Missing Talos configuration patch for controlplane "
                    f"nodes in {cfg.path_config_file}")
                is_talos_section_ok = False

            if is_talos_section_ok:
                console.success("Talos section")
            else:
                self.check_failed = True
        else:
            console.failure(f"Missing Talos section in {cfg.path_config_file}")
            self.check_failed = True


def _is_missing(variable):
    return variable == "" or variable is None
