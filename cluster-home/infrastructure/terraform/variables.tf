variable "talos_schematic_id" {
  description = "Talos schematic ID for custom image"
  type        = string
}

variable "talos_version" {
  description = "Talos version to deploy"
  type        = string
}

locals {
  config = yamldecode(file("config.yaml"))

  credentials = {
    pm_username = data.sops_file.secrets.data["pm_username"]
    pm_password = data.sops_file.secrets.data["pm_password"]
    vm_username = data.sops_file.secrets.data["vm_ua_username"]
    vm_password = data.sops_file.secrets.data["vm_ua_password"]
    ssh_keys    = [data.sops_file.secrets.data["vm_allowed_ssh_key"]]
  }

  nodes = {
    for node_name, node_config in local.config.nodes : node_name => merge(node_config, {
      credentials = local.credentials
    })
  }
}
