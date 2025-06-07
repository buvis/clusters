provider "proxmox" {
  alias    = "feynman"
  endpoint = local.nodes.feynman.api_url
  username = local.credentials.pm_username
  password = local.credentials.pm_password
  insecure = true
  ssh {
    agent    = true
    username = "root"
  }
}

module "feynman_node" {
  source = "./modules/proxmox_node"
  providers = {
    proxmox.node = proxmox.feynman
  }
  node_name          = "feynman"
  node_config        = local.nodes["feynman"]
  talos_schematic_id = var.talos_schematic_id
  talos_version      = var.talos_version
}
