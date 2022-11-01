provider "proxmox" {
  pm_parallel     = 1
  pm_tls_insecure = true
  pm_api_url      = var.pm_api_url
  pm_user         = var.pm_user
  pm_timeout = 600
  pm_log_enable = true
  pm_debug = true
  pm_log_levels = {
    _default = "debug"
    _capturelog = ""
  }
}

provider "sops" {}
