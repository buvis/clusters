provider "proxmox" {
  alias    = "higgs"
  endpoint = local.nodes.higgs.api_url
  username = local.credentials.pm_username
  password = local.credentials.pm_password
  insecure = true
  ssh {
    agent    = true
    username = "root"
  }
}

module "higgs_node" {
  source = "./modules/proxmox_node"
  providers = {
    proxmox.node = proxmox.higgs
  }
  node_name          = "higgs"
  node_config        = local.nodes["higgs"]
  talos_schematic_id = var.talos_schematic_id
  talos_version      = var.talos_version
}
